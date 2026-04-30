import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import ErrorCode
from app.core.logging import configure_logging
from app.core.middleware import OperationLogMiddleware, RequestIDMiddleware
from app.core.responses import error_response, success
from app.modules.audit_log.router import router as audit_log_router
from app.modules.identity.router import admin_router as users_admin_router
from app.modules.identity.router import auth_router
from app.modules.placeholder.router import router as placeholder_router
from app.modules.rbac.router import admin_menus_router, menus_router, permissions_router, roles_router
from app.modules.security_gate.router import router as security_gate_router

# 入口文件的职责：
# 1. 创建 FastAPI 应用实例。
# 2. 注册全局中间件，例如请求 ID、操作日志、跨域。
# 3. 注册全局异常处理器，把异常统一转换成固定 JSON 结构。
# 4. 挂载各业务模块的 router，让接口真正生效。
configure_logging()
logger = logging.getLogger("astraflow.error")

# app 就是整个后端应用对象。uvicorn 启动时会加载 `app.main:app`。
app = FastAPI(title=settings.app_name, version="0.1.0")

# 中间件可以理解为“所有请求都会经过的公共管道”。
# 注意执行顺序和声明顺序有关：请求进入时通常后注册的先执行，响应返回时反过来。
app.add_middleware(OperationLogMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    # 业务里主动 raise 的 HTTPException 会走这里。
    # 项目约定：如果 detail 是 dict，就认为它已经带了业务错误码和中文提示。
    if isinstance(exc.detail, dict):
        return error_response(
            exc.status_code,
            exc.detail.get("code", ErrorCode.BAD_REQUEST),
            exc.detail.get("message", str(exc.detail)),
            exc.detail.get("data"),
        )
    # 兜底处理普通 HTTPException，避免前端看到 FastAPI 默认错误结构。
    return error_response(exc.status_code, ErrorCode.BAD_REQUEST, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    # 请求参数不符合 Pydantic schema 时会走这里，例如缺字段、类型不对、长度不合法。
    return error_response(422, ErrorCode.VALIDATION_ERROR, "参数校验失败", exc.errors())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # 未预期异常才走这里，说明后端代码或外部依赖出问题。
    # 这里要打 error 日志，但不能把 Python 堆栈、数据库错误等敏感信息直接返回给前端。
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": getattr(request.state, "request_id", "-"),
            "method": request.method,
            "path": request.url.path,
        },
    )
    return error_response(500, ErrorCode.SERVER_ERROR, "系统繁忙，请稍后再试")


@app.get("/api/health")
async def health():
    # 健康检查接口。部署、Docker、Nginx 或监控系统可以用它判断后端是否存活。
    return success({"status": "ok", "app": settings.app_name})


# 下面是路由挂载区。
# router 可以理解为一个模块的一组接口集合；include_router 后，这些接口才会加入 app。
app.include_router(security_gate_router)
app.include_router(auth_router)
app.include_router(menus_router)
app.include_router(users_admin_router)
app.include_router(roles_router)
app.include_router(admin_menus_router)
app.include_router(permissions_router)
app.include_router(audit_log_router)
app.include_router(placeholder_router)
