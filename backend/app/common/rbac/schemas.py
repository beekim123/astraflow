from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import TimestampOutMixin


class RoleBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=64)
    description: str = ""
    status: str = "active"
    permission_ids: list[str] = Field(default_factory=list)
    menu_ids: list[str] = Field(default_factory=list)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    permission_ids: list[str] | None = None
    menu_ids: list[str] | None = None


class PermissionBrief(BaseModel):
    id: str
    code: str
    name: str


class MenuBrief(BaseModel):
    id: str
    code: str
    name: str
    menu_type: str
    app_key: str | None = None
    path: str


class RoleOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    permission_ids: list[str] = Field(default_factory=list)
    menu_ids: list[str] = Field(default_factory=list)
    permissions: list[PermissionBrief] = Field(default_factory=list)
    menus: list[MenuBrief] = Field(default_factory=list)


class PermissionBase(BaseModel):
    code: str = Field(min_length=2, max_length=128)
    name: str = Field(min_length=2, max_length=64)
    resource: str
    action: str
    description: str = ""


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: str | None = None
    resource: str | None = None
    action: str | None = None
    description: str | None = None


class PermissionOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    resource: str
    action: str
    description: str
    created_at: datetime
    updated_at: datetime


class MenuBase(BaseModel):
    parent_id: str | None = None
    code: str = Field(min_length=2, max_length=128)
    name: str
    menu_type: str = "page"
    app_key: str | None = None
    path: str = ""
    component: str = ""
    icon: str = ""
    sort: int = 0
    permission_code: str | None = None
    visible: bool = True
    status: str = "active"


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    parent_id: str | None = None
    code: str | None = None
    name: str | None = None
    menu_type: str | None = None
    app_key: str | None = None
    path: str | None = None
    component: str | None = None
    icon: str | None = None
    sort: int | None = None
    permission_code: str | None = None
    visible: bool | None = None
    status: str | None = None


class MenuOut(TimestampOutMixin):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str | None = None
    code: str
    name: str
    menu_type: str
    app_key: str | None = None
    path: str
    component: str
    icon: str
    sort: int
    permission_code: str | None = None
    visible: bool
    status: str
    created_at: datetime
    updated_at: datetime
    children: list["MenuOut"] = Field(default_factory=list)


MenuOut.model_rebuild()
