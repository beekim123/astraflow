from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.core.responses import error_response, success
from app.modules.security_gate.schemas import CaptchaVerifyRequest
from app.modules.security_gate.service import create_captcha, verify_captcha

router = APIRouter(prefix="/api/security", tags=["security-gate"])


def get_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/visitor-captcha")
async def visitor_captcha(request: Request):
    try:
        captcha_id, question = await create_captcha(get_ip(request))
    except ValueError as exc:
        return error_response(429, 40029, str(exc))
    return success({"captcha_id": captcha_id, "question": question})


@router.post("/visitor-captcha/verify")
async def visitor_captcha_verify(payload: CaptchaVerifyRequest, request: Request, response: Response):
    ok = await verify_captcha(get_ip(request), payload.captcha_id, payload.answer)
    if not ok:
        return error_response(400, 40022, "captcha invalid or expired")
    response.set_cookie(
        key="gate_passed",
        value="true",
        max_age=3600,
        httponly=True,
        secure=settings.gate_cookie_secure,
        samesite="lax",
    )
    return success({"gate_passed": True})


@router.get("/visitor-gate/status")
async def visitor_gate_status(request: Request):
    return success({"gate_passed": request.cookies.get("gate_passed") == "true"})

