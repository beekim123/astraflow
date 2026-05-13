from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, BaseModelMixin

json_type = JSON().with_variant(JSONB, "postgresql")


class ChatConversation(BaseModelMixin, Base):
    __tablename__ = "chat_conversations"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160), default="新的 AI 工作台会话")
    mode: Mapped[str] = mapped_column(String(32), default="general", index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="conversation", lazy="selectin")


class ChatMessage(BaseModelMixin, Base):
    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    content: Mapped[str] = mapped_column(Text, default="")
    content_type: Mapped[str] = mapped_column(String(32), default="text")
    status: Mapped[str] = mapped_column(String(32), default="success")
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    model: Mapped[str] = mapped_column(String(128), default="mock-assistant")
    mode: Mapped[str] = mapped_column(String(32), default="mock")
    request_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    reasoning_summary: Mapped[str] = mapped_column(Text, default="")
    process_steps: Mapped[list] = mapped_column(json_type, default=list)

    conversation: Mapped[ChatConversation] = relationship(back_populates="messages")


class ChatAttachment(BaseModelMixin, Base):
    __tablename__ = "chat_attachments"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(Text)
    public_url: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="ready", index=True)


class ChatArtifact(BaseModelMixin, Base):
    __tablename__ = "chat_artifacts"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(32), default="report", index=True)
    title: Mapped[str] = mapped_column(String(160))
    content_markdown: Mapped[str] = mapped_column(Text, default="")
    content_json: Mapped[dict] = mapped_column(json_type, default=dict)
    file_url: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="ready", index=True)


class AiMediaTask(BaseModelMixin, Base):
    __tablename__ = "ai_media_tasks"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(32), default="video-summary", index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed", index=True)
    input_attachment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("chat_attachments.id", ondelete="SET NULL"), nullable=True)
    result_artifact_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("chat_artifacts.id", ondelete="SET NULL"), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=100)
    error_message: Mapped[str] = mapped_column(Text, default="")
