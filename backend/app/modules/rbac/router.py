from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_permission
from app.core.responses import success
from app.db.session import get_session
from app.modules.identity.models import User
from app.modules.rbac import service
from app.modules.rbac.schemas import (
    MenuCreate,
    MenuUpdate,
    PermissionCreate,
    PermissionUpdate,
    RoleCreate,
    RoleUpdate,
)

menus_router = APIRouter(prefix="/api/menus", tags=["menus"])
roles_router = APIRouter(prefix="/api/admin/roles", tags=["admin-roles"])
permissions_router = APIRouter(prefix="/api/admin/permissions", tags=["admin-permissions"])
admin_menus_router = APIRouter(prefix="/api/admin/menus", tags=["admin-menus"])


@menus_router.get("/me")
async def my_menus(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return success([item.model_dump() for item in await service.list_menus_for_user(session, user)])


@roles_router.get("")
async def list_roles(
    _: User = Depends(require_permission("admin:roles")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_roles(session, page, page_size, keyword))


@roles_router.post("")
async def create_role(payload: RoleCreate, _: User = Depends(require_permission("admin:roles")), session: AsyncSession = Depends(get_session)):
    return success((await service.create_role(session, payload)).model_dump())


@roles_router.get("/{role_id}")
async def get_role(role_id: str, _: User = Depends(require_permission("admin:roles")), session: AsyncSession = Depends(get_session)):
    return success(service.role_to_out(await service.get_role_or_404(session, role_id)).model_dump())


@roles_router.put("/{role_id}")
async def update_role(role_id: str, payload: RoleUpdate, _: User = Depends(require_permission("admin:roles")), session: AsyncSession = Depends(get_session)):
    return success((await service.update_role(session, role_id, payload)).model_dump())


@roles_router.delete("/{role_id}")
async def delete_role(role_id: str, _: User = Depends(require_permission("admin:roles")), session: AsyncSession = Depends(get_session)):
    await service.delete_role(session, role_id)
    return success(True)


@permissions_router.get("")
async def list_permissions(
    _: User = Depends(require_permission("admin:permissions")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_permissions(session, page, page_size, keyword))


@permissions_router.post("")
async def create_permission(payload: PermissionCreate, _: User = Depends(require_permission("admin:permissions")), session: AsyncSession = Depends(get_session)):
    return success((await service.create_permission(session, payload)).model_dump())


@permissions_router.get("/{permission_id}")
async def get_permission(permission_id: str, _: User = Depends(require_permission("admin:permissions")), session: AsyncSession = Depends(get_session)):
    return success(service.permission_to_out(await service.get_permission_or_404(session, permission_id)).model_dump())


@permissions_router.put("/{permission_id}")
async def update_permission(permission_id: str, payload: PermissionUpdate, _: User = Depends(require_permission("admin:permissions")), session: AsyncSession = Depends(get_session)):
    return success((await service.update_permission(session, permission_id, payload)).model_dump())


@permissions_router.delete("/{permission_id}")
async def delete_permission(permission_id: str, _: User = Depends(require_permission("admin:permissions")), session: AsyncSession = Depends(get_session)):
    await service.delete_permission(session, permission_id)
    return success(True)


@admin_menus_router.get("")
async def list_menus(
    _: User = Depends(require_permission("admin:menus")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await service.list_menus(session, page, page_size, keyword))


@admin_menus_router.get("/tree")
async def menu_tree(_: User = Depends(require_permission("admin:menus")), session: AsyncSession = Depends(get_session)):
    return success([item.model_dump() for item in await service.list_menu_tree(session)])


@admin_menus_router.post("")
async def create_menu(payload: MenuCreate, _: User = Depends(require_permission("admin:menus")), session: AsyncSession = Depends(get_session)):
    return success((await service.create_menu(session, payload)).model_dump())


@admin_menus_router.get("/{menu_id}")
async def get_menu(menu_id: str, _: User = Depends(require_permission("admin:menus")), session: AsyncSession = Depends(get_session)):
    return success(service.menu_to_out(await service.get_menu_or_404(session, menu_id)).model_dump())


@admin_menus_router.put("/{menu_id}")
async def update_menu(menu_id: str, payload: MenuUpdate, _: User = Depends(require_permission("admin:menus")), session: AsyncSession = Depends(get_session)):
    return success((await service.update_menu(session, menu_id, payload)).model_dump())


@admin_menus_router.delete("/{menu_id}")
async def delete_menu(menu_id: str, _: User = Depends(require_permission("admin:menus")), session: AsyncSession = Depends(get_session)):
    await service.delete_menu(session, menu_id)
    return success(True)
