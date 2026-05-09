from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import unauthorized
from app.modules.identity.models import User
from app.modules.learn.schemas import UserInfo


async def getInfo(current_user: User) -> UserInfo:
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        nickname=current_user.nickname,
        email=current_user.email,
        phone=current_user.phone,
        status=current_user.status,
        is_superuser=current_user.is_superuser,
        organization_id=current_user.organization_id,
    )


async def getInfoFromDb(session: AsyncSession, user_id: str) -> UserInfo:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or user.status != "active":
        raise unauthorized("user unavailable")

    return UserInfo(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        status=user.status,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
    )
