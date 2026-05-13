from typing import Any, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import not_found
from app.core.pagination import page_offset, page_payload
from app.common.ai_admin.models import ForbiddenWord, ModelCallLog, ModelRouteRule, PromptTemplate
from app.common.ai_admin.schemas import (
    ForbiddenWordCreate,
    ForbiddenWordOut,
    ForbiddenWordUpdate,
    ModelCallLogOut,
    ModelRouteRuleCreate,
    ModelRouteRuleOut,
    ModelRouteRuleUpdate,
    PromptTemplateCreate,
    PromptTemplateOut,
    PromptTemplateUpdate,
)

ModelT = TypeVar("ModelT", PromptTemplate, ForbiddenWord, ModelRouteRule)


def _out(item: Any, schema: type):
    return schema.model_validate(item)


async def _get_or_404(session: AsyncSession, model: type[ModelT], item_id: str, name: str) -> ModelT:
    item = await session.get(model, item_id)
    if item is None:
        raise not_found(f"{name} not found")
    return item


async def list_prompts(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    stmt = select(PromptTemplate).order_by(PromptTemplate.created_at.desc())
    total_stmt = select(func.count()).select_from(PromptTemplate)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(PromptTemplate.name.ilike(like), PromptTemplate.scene.ilike(like)))
        total_stmt = total_stmt.where(or_(PromptTemplate.name.ilike(like), PromptTemplate.scene.ilike(like)))
    total = await session.scalar(total_stmt)
    result = await session.execute(stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [_out(item, PromptTemplateOut).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_prompt(session: AsyncSession, payload: PromptTemplateCreate) -> PromptTemplateOut:
    item = PromptTemplate(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _out(item, PromptTemplateOut)


async def update_prompt(session: AsyncSession, item_id: str, payload: PromptTemplateUpdate) -> PromptTemplateOut:
    item = await _get_or_404(session, PromptTemplate, item_id, "prompt")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return _out(item, PromptTemplateOut)


async def list_forbidden_words(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    stmt = select(ForbiddenWord).order_by(ForbiddenWord.created_at.desc())
    total_stmt = select(func.count()).select_from(ForbiddenWord)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ForbiddenWord.word.ilike(like), ForbiddenWord.category.ilike(like)))
        total_stmt = total_stmt.where(or_(ForbiddenWord.word.ilike(like), ForbiddenWord.category.ilike(like)))
    total = await session.scalar(total_stmt)
    result = await session.execute(stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [_out(item, ForbiddenWordOut).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_forbidden_word(session: AsyncSession, payload: ForbiddenWordCreate) -> ForbiddenWordOut:
    item = ForbiddenWord(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _out(item, ForbiddenWordOut)


async def update_forbidden_word(session: AsyncSession, item_id: str, payload: ForbiddenWordUpdate) -> ForbiddenWordOut:
    item = await _get_or_404(session, ForbiddenWord, item_id, "forbidden word")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return _out(item, ForbiddenWordOut)


async def list_model_routes(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    stmt = select(ModelRouteRule).order_by(ModelRouteRule.mode, ModelRouteRule.created_at.desc())
    total_stmt = select(func.count()).select_from(ModelRouteRule)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ModelRouteRule.mode.ilike(like), ModelRouteRule.model.ilike(like)))
        total_stmt = total_stmt.where(or_(ModelRouteRule.mode.ilike(like), ModelRouteRule.model.ilike(like)))
    total = await session.scalar(total_stmt)
    result = await session.execute(stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [_out(item, ModelRouteRuleOut).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_model_route(session: AsyncSession, payload: ModelRouteRuleCreate) -> ModelRouteRuleOut:
    item = ModelRouteRule(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _out(item, ModelRouteRuleOut)


async def update_model_route(session: AsyncSession, item_id: str, payload: ModelRouteRuleUpdate) -> ModelRouteRuleOut:
    item = await _get_or_404(session, ModelRouteRule, item_id, "model route")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return _out(item, ModelRouteRuleOut)


async def list_model_call_logs(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    stmt = select(ModelCallLog).order_by(ModelCallLog.created_at.desc())
    total_stmt = select(func.count()).select_from(ModelCallLog)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ModelCallLog.request_id.ilike(like), ModelCallLog.model.ilike(like)))
        total_stmt = total_stmt.where(or_(ModelCallLog.request_id.ilike(like), ModelCallLog.model.ilike(like)))
    total = await session.scalar(total_stmt)
    result = await session.execute(stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [_out(item, ModelCallLogOut).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def get_model_call_log(session: AsyncSession, item_id: str) -> ModelCallLogOut:
    item = await _get_or_404(session, ModelCallLog, item_id, "model call log")
    return _out(item, ModelCallLogOut)
