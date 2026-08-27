"""transactions and tax lots schema

Revision ID: 002_transactions_and_tax_lots
Revises: 001_initial_core_schema
Create Date: 2026-08-27 18:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_transactions_and_tax_lots"
down_revision: Union[str, None] = "001_initial_core_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Transactions table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=True),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("price_per_share", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("brokerage_fee", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("regulatory_fee", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_transactions_portfolio_id", "transactions", ["portfolio_id"])
    op.create_index("ix_transactions_symbol", "transactions", ["symbol"])

    # Tax Lots table
    op.create_table(
        "tax_lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("original_quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("remaining_quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("total_cost_basis", sa.Numeric(18, 4), nullable=False),
        sa.Column("cost_basis_per_share", sa.Numeric(18, 4), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tax_lots_portfolio_id", "tax_lots", ["portfolio_id"])
    op.create_index("ix_tax_lots_symbol", "tax_lots", ["symbol"])


def downgrade() -> None:
    op.drop_table("tax_lots")
    op.drop_table("transactions")