from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.rbac.models import Menu, Permission, Role


async def get_roles_by_ids(session: AsyncSession, role_ids: list[str]) -> list[Role]:
    if not role_ids:
        return []
    result = await session.execute(select(Role).where(Role.id.in_(role_ids)))
    return list(result.scalars().all())


async def get_permissions_by_ids(session: AsyncSession, permission_ids: list[str]) -> list[Permission]:
    if not permission_ids:
        return []
    result = await session.execute(select(Permission).where(Permission.id.in_(permission_ids)))
    return list(result.scalars().all())


async def get_menus_by_ids(session: AsyncSession, menu_ids: list[str]) -> list[Menu]:
    if not menu_ids:
        return []
    result = await session.execute(select(Menu).where(Menu.id.in_(menu_ids)))
    return list(result.scalars().all())


async def list_roles(session: AsyncSession) -> list[Role]:
    result = await session.execute(select(Role).options(selectinload(Role.permissions), selectinload(Role.menus)).order_by(Role.created_at.desc()))
    return list(result.scalars().all())

