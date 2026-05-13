import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.clients.factory import get_agent_client
from app.ai.contracts.schemas import AgentRequest
from app.core.config import settings
from app.core.errors import business_error, forbidden, not_found
from app.core.logging import log_service_event
from app.apps.chat.models import AiMediaTask, ChatArtifact, ChatAttachment, ChatConversation, ChatMessage
from app.apps.chat.repository import get_conversation_for_user
from app.apps.chat.schemas import (
    ArtifactDraftOut,
    ArtifactOut,
    AttachmentOut,
    ChatResponse,
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    MediaTaskOut,
    MessageCreate,
    MessageOut,
    ModelRouteOption,
)
from app.common.ai_admin.models import ModelRouteRule

logger = logging.getLogger("astraflow.backend_api.chat")

IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
FILE_TYPES = {"application/pdf", "text/plain", "text/markdown", "application/json"}
VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}


def _conversation_out(item: ChatConversation) -> ConversationOut:
    return ConversationOut.model_validate(item)


def _message_out(item: ChatMessage) -> MessageOut:
    return MessageOut.model_validate(item)


def _attachment_out(item: ChatAttachment) -> AttachmentOut:
    return AttachmentOut.model_validate(item)


def _artifact_out(item: ChatArtifact) -> ArtifactOut:
    return ArtifactOut.model_validate(item)


def _media_task_out(item: AiMediaTask) -> MediaTaskOut:
    return MediaTaskOut.model_validate(item)


async def list_conversations(session: AsyncSession, user_id: str) -> list[ConversationOut]:
    result = await session.execute(
        select(ChatConversation).where(ChatConversation.user_id == user_id).order_by(ChatConversation.updated_at.desc())
    )
    return [_conversation_out(item) for item in result.scalars().all()]


async def create_conversation(session: AsyncSession, user_id: str, payload: ConversationCreate) -> ConversationOut:
    item = ChatConversation(user_id=user_id, title=payload.title, mode=payload.mode)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _conversation_out(item)


async def list_model_route_options(session: AsyncSession) -> list[ModelRouteOption]:
    # 聊天页模型下拉框从这里读取管理台配置，避免前端写死 real/mock/deep。
    result = await session.execute(
        select(ModelRouteRule)
        .where(ModelRouteRule.enabled.is_(True))
        .order_by(ModelRouteRule.mode, ModelRouteRule.priority, ModelRouteRule.created_at.desc())
    )
    options: dict[str, ModelRouteOption] = {}
    for item in result.scalars().all():
        if item.mode in options:
            continue
        options[item.mode] = ModelRouteOption(
            mode=item.mode,
            display_name=item.display_name or item.model,
            provider=item.provider,
            model=item.model,
            health_status=item.health_status,
        )
    return list(options.values())


async def get_conversation_detail(session: AsyncSession, conversation_id: str, user_id: str) -> ConversationDetail:
    # 打开某个会话详情时，需要一次性返回页面展示用的所有数据：
    # 1. conversation：会话本身
    # 2. messages：聊天消息
    # 3. attachments：用户上传的附件
    # 4. artifacts：AI 生成的报告/草稿等产物
    # 5. media_tasks：视频等异步媒体任务记录
    conversation = await get_conversation_for_user(session, conversation_id, user_id)
    messages = await session.execute(
        select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at)
    )
    attachments = await session.execute(
        select(ChatAttachment).where(ChatAttachment.conversation_id == conversation_id).order_by(ChatAttachment.created_at)
    )
    artifacts = await session.execute(
        select(ChatArtifact).where(ChatArtifact.conversation_id == conversation_id).order_by(ChatArtifact.created_at.desc())
    )
    media_tasks = await session.execute(
        select(AiMediaTask).where(AiMediaTask.conversation_id == conversation_id).order_by(AiMediaTask.created_at.desc())
    )
    return ConversationDetail(
        conversation=_conversation_out(conversation),
        messages=[_message_out(item) for item in messages.scalars().all()],
        attachments=[_attachment_out(item) for item in attachments.scalars().all()],
        artifacts=[_artifact_out(item) for item in artifacts.scalars().all()],
        media_tasks=[_media_task_out(item) for item in media_tasks.scalars().all()],
    )


async def create_message(session: AsyncSession, conversation_id: str, user_id: str, payload: MessageCreate) -> ChatResponse:
    # 非流式备用接口：流程和 stream_message_events 类似，只是不逐段 yield 给前端。
    await get_conversation_for_user(session, conversation_id, user_id)
    request_id = str(uuid4())
    started = perf_counter()
    # 先保存一条用户消息。role="user" 表示这是用户输入，不是 AI 回复。
    user_message = ChatMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=payload.content,
        content_type="text",
        mode=payload.mode,
        provider="",
        model="",
        request_id=request_id,
    )
    session.add(user_message)
    # flush 会把 INSERT 先发到数据库，但不提交事务；这样可以拿到数据库生成的 user_message.id。
    await session.flush()
    # 用户上传文件是先上传、后发送消息；这里把已经上传好的附件绑定到这条用户消息上。
    await _attach_uploads_to_message(session, conversation_id, user_id, user_message.id, payload.attachment_ids)

    # 调用 AI 网关。AgentRequest 是业务层传给 AI 层的统一请求对象。
    agent_result = await get_agent_client().run(
        AgentRequest(
            task_type=payload.task_type,
            user_id=user_id,
            payload={"content": payload.content},
            mode=payload.mode,
            prompt_scene=_scene_for(payload.task_type),
            conversation_id=conversation_id,
            message_id=user_message.id,
            request_id=request_id,
        )
    )
    # AI 网关返回后，再保存一条助手消息。role="assistant" 表示这是 AI 回复。
    assistant_message = ChatMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=agent_result.summary,
        content_type="markdown",
        status=agent_result.status,
        provider=agent_result.provider,
        model=agent_result.model,
        mode=agent_result.mode,
        request_id=request_id,
        reasoning_summary=agent_result.reasoning_summary,
        process_steps=agent_result.process_steps,
    )
    session.add(assistant_message)
    # flush 后 assistant_message.id 才可用，后面的 artifacts 需要关联到这条 AI 回复。
    await session.flush()

    # artifact 是 AI 生成的“产物”，例如报告、总结文档、草稿，不是用户上传的附件。
    artifacts = _build_artifacts(agent_result.data.get("artifacts", []), conversation_id, assistant_message.id, user_id)
    # add_all 表示把多个 ORM 对象加入待保存队列；真正提交仍然等后面的 commit。
    session.add_all(artifacts)
    await session.flush()
    # media_tasks 是视频/多模态处理任务记录。第二阶段先建结构，后续可换成真实异步任务。
    media_tasks = _build_media_tasks(payload.task_type, conversation_id, assistant_message.id, user_id, artifacts)
    session.add_all(media_tasks)
    # commit 才是正式提交事务；前面的用户消息、助手消息、产物、任务会一起生效。
    await session.commit()
    _log_chat_agent_finished(request_id, agent_result.provider, agent_result.model, agent_result.status, started)

    # commit 后 refresh 一下，把数据库里的默认值、时间字段等最新状态同步回 Python 对象。
    for item in [user_message, assistant_message, *artifacts, *media_tasks]:
        await session.refresh(item)

    return ChatResponse(
        user_message=_message_out(user_message),
        assistant_message=_message_out(assistant_message),
        artifacts=[_artifact_out(item) for item in artifacts],
        media_tasks=[_media_task_out(item) for item in media_tasks],
        model_meta={
            "provider": agent_result.provider,
            "model": agent_result.model,
            "mode": agent_result.mode,
            "input_tokens": agent_result.input_tokens,
            "output_tokens": agent_result.output_tokens,
            "estimated_cost": agent_result.estimated_cost,
            "fallback_used": agent_result.fallback_used,
            "reasoning_summary": agent_result.reasoning_summary,
            "process_steps": agent_result.process_steps,
            "evidence": agent_result.evidence,
            "route_chain": agent_result.route_chain,
        },
    )


async def stream_message_events(
    session: AsyncSession,
    conversation_id: str,
    user_id: str,
    payload: MessageCreate,
):
    # 这里是聊天后端主链路：校验会话归属 -> 保存用户消息 -> 调 AI 网关 -> 保存助手消息。
    await get_conversation_for_user(session, conversation_id, user_id)
    request_id = str(uuid4())
    started = perf_counter()
    # request_id 串起同一次请求里的用户消息、AI 回复和模型调用日志，排查问题时能关联起来。
    user_message = ChatMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=payload.content,
        content_type="text",
        mode=payload.mode,
        provider="",
        model="",
        request_id=request_id,
    )
    session.add(user_message)
    # 这里不能直接等 commit，因为后面附件和 AI 请求都需要 user_message.id。
    # flush 只执行 SQL 并拿到 id，事务仍然没结束，后面出错还能整体回滚。
    await session.flush()
    # flush 后 user_message.id 才可用，附件才能绑定到这条用户消息上。
    await _attach_uploads_to_message(session, conversation_id, user_id, user_message.id, payload.attachment_ids)

    result = None
    # AgentClient 会从 ai-gateway 持续产出 status/evidence/answer_delta/reasoning_delta，直接透传给前端。
    async for event in get_agent_client().stream(
        AgentRequest(
            task_type=payload.task_type,
            user_id=user_id,
            payload={"content": payload.content, "attachment_ids": payload.attachment_ids},
            mode=payload.mode,
            prompt_scene=_scene_for(payload.task_type),
            conversation_id=conversation_id,
            message_id=user_message.id,
            request_id=request_id,
        )
    ):
        if event["type"] == "_result":
            # _result 是内部结束信号，不直接发给前端；它里面放最终 AgentResult，供后端落库。
            result = event["result"]
            break
        # 普通事件才发给前端，例如 answer_delta、reasoning_delta、status、evidence。
        yield event

    if result is None:
        raise RuntimeError("stream did not produce a result")

    # 流式输出期间前端看到的是临时内容；这里才把最终助手回复正式落库。
    assistant_message = ChatMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=result.summary,
        content_type="markdown",
        status=result.status,
        provider=result.provider,
        model=result.model,
        mode=result.mode,
        request_id=request_id,
        reasoning_summary=result.reasoning_summary,
        process_steps=result.process_steps,
    )
    session.add(assistant_message)
    # 先 flush 拿到 assistant_message.id，因为 artifact 要挂到这条 AI 回复下面。
    await session.flush()

    # result.data["artifacts"] 是 AI 网关返回的产物列表，这里转成 ChatArtifact ORM 对象。
    artifacts = _build_artifacts(result.data.get("artifacts", []), conversation_id, assistant_message.id, user_id)
    # 批量保存产物。比如一次 AI 生成多个报告/草稿时，都放进 artifacts。
    session.add_all(artifacts)
    await session.flush()
    # 第二阶段先搭好多模态任务表结构，视频等复杂处理目前只生成任务记录和 mock 结果。
    media_tasks = _build_media_tasks(payload.task_type, conversation_id, assistant_message.id, user_id, artifacts)
    session.add_all(media_tasks)
    # 到这里才统一提交，保证“用户消息、AI 回复、产物、任务”要么一起成功，要么一起失败。
    await session.commit()
    _log_chat_agent_finished(request_id, result.provider, result.model, result.status, started)

    # refresh 不是提交，它是重新从数据库读取对象状态，拿到 created_at、updated_at 等字段。
    for item in [user_message, assistant_message, *artifacts, *media_tasks]:
        await session.refresh(item)

    # done 是发给前端的最终事件，告诉前端：后端已经落库完成，可以刷新会话详情。
    response = ChatResponse(
        user_message=_message_out(user_message),
        assistant_message=_message_out(assistant_message),
        artifacts=[_artifact_out(item) for item in artifacts],
        media_tasks=[_media_task_out(item) for item in media_tasks],
        model_meta={
            "provider": result.provider,
            "model": result.model,
            "mode": result.mode,
            "fallback_used": result.fallback_used,
            "evidence": result.evidence,
            "route_chain": result.route_chain,
        },
    )
    yield {"type": "done", "data": response.model_dump(mode="json")}


def _scene_for(task_type: str) -> str:
    # task_type 决定使用哪个 Prompt 场景；未知类型默认走普通聊天。
    if task_type in {"file-analysis", "image-analysis", "ticket-draft"}:
        return task_type
    return "chat-general"


def _log_chat_agent_finished(request_id: str, provider: str, model: str, status: str, started: float) -> None:
    log_service_event(
        logger,
        "backend_chat_agent_finished",
        request_id=request_id,
        provider=provider,
        model=model,
        latency_ms=int((perf_counter() - started) * 1000),
        status=status,
    )


def _build_artifacts(items: list[dict], conversation_id: str, message_id: str, user_id: str) -> list[ChatArtifact]:
    # 把 AI 网关返回的普通 dict 转成 SQLAlchemy ORM 对象，后面才能 session.add_all 保存。
    artifacts: list[ChatArtifact] = []
    for item in items:
        artifacts.append(
            ChatArtifact(
                conversation_id=conversation_id,
                message_id=message_id,
                user_id=user_id,
                artifact_type=item.get("artifact_type", "report"),
                title=item.get("title", "AI 工作台产物"),
                content_markdown=item.get("content_markdown", ""),
                content_json=item.get("content_json", {}),
                file_url=item.get("file_url", ""),
            )
        )
    return artifacts


def _build_media_tasks(
    task_type: str,
    conversation_id: str,
    message_id: str,
    user_id: str,
    artifacts: list[ChatArtifact],
) -> list[AiMediaTask]:
    if task_type != "video-task":
        return []
    # 目前视频任务是第二阶段占位：记录任务已完成，后续可以替换成真实 FFmpeg/异步队列处理。
    return [
        AiMediaTask(
            conversation_id=conversation_id,
            message_id=message_id,
            user_id=user_id,
            task_type="video-summary",
            status="completed",
            result_artifact_id=artifacts[0].id if artifacts else None,
            progress=100,
        )
    ]


async def _attach_uploads_to_message(
    session: AsyncSession,
    conversation_id: str,
    user_id: str,
    message_id: str,
    attachment_ids: list[str],
) -> None:
    if not attachment_ids:
        return
    # 附件必须属于当前用户和当前会话，防止拿别人的 attachment_id 越权绑定。
    result = await session.execute(
        select(ChatAttachment).where(
            ChatAttachment.id.in_(attachment_ids),
            ChatAttachment.conversation_id == conversation_id,
            ChatAttachment.user_id == user_id,
        )
    )
    attachments = result.scalars().all()
    if len(attachments) != len(set(attachment_ids)):
        raise forbidden("attachment forbidden")
    for item in attachments:
        # 这里不是上传文件，而是把“已经上传好的文件记录”挂到本次用户消息下。
        item.message_id = message_id
    # flush 把 UPDATE 发到数据库，但仍等外层统一 commit。
    await session.flush()


async def upload_attachment(
    session: AsyncSession,
    conversation_id: str,
    user_id: str,
    file: UploadFile,
) -> AttachmentOut:
    # 上传接口只负责文件落盘和记录元数据，具体“这次消息用了哪些附件”在发送消息时绑定。
    await get_conversation_for_user(session, conversation_id, user_id)
    content_type = file.content_type or "application/octet-stream"
    max_bytes = _max_upload_bytes(content_type)
    suffix = Path(file.filename or "upload.bin").suffix.lower()
    if not _is_allowed_file(content_type, suffix):
        raise business_error("不支持的文件类型")

    # 文件真实内容保存到 settings.upload_dir 指向的目录；数据库只保存路径和元数据。
    upload_root = Path(settings.upload_dir)
    upload_root.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}{suffix or '.bin'}"
    storage_path = upload_root / safe_name
    size = 0
    with storage_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                storage_path.unlink(missing_ok=True)
                raise business_error("文件超过大小限制")
            output.write(chunk)

    # ChatAttachment 是附件元数据表：文件名、类型、大小、磁盘路径、归属用户和会话。
    item = ChatAttachment(
        conversation_id=conversation_id,
        user_id=user_id,
        filename=file.filename or safe_name,
        content_type=content_type,
        size_bytes=size,
        storage_path=str(storage_path),
        status="ready",
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _attachment_out(item)


def _max_upload_bytes(content_type: str) -> int:
    if content_type in IMAGE_TYPES:
        return settings.upload_image_max_mb * 1024 * 1024
    if content_type in VIDEO_TYPES:
        return settings.upload_video_max_mb * 1024 * 1024
    return settings.upload_file_max_mb * 1024 * 1024


def _is_allowed_file(content_type: str, suffix: str) -> bool:
    allowed_suffixes = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf", ".txt", ".md", ".json", ".mp4", ".webm", ".mov"}
    return suffix in allowed_suffixes and content_type in (IMAGE_TYPES | FILE_TYPES | VIDEO_TYPES)


async def list_artifacts(session: AsyncSession, conversation_id: str, user_id: str) -> list[ArtifactOut]:
    await get_conversation_for_user(session, conversation_id, user_id)
    result = await session.execute(
        select(ChatArtifact).where(ChatArtifact.conversation_id == conversation_id).order_by(ChatArtifact.created_at.desc())
    )
    return [_artifact_out(item) for item in result.scalars().all()]


async def export_artifact(session: AsyncSession, artifact_id: str, user_id: str) -> ArtifactOut:
    artifact = await _get_artifact_for_user(session, artifact_id, user_id)
    return _artifact_out(artifact)


async def create_draft_from_artifact(session: AsyncSession, artifact_id: str, user_id: str) -> ArtifactDraftOut:
    artifact = await _get_artifact_for_user(session, artifact_id, user_id)
    return ArtifactDraftOut(
        draft_type="preview",
        title=f"{artifact.title} - 业务草稿",
        content=artifact.content_markdown,
        source_artifact_id=artifact.id,
    )


async def get_media_task(session: AsyncSession, task_id: str, user_id: str) -> MediaTaskOut:
    result = await session.execute(select(AiMediaTask).where(AiMediaTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise not_found("media task not found")
    if task.user_id != user_id:
        raise forbidden("media task forbidden")
    return _media_task_out(task)


async def _get_artifact_for_user(session: AsyncSession, artifact_id: str, user_id: str) -> ChatArtifact:
    result = await session.execute(select(ChatArtifact).where(ChatArtifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if artifact is None:
        raise not_found("artifact not found")
    if artifact.user_id != user_id:
        raise forbidden("artifact forbidden")
    return artifact
