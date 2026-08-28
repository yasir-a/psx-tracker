"""corporate actions schema

Revision ID: 004_corporate_actions
Revises: 003_securities_and_prices
Create Date: 2026-08-28 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_corporate_actions"
down_revision: Union[str, None] = "003_securities_and_prices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "corporate_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("action_type", sa.String(length=30), nullable=False),
        sa.Column("tax_status", sa.String(length=20), nullable=True),
        sa.Column("gross_amount", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_deducted", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("zakat_deducted", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("net_amount", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("quantity_adjusted", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("ratio", sa.Numeric(10, 4), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_corporate_actions_portfolio_id", "corporate_actions", ["portfolio_id"])
    op.create_index("ix_corporate_actions_symbol", "corporate_actions", ["symbol"])


def downgrade() -> None:
    op.drop_table("corporate_actions")