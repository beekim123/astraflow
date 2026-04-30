from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BaseModelMixin

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

role_menus = Table(
    "role_menus",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", String(36), ForeignKey("menus.id", ondelete="CASCADE"), primary_key=True),
)


class Role(BaseModelMixin, Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="active")

    users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles", lazy="selectin")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    menus: Mapped[list["Menu"]] = relationship(secondary=role_menus, back_populates="roles", lazy="selectin")


class Permission(BaseModelMixin, Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    resource: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")

    roles: Mapped[list[Role]] = relationship(secondary=role_permissions, back_populates="permissions", lazy="selectin")


class Menu(BaseModelMixin, Base):
    __tablename__ = "menus"

    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("menus.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    menu_type: Mapped[str] = mapped_column(String(20), default="page", index=True)
    app_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    path: Mapped[str] = mapped_column(String(160), default="")
    component: Mapped[str] = mapped_column(String(128), default="")
    icon: Mapped[str] = mapped_column(String(64), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    permission_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    roles: Mapped[list[Role]] = relationship(secondary=role_menus, back_populates="menus", lazy="selectin")
