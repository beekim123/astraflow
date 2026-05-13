"""add streaming route metadata and chat provider

Revision ID: 0005_streaming_routes_rag
Revises: 0004_chat_reasoning_trace
Create Date: 2026-05-11
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0005_streaming_routes_rag"
down_revision: str | None = "0004_chat_reasoning_trace"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("chat_messages", sa.Column("provider", sa.String(length=64), server_default="mock", nullable=False))

    op.add_column("model_route_rules", sa.Column("display_name", sa.String(length=128), server_default="", nullable=False))
    op.add_column("model_route_rules", sa.Column("priority", sa.Integer(), server_default="100", nullable=False))
    op.add_column("model_route_rules", sa.Column("health_status", sa.String(length=32), server_default="unknown", nullable=False))
    op.add_column("model_route_rules", sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("model_route_rules", sa.Column("last_error", sa.Text(), server_default="", nullable=False))
    op.add_column("model_route_rules", sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("model_route_rules", sa.Column("fallback_enabled", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_index(op.f("ix_model_route_rules_priority"), "model_route_rules", ["priority"], unique=False)
    op.create_index(op.f("ix_model_route_rules_health_status"), "model_route_rules", ["health_status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_model_route_rules_health_status"), table_name="model_route_rules")
    op.drop_index(op.f("ix_model_route_rules_priority"), table_name="model_route_rules")
    op.drop_column("model_route_rules", "fallback_enabled")
    op.drop_column("model_route_rules", "last_checked_at")
    op.drop_column("model_route_rules", "last_error")
    op.drop_column("model_route_rules", "failure_count")
    op.drop_column("model_route_rules", "health_status")
    op.drop_column("model_route_rules", "priority")
    op.drop_column("model_route_rules", "display_name")
    op.drop_column("chat_messages", "provider")
