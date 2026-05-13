import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse

from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.ai.gateway.service import run_agent, stream_agent
from app.core.config import settings
from app.core.logging import configure_logging, log_service_event
from app.db.session import async_session_maker
from app.services.internal_auth import verify_internal_token

configure_logging()
logger = logging.getLogger("astraflow.ai_gateway")

app = FastAPI(title="AstraFlow AI Gateway", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name, "app": settings.app_name}


@app.post("/v1/agent/run", dependencies=[Depends(verify_internal_token)])
async def run_agent_endpoint(payload: AgentRequest) -> dict:
    # 1. 创建独立数据库会话
    # 2. 执行 AI 编排链路并提交模型调用日志
    # 3. 写服务日志并返回标准 AgentResult
    started = perf_counter()
    async with async_session_maker() as session:
        result = await run_agent(session, payload)
        await session.commit()
    _log_agent_finished(payload, result, started)
    return result.model_dump(mode="json")


@app.post("/v1/agent/stream", dependencies=[Depends(verify_internal_token)])
async def stream_agent_endpoint(payload: AgentRequest) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        # 1. 调用 AI 编排服务并逐段转发 SSE 事件
        # 2. 捕获内部 _result，提交模型调用日志事务
        # 3. 失败时回滚并返回前端可识别的 error 事件
        started = perf_counter()
        final_result: AgentResult | None = None
        async with async_session_maker() as session:
            try:
                async for event in stream_agent(session, payload):
                    if event["type"] == "_result":
                        final_result = event["result"]
                        await session.commit()
                        _log_agent_finished(payload, final_result, started)
                    yield _sse(_serialize_agent_event(event))
            except Exception as exc:
                await session.rollback()
                log_service_event(
                    logger,
                    "agent_request_finished",
                    request_id=payload.request_id or "-",
                    provider="-",
                    model=payload.model or "-",
                    latency_ms=int((perf_counter() - started) * 1000),
                    status="failed",
                    error=exc.__class__.__name__,
                )
                yield _sse({"type": "error", "content": "AI Gateway 调用失败，请稍后重试。", "data": {}})
        if final_result is None:
            yield _sse({"type": "error", "content": "AI Gateway 未返回结果。", "data": {}})
        yield "event: close\ndata: {}\n\n"

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)


def _serialize_agent_event(event: dict) -> dict:
    if event["type"] == "_result":
        return {"type": "_result", "result": event["result"].model_dump(mode="json")}
    return event


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _log_agent_finished(payload: AgentRequest, result: AgentResult, started: float) -> None:
    log_service_event(
        logger,
        "agent_request_finished",
        request_id=payload.request_id or "-",
        provider=result.provider,
        model=result.model,
        latency_ms=int((perf_counter() - started) * 1000),
        status=result.status,
    )
