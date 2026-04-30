from collections.abc import Callable

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import forbidden, unauthorized
from app.core.security import decode_token
from app.db.session import get_session
from app.modules.identity.models import User
from app.modules.rbac.models import Permission, Role

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise unauthorized()
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise unauthorized("invalid token") from None
    if payload.get("type") != "access" or not payload.get("sub"):
        raise unauthorized("invalid token")

    result = await session.execute(
        select(User)
        .where(User.id == payload["sub"])
        .options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.roles).selectinload(Role.menus),
        )
    )
    user = result.scalar_one_or_none()
    if user is None or user.status != "active":
        raise unauthorized("user unavailable")
    request.state.user_id = user.id
    return user


def get_permission_codes(user: User) -> set[str]:
    if user.is_superuser:
        return {"*"}
    codes: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            codes.add(permission.code)
    return codes


def require_permission(code: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        codes = get_permission_codes(user)
        if "*" not in codes and code not in codes:
            raise forbidden(f"missing permission: {code}")
        return user

    return dependency


async def list_all_permissions(session: AsyncSession) -> list[str]:
    result = await session.execute(select(Permission.code))
    return list(result.scalars().all())
