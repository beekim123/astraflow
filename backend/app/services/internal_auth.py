from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    if not settings.ai_gateway_internal_token:
        return
    if x_internal_token != settings.ai_gateway_internal_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal token")
