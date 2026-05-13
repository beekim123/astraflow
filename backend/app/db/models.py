"""Import all models so Alembic and metadata creation can see them."""

from app.common.audit_log.models import OperationLog  # noqa: F401
from app.common.ai_admin.models import ForbiddenWord, ModelCallLog, ModelRouteRule, PromptTemplate  # noqa: F401
from app.apps.chat.models import AiMediaTask, ChatArtifact, ChatAttachment, ChatConversation, ChatMessage  # noqa: F401
from app.common.identity.models import RefreshToken, User, user_roles  # noqa: F401
from app.common.rbac.models import Menu, Permission, Role, role_menus, role_permissions  # noqa: F401
