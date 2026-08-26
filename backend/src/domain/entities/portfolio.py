from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class CashBalance:
    """Pure domain entity representing available cash inside a portfolio."""

    portfolio_id: UUID
    currency: str = "PKR"
    amount: Decimal = Decimal("0.0000")
    id: UUID = field(default_factory=uuid4)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Portfolio:
    """Pure domain entity representing an investment portfolio."""

    user_id: UUID
    name: str
    description: str | None = None
    currency: str = "PKR"
    is_default: bool = False
    id: UUID = field(default_factory=uuid4)
    cash_balance: CashBalance | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))