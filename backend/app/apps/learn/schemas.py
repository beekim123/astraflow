from pydantic import BaseModel, EmailStr, Field


class UserInfo(BaseModel):
    id: str
    username: str = Field(min_length=2, max_length=64)
    nickname: str = ""
    email: EmailStr | None = None
    phone: str | None = None
    status: str
    is_superuser: bool
    organization_id: str
