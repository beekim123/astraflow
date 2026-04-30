from typing import Any

from fastapi.responses import JSONResponse

from app.core.errors import ErrorCode


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": ErrorCode.SUCCESS, "message": message, "data": data}


def error_response(status_code: int, code: int, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": data})

