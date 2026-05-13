from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import TimestampOutMixin


class PromptTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    scene: str = Field(min_length=2, max_length=64)
    version: str = "v1"
    content: str = Field(min_length=1)
    variables_json: dict = Field(default_factory=dict)
    enabled: bool = True


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    scene: str | None = None
    version: str | None = None
    content: str | None = None
    variables_json: dict | None = None
    enabled: bool | None = None


class PromptTemplateOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    scene: str
    version: str
    content: str
    variables_json: dict
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ForbiddenWordCreate(BaseModel):
    word: str = Field(min_length=1, max_length=128)
    category: str = "default"
    action: str = "block"
    enabled: bool = True


class ForbiddenWordUpdate(BaseModel):
    word: str | None = None
    category: str | None = None
    action: str | None = None
    enabled: bool | None = None


class ForbiddenWordOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    word: str
    category: str
    action: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ModelRouteRuleCreate(BaseModel):
    mode: str = Field(min_length=2, max_length=32)
    display_name: str = ""
    provider: str = "mock"
    model: str = "mock-assistant"
    temperature: int = Field(default=70, ge=0, le=200)
    max_tokens: int = Field(default=2048, ge=1, le=200000)
    priority: int = Field(default=100, ge=1, le=10000)
    health_status: str = "unknown"
    failure_count: int = Field(default=0, ge=0)
    last_error: str = ""
    fallback_enabled: bool = True
    enabled: bool = True


class ModelRouteRuleUpdate(BaseModel):
    mode: str | None = None
    display_name: str | None = None
    provider: str | None = None
    model: str | None = None
    temperature: int | None = Field(default=None, ge=0, le=200)
    max_tokens: int | None = Field(default=None, ge=1, le=200000)
    priority: int | None = Field(default=None, ge=1, le=10000)
    health_status: str | None = None
    failure_count: int | None = Field(default=None, ge=0)
    last_error: str | None = None
    fallback_enabled: bool | None = None
    enabled: bool | None = None


class ModelRouteRuleOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mode: str
    display_name: str
    provider: str
    model: str
    temperature: int
    max_tokens: int
    priority: int
    health_status: str
    failure_count: int
    last_error: str
    last_checked_at: datetime | None = None
    fallback_enabled: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ModelCallLogOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    user_id: str | None = None
    conversation_id: str | None = None
    message_id: str | None = None
    provider: str
    model: str
    mode: str
    prompt_scene: str
    prompt_version: str
    input_tokens: int
    output_tokens: int
    estimated_cost: int
    latency_ms: int
    status: str
    error_message: str
    fallback_used: bool
    created_at: datetime
    updated_at: datetime
