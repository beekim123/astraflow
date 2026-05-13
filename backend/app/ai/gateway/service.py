import asyncio
from collections.abc import AsyncIterator
from time import perf_counter
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.ai.logging.service import build_model_call_log
from app.ai.prompt_hub.service import render_prompt
from app.ai.providers.base import AiProvider
from app.ai.providers.mcp_llm_gateway import McpLlmGatewayProvider
from app.ai.retrieval.noop import NoopRetriever
from app.ai.retrieval.schemas import Evidence, RetrievalQuery
from app.ai.routing.service import RouteDecision, choose_route_candidates, mark_route_failure, mark_route_success
from app.ai.safety.service import check_text
from app.core.config import settings

PROVIDER_TIMEOUT_SECONDS = 120


async def run_agent(session: AsyncSession, request: AgentRequest) -> AgentResult:
    # 非流式调用复用 stream_agent，消费所有事件后只返回最终 AgentResult。
    result: AgentResult | None = None
    async for event in stream_agent(session, request):
        if event["type"] == "_result":
            result = event["result"]
    if result is None:
        raise RuntimeError("agent did not produce a result")
    return result


async def stream_agent(session: AsyncSession, request: AgentRequest) -> AsyncIterator[dict]:
    # 主流程只保留执行顺序，细节拆到私有函数：
    # 1. 内容安全检查
    # 2. 加载模型路由
    # 3. 渲染 Prompt
    # 4. 预留 RAG 检索
    # 5. 调用候选模型并流式输出
    request_id = request.request_id or str(uuid4())
    started = perf_counter()
    text = _request_text(request)

    # 1. 内容安全检查：不通过就直接返回失败结果，不调用模型。
    yield _status("内容安全检查中")
    if safety_result := await _check_safety(session, request, request_id, started, text):
        yield _error(safety_result.summary)
        yield _agent_result(safety_result)
        return

    # 2. 加载模型路由：根据前端选择的 mode 找到可用候选模型。
    candidates = await _load_route_candidates(session, request)
    if not candidates:
        message = f"当前模式 {request.mode} 没有可用模型，请在模型路由中配置真实候选模型。"
        result = _record_early_failure(session, request, request_id, started, message)
        yield _error(result.summary)
        yield _agent_result(result)
        return

    # 3. 渲染 Prompt：把用户输入和任务类型填入 Prompt 模板。
    prompt, prompt_version = await _render_prompt_for_request(session, request, text, candidates[0])

    # 4. 预留 RAG 检索：当前 NoopRetriever 不查真实知识库，第三阶段会替换。
    yield _status("知识库检索中")
    evidence, retrieval_latency_ms, prompt = await _prepare_retrieval_context(request, text, prompt)
    yield {"type": "evidence", "data": {"items": evidence, "latency_ms": retrieval_latency_ms}}

    # 5. 调用候选模型：成功则返回最终 AgentResult，失败则按配置尝试 fallback。
    async for event in _stream_route_candidates(session, request, request_id, started, candidates, prompt, prompt_version, evidence):
        yield event


def _request_text(request: AgentRequest) -> str:
    # 统一从 payload 里取用户输入文本。不同业务可以传 content 或 text，这里做兼容。
    return str(request.payload.get("content") or request.payload.get("text") or "")


async def _check_safety(
    session: AsyncSession,
    request: AgentRequest,
    request_id: str,
    started: float,
    text: str,
) -> AgentResult | None:
    safety = await check_text(session, text)
    if safety.allowed:
        return None

    # 命中违禁词时不再调用模型，但仍返回失败 AgentResult，方便 chat service 统一落库。
    message = f"内容命中违禁词：{', '.join(safety.matched_words)}"
    return _record_early_failure(session, request, request_id, started, message)


def _record_early_failure(
    session: AsyncSession,
    request: AgentRequest,
    request_id: str,
    started: float,
    message: str,
) -> AgentResult:
    result = _failed_result(request, request_id, message, int((perf_counter() - started) * 1000))
    session.add(build_model_call_log(request, result, result.data["latency_ms"], request_id, message))
    return result


async def _load_route_candidates(session: AsyncSession, request: AgentRequest) -> list[RouteDecision]:
    # 一个 mode 可以配置多个候选模型，后面会按健康状态和优先级尝试 fallback。
    candidates = await choose_route_candidates(session, request.mode)
    return _filter_candidates(candidates, request.mode)


async def _render_prompt_for_request(
    session: AsyncSession,
    request: AgentRequest,
    text: str,
    primary_route: RouteDecision,
) -> tuple[str, str]:
    # render_prompt 会去 Prompt 模板表找当前场景的模板，然后把 content/mode/task_type 填进去。
    # Prompt 先按首选路由渲染；后续 fallback 模型复用同一份业务 Prompt。
    return await render_prompt(
        session,
        request.prompt_scene,
        {"content": text, "mode": primary_route.mode, "task_type": request.task_type},
    )


async def _prepare_retrieval_context(
    request: AgentRequest,
    text: str,
    prompt: str,
) -> tuple[list[dict], int, str]:
    # 第三阶段会把 NoopRetriever 替换成真实 RAG 检索器；当前先固定接口形状。
    retrieval = await NoopRetriever().search(
        RetrievalQuery(user_id=request.user_id, conversation_id=request.conversation_id, query=text)
    )
    evidence = [item.model_dump() for item in retrieval.evidence]
    return evidence, retrieval.latency_ms, _inject_evidence(prompt, retrieval.evidence)


async def _stream_route_candidates(
    session: AsyncSession,
    request: AgentRequest,
    request_id: str,
    started: float,
    candidates: list[RouteDecision],
    prompt: str,
    prompt_version: str,
    evidence: list[dict],
) -> AsyncIterator[dict]:
    route_chain: list[dict] = []
    errors: list[str] = []
    for index, route in enumerate(candidates):
        route_chain.append(_route_chain_item(route, "started"))
        routed_request = _build_routed_request(request, route, prompt_version)
        yield _status(
            f"调用模型：{route.display_name or route.model}",
            {"provider": route.provider, "model": route.model, "mode": route.mode},
        )

        answer_parts: list[str] = []
        reasoning_parts: list[str] = []
        candidate_started = perf_counter()
        try:
            async for event in _forward_provider_stream(route, routed_request, prompt, answer_parts, reasoning_parts):
                yield event

            result = await _finish_successful_route(
                session,
                request,
                routed_request,
                route,
                index,
                prompt,
                prompt_version,
                evidence,
                route_chain,
                errors,
                answer_parts,
                reasoning_parts,
                started,
                request_id,
            )
            yield _agent_result(result)
            return
        except Exception as exc:
            await _record_candidate_failure(
                session,
                request,
                routed_request,
                route,
                index,
                prompt_version,
                route_chain,
                errors,
                candidate_started,
                request_id,
                exc,
            )
            next_route = candidates[index + 1] if index + 1 < len(candidates) else None
            if next_route and route.fallback_enabled:
                yield _status(
                    f"{route.display_name or route.model} 不可用，尝试切换到 {next_route.display_name or next_route.model}",
                    {"severity": "warning", "from_model": route.model, "to_model": next_route.model},
                )
                continue
            break

    message = "当前模型服务不可用，请切换其他模型或稍后重试。"
    # 所有候选都失败时，仍返回一个失败 AgentResult，让 chat service 可以统一保存失败消息。
    result = _failed_result(request, request_id, message, int((perf_counter() - started) * 1000), route_chain)
    yield _error(message, {"errors": errors, "route_chain": route_chain})
    yield _agent_result(result)


def _build_routed_request(request: AgentRequest, route: RouteDecision, prompt_version: str) -> AgentRequest:
    # 把当前候选模型的 model/temperature/max_tokens 填回请求对象，让 Provider 不需要查数据库。
    return request.model_copy(
        update={
            "mode": route.mode,
            "model": route.model,
            "temperature": route.temperature,
            "max_tokens": route.max_tokens,
            "payload": {**request.payload, "prompt_version": prompt_version},
        }
    )


async def _forward_provider_stream(
    route: RouteDecision,
    routed_request: AgentRequest,
    prompt: str,
    answer_parts: list[str],
    reasoning_parts: list[str],
) -> AsyncIterator[dict]:
    provider = _provider_for(route.provider)
    async with asyncio.timeout(PROVIDER_TIMEOUT_SECONDS):
        async for chunk in provider.stream(routed_request, prompt):
            if chunk.type == "answer_delta":
                answer_parts.append(chunk.content)
                yield {"type": "answer_delta", "content": chunk.content, "data": chunk.data}
            elif chunk.type == "reasoning_delta":
                reasoning_parts.append(chunk.content)
                yield {"type": "reasoning_delta", "content": chunk.content, "data": chunk.data}


async def _finish_successful_route(
    session: AsyncSession,
    request: AgentRequest,
    routed_request: AgentRequest,
    route: RouteDecision,
    index: int,
    prompt: str,
    prompt_version: str,
    evidence: list[dict],
    route_chain: list[dict],
    errors: list[str],
    answer_parts: list[str],
    reasoning_parts: list[str],
    started: float,
    request_id: str,
) -> AgentResult:
    summary = "".join(answer_parts)
    reasoning = "".join(reasoning_parts)
    if not summary:
        raise RuntimeError("model returned empty content")

    route_chain[-1] = _route_chain_item(route, "success")
    await mark_route_success(session, route)
    latency_ms = int((perf_counter() - started) * 1000)
    result = _success_result(request, route, index, prompt, prompt_version, evidence, route_chain, summary, reasoning, latency_ms)
    session.add(build_model_call_log(routed_request, result, latency_ms, request_id, "; ".join(errors)))
    return result


async def _record_candidate_failure(
    session: AsyncSession,
    request: AgentRequest,
    routed_request: AgentRequest,
    route: RouteDecision,
    index: int,
    prompt_version: str,
    route_chain: list[dict],
    errors: list[str],
    candidate_started: float,
    request_id: str,
    exc: Exception,
) -> None:
    error_message = f"{route.display_name or route.model} 调用失败：{exc.__class__.__name__}"
    errors.append(error_message)
    route_chain[-1] = _route_chain_item(route, "failed", str(exc))
    await mark_route_failure(session, route, str(exc))
    latency_ms = int((perf_counter() - candidate_started) * 1000)
    failed_result = AgentResult(
        task_type=request.task_type,
        status="failed",
        summary=error_message,
        provider=route.provider,
        model=route.model,
        mode=route.mode,
        prompt_version=prompt_version,
        fallback_used=index > 0,
        route_chain=route_chain,
        data={"route_chain": route_chain, "latency_ms": latency_ms},
    )
    session.add(build_model_call_log(routed_request, failed_result, latency_ms, request_id, str(exc)))


def _success_result(
    request: AgentRequest,
    route: RouteDecision,
    index: int,
    prompt: str,
    prompt_version: str,
    evidence: list[dict],
    route_chain: list[dict],
    summary: str,
    reasoning: str,
    latency_ms: int,
) -> AgentResult:
    return AgentResult(
        task_type=request.task_type,
        status="success",
        summary=summary,
        provider=route.provider,
        model=route.model,
        mode=route.mode,
        prompt_version=prompt_version,
        input_tokens=max(1, len(prompt) // 4),
        output_tokens=max(1, len(summary) // 4),
        estimated_cost=0,
        fallback_used=index > 0,
        reasoning_summary=reasoning,
        process_steps=[
            "内容安全检查通过",
            f"模型路由：{route.mode} -> {route.provider}/{route.model}",
            f"Prompt 场景：{request.prompt_scene}@{prompt_version}",
            f"RAG 检索：NoopRetriever，命中 {len(evidence)} 条证据",
            "真实流式调用完成",
        ],
        evidence=evidence,
        route_chain=route_chain,
        data={
            "content": summary,
            "artifacts": _build_artifacts(request.task_type, summary, route.provider),
            "tool_logs": [{"name": route.provider, "status": "success"}],
            "evidence": evidence,
            "route_chain": route_chain,
            "latency_ms": latency_ms,
        },
    )


def _agent_result(result: AgentResult) -> dict:
    # _result 是内部事件，告诉 chat service：最终结果已经准备好，可以落库了。
    return {"type": "_result", "result": result}


def _provider_for(provider_name: str) -> AiProvider:
    # provider 字段来自模型路由表；AI Gateway 不直接调具体模型，统一转发到 MCP LLM Gateway。
    return McpLlmGatewayProvider(provider_name)


def _filter_candidates(candidates: list[RouteDecision], mode: str) -> list[RouteDecision]:
    # 生产环境默认过滤 mock，避免用户以为用了真实模型但实际走了假回复。
    if settings.app_env == "local" or mode == "mock":
        return candidates
    return [item for item in candidates if item.provider != "mock"]


def _inject_evidence(prompt: str, evidence: list[Evidence]) -> str:
    # RAG 命中证据后，把证据拼进 Prompt，让模型基于知识库回答。
    if not evidence:
        return prompt
    lines = ["", "以下是可参考的知识库证据，请优先基于证据回答，并保留引用："]
    for index, item in enumerate(evidence, start=1):
        lines.append(f"[{index}] {item.title}\n{item.snippet}")
    return f"{prompt}\n{chr(10).join(lines)}"


def _build_artifacts(task_type: str, content: str, provider: str) -> list[dict]:
    if task_type == "chat-general":
        return []
    return [
        {
            "artifact_type": "report",
            "title": "AI 生成结果",
            "content_markdown": content,
            "content_json": {"source": provider, "task_type": task_type},
        }
    ]


def _status(content: str, data: dict | None = None) -> dict:
    return {"type": "status", "content": content, "data": data or {}}


def _error(content: str, data: dict | None = None) -> dict:
    return {"type": "error", "content": content, "data": data or {}}


def _route_chain_item(route: RouteDecision, status: str, error: str = "") -> dict:
    return {
        "mode": route.mode,
        "display_name": route.display_name,
        "provider": route.provider,
        "model": route.model,
        "status": status,
        "error": error[:500],
    }


def _failed_result(
    request: AgentRequest,
    request_id: str,
    message: str,
    latency_ms: int,
    route_chain: list[dict] | None = None,
) -> AgentResult:
    return AgentResult(
        task_type=request.task_type,
        status="failed",
        summary=message,
        provider="",
        model="",
        mode=request.mode,
        prompt_version="",
        fallback_used=False,
        route_chain=route_chain or [],
        data={"request_id": request_id, "latency_ms": latency_ms, "route_chain": route_chain or []},
    )
