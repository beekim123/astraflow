from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_permission
from app.core.responses import success
from app.db.session import get_session
from app.modules.ai_admin import service
from app.modules.ai_admin.schemas import (
    ForbiddenWordCreate,
    ForbiddenWordUpdate,
    ModelRouteRuleCreate,
    ModelRouteRuleUpdate,
    PromptTemplateCreate,
    PromptTemplateUpdate,
)
from app.modules.identity.models import User

router = APIRouter(prefix="/api/admin/ai", tags=["admin-ai"])


@router.get("/prompts")
async def list_prompts(
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_prompts(session, page, page_size, keyword))


@router.post("/prompts")
async def create_prompt(
    payload: PromptTemplateCreate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_prompt(session, payload)).model_dump())


@router.put("/prompts/{item_id}")
async def update_prompt(
    item_id: str,
    payload: PromptTemplateUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_prompt(session, item_id, payload)).model_dump())


@router.patch("/prompts/{item_id}/enabled")
async def set_prompt_enabled(
    item_id: str,
    payload: PromptTemplateUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_prompt(session, item_id, payload)).model_dump())


@router.get("/forbidden-words")
async def list_forbidden_words(
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_forbidden_words(session, page, page_size, keyword))


@router.post("/forbidden-words")
async def create_forbidden_word(
    payload: ForbiddenWordCreate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_forbidden_word(session, payload)).model_dump())


@router.put("/forbidden-words/{item_id}")
async def update_forbidden_word(
    item_id: str,
    payload: ForbiddenWordUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_forbidden_word(session, item_id, payload)).model_dump())


@router.patch("/forbidden-words/{item_id}/enabled")
async def set_forbidden_word_enabled(
    item_id: str,
    payload: ForbiddenWordUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_forbidden_word(session, item_id, payload)).model_dump())


@router.get("/model-routes")
async def list_model_routes(
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_model_routes(session, page, page_size, keyword))


@router.post("/model-routes")
async def create_model_route(
    payload: ModelRouteRuleCreate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_model_route(session, payload)).model_dump())


@router.put("/model-routes/{item_id}")
async def update_model_route(
    item_id: str,
    payload: ModelRouteRuleUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_model_route(session, item_id, payload)).model_dump())


@router.patch("/model-routes/{item_id}/enabled")
async def set_model_route_enabled(
    item_id: str,
    payload: ModelRouteRuleUpdate,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_model_route(session, item_id, payload)).model_dump())


@router.get("/model-call-logs")
async def list_model_call_logs(
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_model_call_logs(session, page, page_size, keyword))


@router.get("/model-call-logs/{item_id}")
async def get_model_call_log(
    item_id: str,
    _: User = Depends(require_permission("admin:ai")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.get_model_call_log(session, item_id)).model_dump())
