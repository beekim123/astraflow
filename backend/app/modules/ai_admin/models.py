from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base, BaseModelMixin

json_type = JSON().with_variant(JSONB, "postgresql")


class PromptTemplate(BaseModelMixin, Base):
    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(128), index=True)
    scene: Mapped[str] = mapped_column(String(64), index=True)
    version: Mapped[str] = mapped_column(String(32), default="v1")
    content: Mapped[str] = mapped_column(Text)
    variables_json: Mapped[dict] = mapped_column(json_type, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class ForbiddenWord(BaseModelMixin, Base):
    __tablename__ = "forbidden_words"

    word: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), default="default")
    action: Mapped[str] = mapped_column(String(32), default="block")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class ModelRouteRule(BaseModelMixin, Base):
    __tablename__ = "model_route_rules"

    mode: Mapped[str] = mapped_column(String(32), index=True)
    display_name: Mapped[str] = mapped_column(String(128), default="")
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    model: Mapped[str] = mapped_column(String(128), default="mock-assistant")
    temperature: Mapped[int] = mapped_column(Integer, default=70)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    priority: Mapped[int] = mapped_column(Integer, default=100, index=True)
    health_status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, default="")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class ModelCallLog(BaseModelMixin, Base):
    __tablename__ = "model_call_logs"

    request_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    model: Mapped[str] = mapped_column(String(128), default="mock-assistant")
    mode: Mapped[str] = mapped_column(String(32), default="mock")
    prompt_scene: Mapped[str] = mapped_column(String(64), default="chat-general")
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="success")
    error_message: Mapped[str] = mapped_column(Text, default="")
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
