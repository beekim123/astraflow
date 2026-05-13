import json
from collections.abc import AsyncIterator

import httpx

from app.ai.contracts.client import AgentClient
from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.core.config import settings


class HttpAgentClient(AgentClient):
    async def run(self, request: AgentRequest) -> AgentResult:
        # 1. 把业务侧 AgentRequest 序列化为 HTTP 请求
        # 2. 调用独立 ai-gateway 服务
        # 3. 把响应恢复成稳定的 AgentResult 契约
        async with httpx.AsyncClient(timeout=settings.ai_gateway_timeout_seconds) as client:
            response = await client.post(
                _agent_url("/v1/agent/run"),
                json=request.model_dump(mode="json"),
                headers=_headers(request),
            )
            response.raise_for_status()
        return AgentResult.model_validate(response.json())

    async def stream(self, request: AgentRequest) -> AsyncIterator[dict]:
        # 1. 向 ai-gateway 发起内部流式请求
        # 2. 解析 SSE data 块并保持事件形状
        # 3. 只把内部 _result 转回 AgentResult，其他事件原样透传给聊天服务
        timeout = httpx.Timeout(settings.ai_gateway_timeout_seconds, read=settings.ai_gateway_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                _agent_url("/v1/agent/stream"),
                json=request.model_dump(mode="json"),
                headers=_headers(request),
            ) as response:
                response.raise_for_status()
                async for event in _iter_sse_events(response):
                    if event.get("type") == "_result":
                        yield {"type": "_result", "result": AgentResult.model_validate(event["result"])}
                    else:
                        yield event


def _agent_url(path: str) -> str:
    return f"{settings.ai_gateway_url.rstrip('/')}{path}"


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
