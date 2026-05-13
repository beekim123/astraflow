import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.ai.providers.base import AiProvider
from app.ai.providers.mock import MockProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings
from app.core.logging import configure_logging, log_service_event
from app.services.internal_auth import verify_internal_token

configure_logging()
logger = logging.getLogger("astraflow.llm_provider")

app = FastAPI(title="AstraFlow LLM Provider", version="0.1.0")


class LlmGatewayRequest(BaseModel):
    provider: str = "mock"
    prompt: str
    request: AgentRequest


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name, "app": settings.app_name}


@app.post("/v1/llm/run", dependencies=[Depends(verify_internal_token)])
async def run_llm_endpoint(payload: LlmGatewayRequest) -> dict:
    # 1. 根据 provider 选择具体模型适配器
    # 2. 执行一次性模型调用
    # 3. 记录模型工具服务日志并返回 AgentResult
    started = perf_counter()
    provider = _provider_for(payload.provider)
    result = await provider.run(payload.request, payload.prompt)
    _log_llm_finished(payload, result.provider, result.model, result.status, started)
    return result.model_dump(mode="json")


@app.post("/v1/llm/stream", dependencies=[Depends(verify_internal_token)])
async def stream_llm_endpoint(payload: LlmGatewayRequest) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        # 1. 根据 provider 选择具体模型适配器
        # 2. 把 Provider chunk 转成统一 SSE 事件
        # 3. 收尾时补内部 _result 并写服务日志
        started = perf_counter()
        answer_parts: list[str] = []
        reasoning_parts: list[str] = []
        model = payload.request.model or settings.effective_llm_model or "mock-assistant"
        status = "success"
        try:
            provider = _provider_for(payload.provider)
            async for chunk in provider.stream(payload.request, payload.prompt):
                if chunk.type == "answer_delta":
                    answer_parts.append(chunk.content)
                    yield _sse({"type": "answer_delta", "content": chunk.content, "data": chunk.data})
                elif chunk.type == "reasoning_delta":
                    reasoning_parts.append(chunk.content)
                    yield _sse({"type": "reasoning_delta", "content": chunk.content, "data": chunk.data})
            result = _build_stream_result(payload, model, "".join(answer_parts), "".join(reasoning_parts))
            yield _sse({"type": "_result", "result": result.model_dump(mode="json")})
        except Exception as exc:
            status = "failed"
            yield _sse({"type": "error", "content": f"LLM Gateway 调用失败：{exc.__class__.__name__}", "data": {}})
        finally:
            _log_llm_finished(payload, payload.provider, model, status, started)
            yield "event: close\ndata: {}\n\n"

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)


def _provider_for(provider_name: str) -> AiProvider:
    if provider_name == "mock":
        return MockProvider()
    if provider_name in {"openai-compatible", "openai_compatible", "llm"}:
        return OpenAICompatibleProvider()
    raise ValueError(f"unsupported provider: {provider_name}")


def _build_stream_result(payload: LlmGatewayRequest, model: str, summary: str, reasoning: str) -> AgentResult:
    return AgentResult(
        task_type=payload.request.task_type,
        status="success",
        summary=summary,
        provider=payload.provider,
        model=model,
        mode=payload.request.mode,
        prompt_version=payload.request.payload.get("prompt_version", "v1"),
        input_tokens=max(1, len(payload.prompt) // 4),
        output_tokens=max(1, len(summary) // 4),
        estimated_cost=0,
        reasoning_summary=reasoning,
        process_steps=[
            f"LLM Provider 选择 Provider：{payload.provider}",
            f"调用模型：{model}",
        ],
        data={"content": summary, "tool_logs": [{"name": payload.provider, "status": "success"}]},
    )


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _log_llm_finished(payload: LlmGatewayRequest, provider: str, model: str, status: str, started: float) -> None:
    log_service_event(
        logger,
        "llm_request_finished",
        request_id=payload.request.request_id or "-",
        provider=provider,
        model=model,
        latency_ms=int((perf_counter() - started) * 1000),
        status=status,
    )
