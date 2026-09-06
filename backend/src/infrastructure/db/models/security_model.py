from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import Boolean, Date, DateTime, Enum, Index, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.market.security import SecurityType
from src.infrastructure.db.base import Base, TimestampMixin


class SecurityModel(Base, TimestampMixin):
    """SQLAlchemy model for securities catalog."""

    __tablename__ = "securities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    security_type: Mapped[SecurityType] = mapped_column(
        Enum(SecurityType, name="security_type_enum"), default=SecurityType.EQUITY, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class HistoricalPriceModel(Base):
    """SQLAlchemy model for daily historical end-of-day prices."""

    __tablename__ = "historical_prices"
    __table_args__ = (
        Index("ix_historical_prices_symbol_date", "symbol", "trade_date", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    volume: Mapped[int] = mapped_column(default=0, nullable=False)


class IntradaySnapshotModel(Base):
    """SQLAlchemy model persisting full timestamped intraday tick histories for weekends and off-market hours."""

    __tablename__ = "intraday_snapshots"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    ticks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)