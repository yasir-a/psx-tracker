"""securities and historical prices schema

Revision ID: 003_securities_and_prices
Revises: 002_transactions_and_tax_lots
Create Date: 2026-08-28 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_securities_and_prices"
down_revision: Union[str, None] = "002_transactions_and_tax_lots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Securities table
    op.create_table(
        "securities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=False),
        sa.Column("security_type", sa.String(length=30), nullable=False, server_default="EQUITY"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_securities_symbol", "securities", ["symbol"], unique=True)
    op.create_index("ix_securities_sector", "securities", ["sector"])

    # Historical Prices table
    op.create_table(
        "historical_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("open_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("high_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("low_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("close_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.create_index("ix_historical_prices_symbol", "historical_prices", ["symbol"])
    op.create_index("ix_historical_prices_symbol_date", "historical_prices", ["symbol", "trade_date"], unique=True)


def downgrade() -> None:
    op.drop_table("historical_prices")
    op.drop_table("securities")