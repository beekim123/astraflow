from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import forbidden, not_found
from app.core.pagination import page_offset, page_payload
from app.common.identity.models import User
from app.common.rbac.models import Menu, Permission, Role
from app.common.rbac.repository import get_menus_by_ids, get_permissions_by_ids
from app.common.rbac.schemas import (
    MenuCreate,
    MenuOut,
    MenuUpdate,
    PermissionCreate,
    PermissionOut,
    PermissionUpdate,
    RoleCreate,
    RoleOut,
    RoleUpdate,
)


def permission_to_out(permission: Permission) -> PermissionOut:
    return PermissionOut.model_validate(permission)


def role_to_out(role: Role) -> RoleOut:
    return RoleOut(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        status=role.status,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permission_ids=[item.id for item in role.permissions],
        menu_ids=[item.id for item in role.menus],
        permissions=[{"id": item.id, "code": item.code, "name": item.name} for item in role.permissions],
        menus=[
            {
                "id": item.id,
                "code": item.code,
                "name": item.name,
                "menu_type": item.menu_type,
                "app_key": item.app_key,
                "path": item.path,
            }
            for item in role.menus
        ],
    )


def menu_to_out(menu: Menu, children: list[MenuOut] | None = None) -> MenuOut:
    return MenuOut(
        id=menu.id,
        parent_id=menu.parent_id,
        code=menu.code,
        name=menu.name,
        menu_type=menu.menu_type,
        app_key=menu.app_key,
        path=menu.path,
        component=menu.component,
        icon=menu.icon,
        sort=menu.sort,
        permission_code=menu.permission_code,
        visible=menu.visible,
        status=menu.status,
        created_at=menu.created_at,
        updated_at=menu.updated_at,
        children=children or [],
    )


def build_menu_tree(menus: list[Menu]) -> list[MenuOut]:
    items = sorted(menus, key=lambda item: item.sort)
    by_parent: dict[str | None, list[Menu]] = {}
    for menu in items:
        by_parent.setdefault(menu.parent_id, []).append(menu)

    def build(parent_id: str | None) -> list[MenuOut]:
        return [menu_to_out(menu, build(menu.id)) for menu in by_parent.get(parent_id, [])]

    return build(None)


async def list_menus_for_user(session: AsyncSession, user: User) -> list[MenuOut]:
    result = await session.execute(select(Menu).where(Menu.visible.is_(True), Menu.status == "active").order_by(Menu.sort))
    all_menus = list(result.scalars().all())
    if user.is_superuser:
        return build_menu_tree(all_menus)

    by_id = {menu.id: menu for menu in all_menus}
    seen: dict[str, Menu] = {}
    for role in user.roles:
        for menu in role.menus:
            if menu.visible and menu.status == "active":
                seen[menu.id] = menu

    # 授权子页面时自动补父菜单，避免前端菜单树断层。
    for menu in list(seen.values()):
        parent_id = menu.parent_id
        while parent_id:
            parent = by_id.get(parent_id)
            if parent is None:
                break
            seen[parent.id] = parent
            parent_id = parent.parent_id

    return build_menu_tree(list(seen.values()))


async def list_roles(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    filters = []
    if keyword:
        like = f"%{keyword}%"
        filters.append(or_(Role.code.ilike(like), Role.name.ilike(like), Role.description.ilike(like)))

    total_stmt = select(func.count()).select_from(Role)
    list_stmt = select(Role).options(selectinload(Role.permissions), selectinload(Role.menus)).order_by(Role.created_at.desc())
    if filters:
        total_stmt = total_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = await session.scalar(total_stmt)
    result = await session.execute(list_stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [role_to_out(item).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_role(session: AsyncSession, payload: RoleCreate) -> RoleOut:
    exists = await session.execute(select(Role).where(Role.code == payload.code))
    if exists.scalar_one_or_none():
        raise forbidden("role code already exists")
    role = Role(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        permissions=await get_permissions_by_ids(session, payload.permission_ids),
        menus=await get_menus_by_ids(session, payload.menu_ids),
    )
    session.add(role)
    await session.commit()
    await session.refresh(role, ["permissions", "menus"])
    return role_to_out(role)


async def get_role_or_404(session: AsyncSession, role_id: str) -> Role:
    result = await session.execute(
        select(Role).where(Role.id == role_id).options(selectinload(Role.permissions), selectinload(Role.menus))
    )
    role = result.scalar_one_or_none()
    if role is None:
        raise not_found("role not found")
    return role


async def update_role(session: AsyncSession, role_id: str, payload: RoleUpdate) -> RoleOut:
    role = await get_role_or_404(session, role_id)
    data = payload.model_dump(exclude_unset=True)
    permission_ids = data.pop("permission_ids", None)
    menu_ids = data.pop("menu_ids", None)
    for key, value in data.items():
        setattr(role, key, value)
    if permission_ids is not None:
        role.permissions = await get_permissions_by_ids(session, permission_ids)
    if menu_ids is not None:
        role.menus = await get_menus_by_ids(session, menu_ids)
    await session.commit()
    await session.refresh(role, ["permissions", "menus"])
    return role_to_out(role)


async def delete_role(session: AsyncSession, role_id: str) -> None:
    role = await get_role_or_404(session, role_id)
    await session.delete(role)
    await session.commit()


async def list_permissions(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    filters = []
    if keyword:
        like = f"%{keyword}%"
        filters.append(
            or_(
                Permission.code.ilike(like),
                Permission.name.ilike(like),
                Permission.resource.ilike(like),
                Permission.action.ilike(like),
            )
        )

    total_stmt = select(func.count()).select_from(Permission)
    list_stmt = select(Permission).order_by(Permission.resource, Permission.action)
    if filters:
        total_stmt = total_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = await session.scalar(total_stmt)
    result = await session.execute(list_stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [permission_to_out(item).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_permission(session: AsyncSession, payload: PermissionCreate) -> PermissionOut:
    exists = await session.execute(select(Permission).where(Permission.code == payload.code))
    if exists.scalar_one_or_none():
        raise forbidden("permission code already exists")
    item = Permission(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return permission_to_out(item)


async def get_permission_or_404(session: AsyncSession, permission_id: str) -> Permission:
    item = await session.get(Permission, permission_id)
    if item is None:
        raise not_found("permission not found")
    return item


async def update_permission(session: AsyncSession, permission_id: str, payload: PermissionUpdate) -> PermissionOut:
    item = await get_permission_or_404(session, permission_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return permission_to_out(item)


async def delete_permission(session: AsyncSession, permission_id: str) -> None:
    item = await get_permission_or_404(session, permission_id)
    await session.delete(item)
    await session.commit()


async def list_menu_tree(session: AsyncSession) -> list[MenuOut]:
    result = await session.execute(select(Menu).order_by(Menu.sort))
    return build_menu_tree(list(result.scalars().all()))


async def list_menus(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    filters = []
    if keyword:
        like = f"%{keyword}%"
        filters.append(or_(Menu.code.ilike(like), Menu.name.ilike(like), Menu.path.ilike(like), Menu.app_key.ilike(like)))

    total_stmt = select(func.count()).select_from(Menu)
    list_stmt = select(Menu).order_by(Menu.sort)
    if filters:
        total_stmt = total_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = await session.scalar(total_stmt)
    result = await session.execute(list_stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [menu_to_out(item).model_dump() for item in result.scalars().all()]
    return page_payload(items, int(total or 0), page, page_size)


async def create_menu(session: AsyncSession, payload: MenuCreate) -> MenuOut:
    item = Menu(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return menu_to_out(item)


async def get_menu_or_404(session: AsyncSession, menu_id: str) -> Menu:
    item = await session.get(Menu, menu_id)
    if item is None:
        raise not_found("menu not found")
    return item


async def update_menu(session: AsyncSession, menu_id: str, payload: MenuUpdate) -> MenuOut:
    item = await get_menu_or_404(session, menu_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return menu_to_out(item)


async def delete_menu(session: AsyncSession, menu_id: str) -> None:
    item = await get_menu_or_404(session, menu_id)
    await session.delete(item)
    await session.commit()
