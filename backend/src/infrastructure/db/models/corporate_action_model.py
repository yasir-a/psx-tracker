from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.corporate_actions.corporate_action_type import CorporateActionType
from src.domain.corporate_actions.tax_status import TaxStatus
from src.infrastructure.db.base import Base, TimestampMixin


class CorporateActionModel(Base, TimestampMixin):
    """SQLAlchemy model for corporate actions history."""

    __tablename__ = "corporate_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    action_type: Mapped[CorporateActionType] = mapped_column(
        Enum(CorporateActionType, name="corporate_action_type_enum"), nullable=False
    )
    tax_status: Mapped[TaxStatus | None] = mapped_column(
        Enum(TaxStatus, name="tax_status_enum"), nullable=True
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    tax_deducted: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    zakat_deducted: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    quantity_adjusted: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)