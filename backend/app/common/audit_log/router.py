from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_permission
from app.core.responses import success
from app.db.session import get_session
from app.common.audit_log.service import list_operation_logs
from app.common.identity.models import User

router = APIRouter(prefix="/api/admin/audit-logs", tags=["audit-logs"])


@router.get("")
async def audit_logs(
    _: User = Depends(require_permission("admin:audit_logs")),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    keyword: str = "",
):
    return success(await list_operation_logs(session, page, page_size, keyword))
