import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import async_session_maker
from app.core.logging import log_service_event
from app.common.audit_log.models import OperationLog

logger = logging.getLogger("astraflow.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        started_at = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        cost_ms = round((time.perf_counter() - started_at) * 1000, 2)
        log_service_event(
            logger,
            "request_done",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=cost_ms,
        )
        return response


class OperationLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/api") and path not in {"/api/health"}:
            try:
                async with async_session_maker() as session:
                    user_id = getattr(request.state, "user_id", None)
                    log = OperationLog(
                        user_id=user_id,
                        request_id=getattr(request.state, "request_id", "-"),
                        module=(path.split("/")[2] if len(path.split("/")) > 2 else "api"),
                        action=request.method,
                        resource=path,
                        method=request.method,
                        path=path,
                        ip=request.client.host if request.client else "",
                        user_agent=request.headers.get("user-agent", ""),
                        status_code=response.status_code,
                    )
                    session.add(log)
                    await session.commit()
            except Exception as exc:
                logger.warning("operation_log_failed: %s", exc)
        return response
