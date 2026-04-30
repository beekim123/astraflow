from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import page_offset, page_payload
from app.core.time_format import format_datetime
from app.modules.audit_log.models import OperationLog


async def list_operation_logs(session: AsyncSession, page: int, page_size: int, keyword: str = "") -> dict:
    filters = []
    if keyword:
        like = f"%{keyword}%"
        filters.append(
            or_(
                OperationLog.request_id.ilike(like),
                OperationLog.module.ilike(like),
                OperationLog.action.ilike(like),
                OperationLog.path.ilike(like),
                OperationLog.ip.ilike(like),
            )
        )

    total_stmt = select(func.count()).select_from(OperationLog)
    list_stmt = select(OperationLog).order_by(OperationLog.created_at.desc())
    if filters:
        total_stmt = total_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = await session.scalar(total_stmt)
    result = await session.execute(list_stmt.offset(page_offset(page, page_size)).limit(page_size))
    items = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "request_id": item.request_id,
            "module": item.module,
            "action": item.action,
            "resource": item.resource,
            "method": item.method,
            "path": item.path,
            "ip": item.ip,
            "user_agent": item.user_agent,
            "status_code": item.status_code,
            "created_at": format_datetime(item.created_at),
        }
        for item in result.scalars().all()
    ]
    return page_payload(items, int(total or 0), page, page_size)
