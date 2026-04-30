"""Import all models so Alembic and metadata creation can see them."""

from app.modules.audit_log.models import OperationLog  # noqa: F401
from app.modules.identity.models import RefreshToken, User, user_roles  # noqa: F401
from app.modules.rbac.models import Menu, Permission, Role, role_menus, role_permissions  # noqa: F401

