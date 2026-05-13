import json
from collections.abc import AsyncIterator

import httpx

from app.ai.contracts.schemas import AgentRequest, AgentResult, AgentStreamChunk
from app.ai.providers.base import AiProvider
from app.core.config import settings


class McpLlmGatewayProvider(AiProvider):
    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    async def run(self, request: AgentRequest, prompt: str) -> AgentResult:
        answer_parts: list[str] = []
        reasoning_parts: list[str] = []
        final_result: AgentResult | None = None
        async for chunk in self.stream(request, prompt):
            if chunk.type == "answer_delta":
                answer_parts.append(chunk.content)
            elif chunk.type == "reasoning_delta":
                reasoning_parts.append(chunk.content)
            elif chunk.type == "provider_done":
                final_result = AgentResult.model_validate(chunk.data)
        if final_result is not None:
            return final_result
        return AgentResult(
            task_type=request.task_type,
            status="success",
            summary="".join(answer_parts),
            provider=self.provider_name,
            model=request.model,
            mode=request.mode,
            prompt_version=request.payload.get("prompt_version", "v1"),
            reasoning_summary="".join(reasoning_parts),
            data={"content": "".join(answer_parts)},
        )

    async def stream(self, request: AgentRequest, prompt: str) -> AsyncIterator[AgentStreamChunk]:
        # 1. 把 AI Gateway 已经选定的路由参数转发给 MCP LLM Gateway
        # 2. 把 MCP SSE 事件恢复成 Provider chunk
        # 3. 将 MCP error 事件转换成异常，交给 AI Gateway fallback 逻辑处理
        timeout = httpx.Timeout(settings.ai_gateway_timeout_seconds, read=settings.ai_gateway_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                _llm_url("/v1/llm/stream"),
                json={
                    "provider": self.provider_name,
                    "prompt": prompt,
                    "request": request.model_dump(mode="json"),
                },
                headers=_headers(request),
            ) as response:
                response.raise_for_status()
                async for event in _iter_sse_events(response):
                    event_type = event.get("type")
                    if event_type == "answer_delta":
                        yield AgentStreamChunk(
                            type="answer_delta",
                            content=str(event.get("content") or ""),
                            data=event.get("data") or {},
                        )
                    elif event_type == "reasoning_delta":
                        yield AgentStreamChunk(
                            type="reasoning_delta",
                            content=str(event.get("content") or ""),
                            data=event.get("data") or {},
                        )
                    elif event_type == "_result":
                        yield AgentStreamChunk(type="provider_done", data=event.get("result") or {})
                    elif event_type == "error":
                        raise RuntimeError(str(event.get("content") or "mcp llm gateway error"))


def _llm_url(path: str) -> str:
    return f"{settings.mcp_llm_gateway_url.rstrip('/')}{path}"


def _headers(request: AgentRequest) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": settings.ai_gateway_internal_token,
    }
    if request.request_id:
        headers["X-Request-ID"] = request.request_id
    return headers


async def _iter_sse_events(response: httpx.Response) -> AsyncIterator[dict]:
    buffer = ""
    async for line in response.aiter_lines():
        if line == "":
            if buffer.strip():
                event = _parse_sse_block(buffer)
                if event:
                    yield event
            buffer = ""
            continue
        buffer += f"{line}\n"
    if buffer.strip():
        event = _parse_sse_block(buffer)
        if event:
            yield event


def _parse_sse_block(block: str) -> dict | None:
    payload = "\n".join(line[6:] for line in block.splitlines() if line.startswith("data: "))
    if not payload:
        return None
    return json.loads(payload)
