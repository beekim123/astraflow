import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.models import *  # noqa: F403
from app.db.session import async_session_maker, engine
from app.modules.identity.models import User
from app.modules.ai_admin.models import ForbiddenWord, ModelRouteRule, PromptTemplate
from app.modules.rbac.models import Menu, Permission, Role


PERMISSIONS = [
    ("admin:users", "用户管理", "users", "manage"),
    ("admin:roles", "角色管理", "roles", "manage"),
    ("admin:menus", "菜单管理", "menus", "manage"),
    ("admin:permissions", "权限管理", "permissions", "manage"),
    ("admin:audit_logs", "操作日志", "audit_logs", "read"),
    ("admin:ai", "AI 管理", "ai", "manage"),
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
        "code": "admin.ai",
        "name": "AI 管理",
        "path": "/admin/ai",
        "component": "AiManagement",
        "icon": "spark",
        "sort": 26,
        "permission_code": "admin:ai",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "system.admin",
    },
    {
        "code": "admin.ai.model_routes",
        "name": "模型路由",
        "path": "/admin/ai/model-routes",
        "component": "ModelRoutesPage",
        "icon": "route",
        "sort": 261,
        "permission_code": "admin:ai",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "admin.ai",
    },
    {
        "code": "admin.ai.prompts",
        "name": "Prompt 模板",
        "path": "/admin/ai/prompts",
        "component": "PromptTemplatesPage",
        "icon": "prompt",
        "sort": 262,
        "permission_code": "admin:ai",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "admin.ai",
    },
    {
        "code": "admin.ai.forbidden_words",
        "name": "违禁词策略",
        "path": "/admin/ai/forbidden-words",
        "component": "ForbiddenWordsPage",
        "icon": "shield",
        "sort": 263,
        "permission_code": "admin:ai",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "admin.ai",
    },
    {
        "code": "admin.ai.model_call_logs",
        "name": "模型调用日志",
        "path": "/admin/ai/model-call-logs",
        "component": "ModelCallLogsPage",
        "icon": "log",
        "sort": 264,
        "permission_code": "admin:ai",
        "menu_type": "page",
        "app_key": "admin",
        "parent_code": "admin.ai",
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

DEFAULT_MODEL_ROUTES = [
    ("mock", "开发 Mock", "mock", "mock-assistant", 70, 2048, 100),
    ("fast", "快速模式 Mock", "mock", "mock-fast", 40, 2048, 100),
    ("deep", "深度模式 Mock", "mock", "mock-deep", 70, 4096, 100),
    ("vision", "视觉模式 Mock", "mock", "mock-vision", 70, 2048, 100),
]

DEFAULT_PROMPTS = [
    ("通用助手", "chat-general", "v1", "你是 AstraFlow 企业 AI 工作台助手，请用清晰、简洁、可执行的方式回答用户。"),
    ("文件分析", "file-analysis", "v1", "请分析用户上传的文件，输出摘要、关键字段、风险点和待办事项。"),
    ("图片理解", "image-analysis", "v1", "请分析用户上传的图片，输出图片说明、可见文字、风险点和建议。"),
    ("工单草稿", "ticket-draft", "v1", "请根据用户输入生成工单草稿，包含标题、分类、优先级和处理建议。"),
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        permissions = []
        for code, name, resource, action in PERMISSIONS:
            result = await session.execute(select(Permission).where(Permission.code == code))
            permission = result.scalar_one_or_none()
            if permission is None:
                permission = Permission(code=code, name=name, resource=resource, action=action, description=name)
                session.add(permission)
            else:
                permission.name = name
                permission.resource = resource
                permission.action = action
            permissions.append(permission)

        menus_by_code = {}
        for item in MENUS:
            result = await session.execute(select(Menu).where(Menu.code == item["code"]))
            menu = result.scalar_one_or_none()
            if menu is None:
                menu = Menu(code=item["code"], name=item["name"])
                session.add(menu)
            menu.name = item["name"]
            menu.path = item["path"]
            menu.component = item["component"]
            menu.icon = item["icon"]
            menu.sort = item["sort"]
            menu.permission_code = item.get("permission_code")
            menu.menu_type = item["menu_type"]
            menu.app_key = item.get("app_key")
            menu.visible = True
            menu.status = "active"
            menus_by_code[item["code"]] = menu
        await session.flush()
        for item in MENUS:
            parent_code = item.get("parent_code")
            if parent_code and parent_code in menus_by_code:
                menus_by_code[item["code"]].parent_id = menus_by_code[parent_code].id

        menus = list(menus_by_code.values())
        result = await session.execute(select(Role).where(Role.code == "admin"))
        admin_role = result.scalar_one_or_none()
        if admin_role is None:
            admin_role = Role(code="admin", name="管理员", description="平台管理员")
            session.add(admin_role)
        admin_role.permissions = permissions
        admin_role.menus = menus

        member_menus = [
            menu
            for menu in menus
            if menu.menu_type == "system" and menu.app_key in {"chat", "audit", "ticket", "customer-h5", "marketing"}
        ]
        result = await session.execute(select(Role).where(Role.code == "member"))
        member_role = result.scalar_one_or_none()
        if member_role is None:
            member_role = Role(code="member", name="普通成员", description="业务使用者")
            session.add(member_role)
        member_role.permissions = []
        member_role.menus = member_menus

        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                username="admin",
                password_hash=hash_password("Admin@123456"),
                nickname="平台管理员",
                is_superuser=True,
                roles=[admin_role],
            )
            session.add(admin)

        result = await session.execute(select(User).where(User.username == "member"))
        member = result.scalar_one_or_none()
        if member is None:
            member = User(
                username="member",
                password_hash=hash_password("Member@123456"),
                nickname="业务成员",
                is_superuser=False,
                roles=[member_role],
            )
            session.add(member)

        for mode, display_name, provider, model, temperature, max_tokens, priority in DEFAULT_MODEL_ROUTES:
            result = await session.execute(select(ModelRouteRule).where(ModelRouteRule.mode == mode))
            route = result.scalar_one_or_none()
            if route is None:
                session.add(
                    ModelRouteRule(
                        mode=mode,
                        display_name=display_name,
                        provider=provider,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        priority=priority,
                        health_status="healthy" if provider == "mock" else "unknown",
                        fallback_enabled=True,
                        enabled=True,
                    )
                )
            else:
                if not route.display_name:
                    route.display_name = display_name
                if not route.priority:
                    route.priority = priority
                if not route.health_status:
                    route.health_status = "healthy" if route.provider == "mock" else "unknown"

        for name, scene, version, content in DEFAULT_PROMPTS:
            result = await session.execute(select(PromptTemplate).where(PromptTemplate.scene == scene))
            if result.scalar_one_or_none() is None:
                session.add(
                    PromptTemplate(
                        name=name,
                        scene=scene,
                        version=version,
                        content=content,
                        variables_json={},
                        enabled=True,
                    )
                )

        result = await session.execute(select(ForbiddenWord).where(ForbiddenWord.word == "违法"))
        if result.scalar_one_or_none() is None:
            session.add(ForbiddenWord(word="违法", category="default", action="block", enabled=True))

        await session.commit()
        print("Seed complete: admin/Admin@123456, member/Member@123456")


if __name__ == "__main__":
    asyncio.run(seed())
