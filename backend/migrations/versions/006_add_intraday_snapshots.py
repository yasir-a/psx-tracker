"""add intraday snapshots table for weekend and off-hours market persistence

Revision ID: 006_add_intraday_snapshots
Revises: 005_add_user_role
Create Date: 2026-09-06 16:15:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "006_add_intraday_snapshots"
down_revision: Union[str, None] = "005_add_user_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "intraday_snapshots",
        sa.Column("symbol", sa.String(length=20), primary_key=True, nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("ticks", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("intraday_snapshots")