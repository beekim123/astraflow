from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import business_error, forbidden, not_found, unauthorized
from app.core.pagination import page_offset, page_payload
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    utcnow,
    verify_password,
)
from app.modules.identity.models import RefreshToken, User
from app.modules.identity.repository import get_refresh_token, get_user_by_id, get_user_by_username
from app.modules.identity.schemas import MeOut, TokenResponse, UserCreate, UserOut, UserUpdate
from app.modules.audit_log.models import OperationLog
from app.modules.rbac.repository import get_roles_by_ids


def user_to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        status=user.status,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_ids=[role.id for role in user.roles],
        roles=[{"id": role.id, "code": role.code, "name": role.name} for role in user.roles],
    )


def user_to_me(user: User) -> MeOut:
    permissions: set[str] = set()
    roles = [role.code for role in user.roles]
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    if user.is_superuser:
        permissions.add("*")
    return MeOut(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        is_superuser=user.is_superuser,
        roles=roles,
        permissions=sorted(permissions),
    )


async def login(session: AsyncSession, username: str, password: str) -> TokenResponse:
    user = await get_user_by_username(session, username)
    if user is None or not verify_password(password, user.password_hash):
        raise unauthorized("invalid username or password")
    if user.status != "active":
        raise forbidden("user disabled")

    access_token = create_access_token(user.id)
    refresh_token, token_hash, expires_at = create_refresh_token()
    session.add(RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh(session: AsyncSession, raw_refresh_token: str) -> TokenResponse:
    token_hash = hash_refresh_token(raw_refresh_token)
    item = await get_refresh_token(session, token_hash)
    if item is None or item.revoked_at is not None or item.expires_at < utcnow():
        raise unauthorized("invalid refresh token")
    user = await get_user_by_id(session, item.user_id)
    if user is None:
        raise unauthorized("invalid refresh token")
    item.revoked_at = datetime.now(timezone.utc)
    new_refresh, new_hash, expires_at = create_refresh_token()
    session.add(RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=expires_at))
    await session.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=new_refresh)


async def logout(session: AsyncSession, raw_refresh_token: str) -> None:
    item = await get_refresh_token(session, hash_refresh_token(raw_refresh_token))
    if item:
        item.revoked_at = datetime.now(timezone.utc)
        await session.commit()


async def list_users(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    filters = []
    if keyword:
        like = f"%{keyword}%"
        filters.append(or_(User.username.ilike(like), User.nickname.ilike(like), User.email.ilike(like)))

    total_stmt = select(func.count()).select_from(User)
    list_stmt = select(User).options(selectinload(User.roles)).order_by(User.created_at.desc())
    if filters:
        total_stmt = total_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = await session.scalar(total_stmt)
    result = await session.execute(list_stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [user_to_out(user).model_dump() for user in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_user(session: AsyncSession, payload: UserCreate) -> UserOut:
    exists = await get_user_by_username(session, payload.username)
    if exists:
        raise forbidden("username already exists")
    roles = await get_roles_by_ids(session, payload.role_ids)
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname or payload.username,
        email=payload.email,
        phone=payload.phone,
        status=payload.status,
        is_superuser=payload.is_superuser,
        organization_id=payload.organization_id,
        roles=roles,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user, ["roles"])
    return user_to_out(user)


async def get_user_or_404(session: AsyncSession, user_id: str) -> User:
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise not_found("user not found")
    return user


async def update_user(session: AsyncSession, user_id: str, payload: UserUpdate) -> UserOut:
    user = await get_user_or_404(session, user_id)
    data = payload.model_dump(exclude_unset=True)
    role_ids = data.pop("role_ids", None)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        user.password_hash = hash_password(password)
    if role_ids is not None:
        user.roles = await get_roles_by_ids(session, role_ids)
    await session.commit()
    await session.refresh(user, ["roles"])
    return user_to_out(user)


async def delete_user(session: AsyncSession, user_id: str, current_user: User) -> None:
    user = await get_user_or_404(session, user_id)
    if user.username == "admin" or user.is_superuser:
        raise business_error("内置管理员账号不允许删除")
    if user.id == current_user.id:
        raise business_error("不能删除当前登录账号")
    log_count = await session.scalar(select(func.count()).select_from(OperationLog).where(OperationLog.user_id == user.id))
    if log_count:
        raise business_error("该用户已有操作日志，不允许物理删除，请改为禁用账号")
    await session.delete(user)
    await session.commit()
