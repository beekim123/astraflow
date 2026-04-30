"""add menu metadata for RBAC

Revision ID: 0002_menu_metadata
Revises: 0001_initial
Create Date: 2026-04-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_menu_metadata"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("menus", sa.Column("code", sa.String(length=128), nullable=True))
    op.add_column("menus", sa.Column("menu_type", sa.String(length=20), nullable=True))
    op.add_column("menus", sa.Column("app_key", sa.String(length=64), nullable=True))
    op.add_column("menus", sa.Column("status", sa.String(length=20), nullable=True))

    op.execute(
        """
        UPDATE menus
        SET
          code = CASE path
            WHEN '/systems' THEN 'portal.systems'
            WHEN '/admin' THEN 'system.admin'
            WHEN '/admin/users' THEN 'admin.users'
            WHEN '/admin/roles' THEN 'admin.roles'
            WHEN '/admin/menus' THEN 'admin.menus'
            WHEN '/admin/permissions' THEN 'admin.permissions'
            WHEN '/admin/audit-logs' THEN 'admin.audit_logs'
            WHEN '/chat' THEN 'system.chat'
            WHEN '/audit' THEN 'system.audit'
            WHEN '/ticket' THEN 'system.ticket'
            WHEN '/customer-h5' THEN 'system.customer_h5'
            WHEN '/marketing' THEN 'system.marketing'
            ELSE 'menu.' || id
          END,
          menu_type = CASE
            WHEN path IN ('/admin', '/chat', '/audit', '/ticket', '/customer-h5', '/marketing') THEN 'system'
            ELSE 'page'
          END,
          app_key = CASE
            WHEN path = '/systems' THEN 'portal'
            WHEN path LIKE '/admin%' THEN 'admin'
            WHEN path = '/chat' THEN 'chat'
            WHEN path = '/audit' THEN 'audit'
            WHEN path = '/ticket' THEN 'ticket'
            WHEN path = '/customer-h5' THEN 'customer-h5'
            WHEN path = '/marketing' THEN 'marketing'
            ELSE NULL
          END,
          status = 'active'
        """
    )
    op.execute(
        """
        UPDATE menus child
        SET parent_id = parent.id
        FROM menus parent
        WHERE parent.path = '/admin'
          AND child.path IN (
            '/admin/users',
            '/admin/roles',
            '/admin/menus',
            '/admin/permissions',
            '/admin/audit-logs'
          )
        """
    )

    op.alter_column("menus", "code", existing_type=sa.String(length=128), nullable=False)
    op.alter_column("menus", "menu_type", existing_type=sa.String(length=20), nullable=False)
    op.alter_column("menus", "status", existing_type=sa.String(length=20), nullable=False)
    op.create_index(op.f("ix_menus_code"), "menus", ["code"], unique=True)
    op.create_index(op.f("ix_menus_menu_type"), "menus", ["menu_type"], unique=False)
    op.create_index(op.f("ix_menus_app_key"), "menus", ["app_key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_menus_app_key"), table_name="menus")
    op.drop_index(op.f("ix_menus_menu_type"), table_name="menus")
    op.drop_index(op.f("ix_menus_code"), table_name="menus")
    op.drop_column("menus", "status")
    op.drop_column("menus", "app_key")
    op.drop_column("menus", "menu_type")
    op.drop_column("menus", "code")
