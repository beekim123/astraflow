import json

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.responses import success
from app.db.session import get_session
from app.modules.chat import service
from app.modules.chat.schemas import ConversationCreate, MessageCreate
from app.modules.identity.models import User

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success([item.model_dump() for item in await service.list_conversations(session, current_user.id)])


@router.post("/conversations")
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_conversation(session, current_user.id, payload)).model_dump())


@router.get("/model-routes")
async def list_model_route_options(
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success([item.model_dump() for item in await service.list_model_route_options(session)])


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.get_conversation_detail(session, conversation_id, current_user.id)).model_dump())


@router.post("/conversations/{conversation_id}/messages")
async def create_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_message(session, conversation_id, current_user.id, payload)).model_dump())


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    async def event_stream():
        # 主聊天流式入口：service 产出业务事件，router 只负责包装成 SSE 协议格式。
        async for event in service.stream_message_events(session, conversation_id, current_user.id, payload):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        yield "event: close\ndata: {}\n\n"

    # X-Accel-Buffering=no 用来提示 Nginx 不要缓存流式响应，否则前端看不到逐段输出。
    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)


@router.post("/conversations/{conversation_id}/attachments")
async def upload_attachment(
    conversation_id: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.upload_attachment(session, conversation_id, current_user.id, file)).model_dump())


@router.get("/conversations/{conversation_id}/artifacts")
async def list_artifacts(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success([item.model_dump() for item in await service.list_artifacts(session, conversation_id, current_user.id)])


@router.post("/artifacts/{artifact_id}/export")
async def export_artifact(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.export_artifact(session, artifact_id, current_user.id)).model_dump())


@router.post("/artifacts/{artifact_id}/draft")
async def create_draft(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.create_draft_from_artifact(session, artifact_id, current_user.id)).model_dump())


@router.get("/media-tasks/{task_id}")
async def get_media_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.get_media_task(session, task_id, current_user.id)).model_dump())
