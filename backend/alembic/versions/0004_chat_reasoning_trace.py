"""add chat reasoning trace fields

Revision ID: 0004_chat_reasoning_trace
Revises: 0003_phase2_ai_workbench
Create Date: 2026-05-10
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_chat_reasoning_trace"
down_revision: str | None = "0003_phase2_ai_workbench"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column("reasoning_summary", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "chat_messages",
        sa.Column("process_steps", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("chat_messages", "process_steps")
    op.drop_column("chat_messages", "reasoning_summary")
