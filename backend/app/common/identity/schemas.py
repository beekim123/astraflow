from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.schemas import TimestampOutMixin


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    nickname: str = ""
    email: EmailStr | None = None
    phone: str | None = None
    status: str = "active"
    is_superuser: bool = False
    organization_id: str = "default"
    role_ids: list[str] = Field(default_factory=list)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    nickname: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: str | None = None
    is_superuser: bool | None = None
    organization_id: str | None = None
    role_ids: list[str] | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRoleBrief(BaseModel):
    id: str
    code: str
    name: str


class UserOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    nickname: str
    email: str | None = None
    phone: str | None = None
    status: str
    is_superuser: bool
    organization_id: str
    created_at: datetime
    updated_at: datetime
    role_ids: list[str] = Field(default_factory=list)
    roles: list[UserRoleBrief] = Field(default_factory=list)


class MeOut(BaseModel):
    id: str
    username: str
    nickname: str
    is_superuser: bool
    roles: list[str]
    permissions: list[str]
