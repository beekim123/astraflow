from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import TimestampOutMixin


class ConversationCreate(BaseModel):
    title: str = "新的 AI 工作台会话"
    mode: str = "general"


class ConversationOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    mode: str
    status: str
    pinned: bool
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str = ""
    mode: str = "mock"
    task_type: str = "chat-general"
    attachment_ids: list[str] = Field(default_factory=list)


class ModelRouteOption(BaseModel):
    mode: str
    display_name: str
    provider: str
    model: str
    health_status: str


class MessageOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    content_type: str
    status: str
    provider: str
    model: str
    mode: str
    request_id: str
    reasoning_summary: str
    process_steps: list[str]
    created_at: datetime
    updated_at: datetime


class AttachmentOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    message_id: str | None = None
    user_id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    public_url: str
    status: str
    created_at: datetime
    updated_at: datetime


class ArtifactOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    message_id: str | None = None
    user_id: str
    artifact_type: str
    title: str
    content_markdown: str
    content_json: dict
    file_url: str
    status: str
    created_at: datetime
    updated_at: datetime


class MediaTaskOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    message_id: str | None = None
    user_id: str
    task_type: str
    status: str
    input_attachment_id: str | None = None
    result_artifact_id: str | None = None
    progress: int
    error_message: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(BaseModel):
    conversation: ConversationOut
    messages: list[MessageOut]
    attachments: list[AttachmentOut]
    artifacts: list[ArtifactOut]
    media_tasks: list[MediaTaskOut]


class ChatResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    artifacts: list[ArtifactOut]
    media_tasks: list[MediaTaskOut]
    model_meta: dict


class ArtifactDraftOut(BaseModel):
    draft_type: str
    title: str
    content: str
    source_artifact_id: str
