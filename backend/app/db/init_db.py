import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.models import *  # noqa: F403
from app.db.session import async_session_maker, engine
from app.modules.identity.models import User
from app.modules.rbac.models import Menu, Permission, Role


PERMISSIONS = [
    ("admin:users", "用户管理", "users", "manage"),
    ("admin:roles", "角色管理", "roles", "manage"),
    ("admin:menus", "菜单管理", "menus", "manage"),
    ("admin:permissions", "权限管理", "permissions", "manage"),
    ("admin:audit_logs", "操作日志", "audit_logs", "read"),
]

MENUS = [
    {
        "code": "portal.systems",
        "name": "系统入口",
        "path": "/systems",
        "component": "portal",
        "icon": "grid",
        "sort": 10,
        "menu_type": "page",
        "app_key": "portal",
    },
    {
        "code": "system.admin",
        "name": "管理系统",
        "path": "/admin",
        "component": "app-admin",
        "icon": "settings",
        "sort": 20,
        "permission_code": "admin:users",
        "menu_type": "system",
        "app_key": "admin",
    },
    {
        "code": "admin.users",
        "name": "用户管理",
        "path": "/admin/users",
        "component": "UsersPage",
        "icon": "user",
        "sort": 21,
        "permission_code": "admin:users",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "admin.roles",
        "name": "角色管理",
        "path": "/admin/roles",
        "component": "RolesPage",
        "icon": "shield",
        "sort": 22,
        "permission_code": "admin:roles",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "admin.menus",
        "name": "菜单管理",
        "path": "/admin/menus",
        "component": "MenusPage",
        "icon": "menu",
        "sort": 23,
        "permission_code": "admin:menus",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "admin.permissions",
        "name": "权限管理",
        "path": "/admin/permissions",
        "component": "PermissionsPage",
        "icon": "key",
        "sort": 24,
        "permission_code": "admin:permissions",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "admin.audit_logs",
        "name": "操作日志",
        "path": "/admin/audit-logs",
        "component": "AuditLogsPage",
        "icon": "log",
        "sort": 25,
        "permission_code": "admin:audit_logs",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "system.chat",
        "name": "AI 对话",
        "path": "/chat",
        "component": "app-chat",
        "icon": "message",
        "sort": 30,
        "menu_type": "system",
        "app_key": "chat",
    },
    {
        "code": "system.audit",
        "name": "智能审核",
        "path": "/audit",
        "component": "app-audit",
        "icon": "scan",
        "sort": 40,
        "menu_type": "system",
        "app_key": "audit",
    },
    {
        "code": "system.ticket",
        "name": "AI 工单",
        "path": "/ticket",
        "component": "app-ticket",
        "icon": "ticket",
        "sort": 50,
        "menu_type": "system",
        "app_key": "ticket",
    },
    {
        "code": "system.customer_h5",
        "name": "H5 客服",
        "path": "/customer-h5",
        "component": "app-customer-h5",
        "icon": "phone",
        "sort": 60,
        "menu_type": "system",
        "app_key": "customer-h5",
    },
    {
        "code": "system.marketing",
        "name": "内容营销助手",
        "path": "/marketing",
        "component": "app-marketing",
        "icon": "spark",
        "sort": 70,
        "menu_type": "system",
        "app_key": "marketing",
    },
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        existing = await session.execute(select(User).where(User.username == "admin"))
        if existing.scalar_one_or_none():
            return

        permissions = [
            Permission(code=code, name=name, resource=resource, action=action, description=name)
            for code, name, resource, action in PERMISSIONS
        ]
        menus_by_code = {
            item["code"]: Menu(
                code=item["code"],
                name=item["name"],
                path=item["path"],
                component=item["component"],
                icon=item["icon"],
                sort=item["sort"],
                permission_code=item.get("permission_code"),
                menu_type=item["menu_type"],
                app_key=item.get("app_key"),
                visible=True,
                status="active",
            )
            for item in MENUS
        }
        menus = list(menus_by_code.values())
        session.add_all([*permissions, *menus])
        await session.flush()
        for item in MENUS:
            parent_code = item.get("parent_code")
            if parent_code:
                menus_by_code[item["code"]].parent_id = menus_by_code[parent_code].id
        admin_role = Role(code="admin", name="管理员", description="平台管理员", permissions=permissions, menus=menus)
        member_menus = [
            menu
            for menu in menus
            if menu.menu_type == "system" and menu.app_key in {"chat", "audit", "ticket", "customer-h5", "marketing"}
        ]
        member_role = Role(code="member", name="普通成员", description="业务使用者", permissions=[], menus=member_menus)
        admin = User(
            username="admin",
            password_hash=hash_password("Admin@123456"),
            nickname="平台管理员",
            is_superuser=True,
            roles=[admin_role],
        )
        member = User(
            username="member",
            password_hash=hash_password("Member@123456"),
            nickname="业务成员",
            is_superuser=False,
            roles=[member_role],
        )
        session.add_all([admin_role, member_role, admin, member])
        await session.commit()
        print("Seed complete: admin/Admin@123456, member/Member@123456")


if __name__ == "__main__":
    asyncio.run(seed())
