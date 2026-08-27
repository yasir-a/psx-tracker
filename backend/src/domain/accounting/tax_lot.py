from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


class LotStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class TaxLot:
    """Represents a discrete tax acquisition lot for FIFO tracking."""

    portfolio_id: UUID
    symbol: str
    original_quantity: Quantity
    remaining_quantity: Quantity
    unit_price: Money
    total_cost_basis: Money
    cost_basis_per_share: Money
    executed_at: datetime
    id: UUID = field(default_factory=uuid4)
    transaction_id: UUID | None = None
    status: LotStatus = LotStatus.OPEN
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def remaining_cost_basis(self) -> Money:
        """Calculate remaining cost basis for unsold shares in this lot."""
        if self.remaining_quantity.is_zero():
            return Money.zero(self.total_cost_basis.currency)
        return (self.cost_basis_per_share * self.remaining_quantity.value).round(4)


@dataclass
class LotDepletion:
    """Records the depletion of an existing tax lot by a SELL transaction."""

    lot_id: UUID
    sell_transaction_id: UUID
    depleted_quantity: Quantity
    cost_basis_depleted: Money
    gross_proceeds: Money
    allocated_fee: Money
    realized_gain: Money
    executed_at: datetime
    id: UUID = field(default_factory=uuid4)