from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_permission
from app.core.responses import success
from app.db.session import get_session
from app.modules.identity import service
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    UserCreate,
    UserUpdate,
)

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
admin_router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])


@auth_router.post("/login")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    return success((await service.login(session, payload.username, payload.password)).model_dump())


@auth_router.post("/refresh")
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    return success((await service.refresh(session, payload.refresh_token)).model_dump())


@auth_router.post("/logout")
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_session)):
    await service.logout(session, payload.refresh_token)
    return success(True)


@auth_router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return success(service.user_to_me(user).model_dump())


@admin_router.get("")
async def list_users(
    _: User = Depends(require_permission("admin:users")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_users(session, page, page_size, keyword))


@admin_router.post("")
async def create_user(
    payload: UserCreate,
    _: User = Depends(require_permission("admin:users")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_user(session, payload)).model_dump())


@admin_router.get("/{user_id}")
async def get_user(
    user_id: str,
    _: User = Depends(require_permission("admin:users")),
    session: AsyncSession = Depends(get_session),
):
    return success(service.user_to_out(await service.get_user_or_404(session, user_id)).model_dump())


@admin_router.put("/{user_id}")
async def update_user(
    user_id: str,
    payload: UserUpdate,
    _: User = Depends(require_permission("admin:users")),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.update_user(session, user_id, payload)).model_dump())


@admin_router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission("admin:users")),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_user(session, user_id, current_user)
    return success(True)
