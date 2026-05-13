from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.responses import success
from app.common.identity.models import User

router = APIRouter(prefix="/api/placeholders", tags=["placeholders"])


def placeholder(name: str, stage: str) -> dict:
    return {
        "name": name,
        "stage": stage,
        "status": "placeholder",
        "message": "第一阶段占位，后续阶段实现真实业务能力。",
    }


@router.get("/chat")
async def chat(_: User = Depends(get_current_user)):
    return success(placeholder("AI 对话", "阶段 2/3"))


@router.get("/audit")
async def audit(_: User = Depends(get_current_user)):
    return success(placeholder("智能审核", "阶段 4"))


@router.get("/ticket")
async def ticket(_: User = Depends(get_current_user)):
    return success(placeholder("AI 工单", "阶段 5"))


@router.get("/customer-h5")
async def customer_h5(_: User = Depends(get_current_user)):
    return success(placeholder("H5 客服/数字人组件", "阶段 6"))


@router.get("/marketing")
async def marketing(_: User = Depends(get_current_user)):
    return success(placeholder("内容营销助手", "阶段 6"))

