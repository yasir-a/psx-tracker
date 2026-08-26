from __future__ import annotations

import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.db.models.user_model import UserModel


class PortfolioModel(Base, TimestampMixin):
    """SQLAlchemy model mapping to the 'portfolios' table."""

    __tablename__ = "portfolios"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_portfolio_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="PKR",
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped[UserModel] = relationship("UserModel", back_populates="portfolios")
    cash_balance: Mapped[CashBalanceModel | None] = relationship(
        "CashBalanceModel",
        back_populates="portfolio",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CashBalanceModel(Base):
    """SQLAlchemy model mapping to the 'cash_balances' table."""

    __tablename__ = "cash_balances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="PKR",
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        default=Decimal("0.0000"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    portfolio: Mapped[PortfolioModel] = relationship("PortfolioModel", back_populates="cash_balance")