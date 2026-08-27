from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


@dataclass
class Transaction:
    """Immutable ledger event record."""

    portfolio_id: UUID
    transaction_type: TransactionType
    executed_at: datetime
    id: UUID = field(default_factory=uuid4)
    symbol: str | None = None
    quantity: Quantity = field(default_factory=Quantity.zero)
    price_per_share: Money = field(default_factory=Money.zero)
    brokerage_fee: Money = field(default_factory=Money.zero)
    regulatory_fee: Money = field(default_factory=Money.zero)
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_fees(self) -> Money:
        return self.brokerage_fee + self.regulatory_fee

    @property
    def gross_amount(self) -> Money:
        return (self.price_per_share * self.quantity.value).round(4)

    @property
    def net_amount(self) -> Money:
        """Net cash impact on portfolio."""
        if self.transaction_type == TransactionType.BUY:
            return self.gross_amount + self.total_fees
        elif self.transaction_type == TransactionType.SELL:
            return self.gross_amount - self.total_fees
        elif self.transaction_type == TransactionType.CASH_DEPOSIT:
            return self.price_per_share
        elif self.transaction_type == TransactionType.CASH_WITHDRAWAL:
            return -self.price_per_share
        elif self.transaction_type == TransactionType.DIVIDEND_CASH:
            return self.gross_amount - self.total_fees
        elif self.transaction_type == TransactionType.FEE:
            return -self.total_fees
        return Money.zero(self.price_per_share.currency)