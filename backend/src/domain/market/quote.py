from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from src.domain.values.money import Money


@dataclass(frozen=True)
class MarketQuote:
    """Real-time / Intraday price quote for a security."""

    symbol: str
    current_price: Money
    previous_close: Money
    change: Money
    change_percent: Decimal
    volume: int
    updated_at: datetime

    @classmethod
    def create(
        cls,
        symbol: str,
        current_price: Money,
        previous_close: Money,
        volume: int = 0,
        updated_at: datetime | None = None,
    ) -> MarketQuote:
        change = (current_price - previous_close).round(4)
        if previous_close.amount > Decimal("0"):
            pct = ((change.amount / previous_close.amount) * Decimal("100")).quantize(Decimal("0.01"))
        else:
            pct = Decimal("0.00")
        return cls(
            symbol=symbol.upper().strip(),
            current_price=current_price.round(4),
            previous_close=previous_close.round(4),
            change=change,
            change_percent=pct,
            volume=volume,
            updated_at=updated_at or datetime.now(timezone.utc),
        )


@dataclass(frozen=True)
class HistoricalPrice:
    """End-of-day historical price bar."""

    symbol: str
    trade_date: date
    open_price: Money
    high_price: Money
    low_price: Money
    close_price: Money
    volume: int