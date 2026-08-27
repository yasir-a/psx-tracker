from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4
import pytest

from src.domain.accounting.fifo_engine import FIFOMatcher, InsufficientHoldingsError
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_fifo_multiple_buys_and_partial_sell() -> None:
    portfolio_id = uuid4()
    base_time = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)

    # Buy 1: 100 shares @ 100 + 10 fee -> total cost = 10,010 -> 100.10/share
    buy1 = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="ENGRO",
        quantity=Quantity(Decimal("100")),
        price_per_share=Money(Decimal("100")),
        brokerage_fee=Money(Decimal("10")),
        executed_at=base_time,
    )
    lot1 = FIFOMatcher.create_lot_from_buy(buy1)

    # Buy 2: 100 shares @ 120 + 10 fee -> total cost = 12,010 -> 120.10/share
    buy2 = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="ENGRO",
        quantity=Quantity(Decimal("100")),
        price_per_share=Money(Decimal("120")),
        brokerage_fee=Money(Decimal("10")),
        executed_at=base_time + timedelta(days=5),
    )
    lot2 = FIFOMatcher.create_lot_from_buy(buy2)

    # Sell: 150 shares @ 150 - 20 fee
    sell = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.SELL,
        symbol="ENGRO",
        quantity=Quantity(Decimal("150")),
        price_per_share=Money(Decimal("150")),
        brokerage_fee=Money(Decimal("20")),
        executed_at=base_time + timedelta(days=10),
    )

    depletions, remaining_lots = FIFOMatcher.match_sell(sell, [lot1, lot2])

    assert len(depletions) == 2
    # Depletion 1: 100 shares from Lot 1
    # Gross: 150 * 100 = 15,000
    # Cost: 100.10 * 100 = 10,010
    # Fee: 20 * (100 / 150) = 13.3333
    # Realized: 15,000 - 10,010 - 13.3333 = 4,976.6667
    assert depletions[0].depleted_quantity.value == Decimal("100")
    assert depletions[0].realized_gain.amount == Decimal("4976.6667")

    # Depletion 2: 50 shares from Lot 2
    # Gross: 150 * 50 = 7,500
    # Cost: 120.10 * 50 = 6,005
    # Fee: 20 * (50 / 150) = 6.6667
    # Realized: 7,500 - 6,005 - 6.6667 = 1,488.3333
    assert depletions[1].depleted_quantity.value == Decimal("50")
    assert depletions[1].realized_gain.amount == Decimal("1488.3333")

    # Remaining lots: 50 shares left in Lot 2
    assert len(remaining_lots) == 1
    assert remaining_lots[0].remaining_quantity.value == Decimal("50")
    assert remaining_lots[0].cost_basis_per_share.amount == Decimal("120.1000")


def test_insufficient_holdings_raises_error() -> None:
    portfolio_id = uuid4()
    buy = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="OGDC",
        quantity=Quantity(Decimal("50")),
        price_per_share=Money(Decimal("100")),
        executed_at=datetime.now(timezone.utc),
    )
    lot = FIFOMatcher.create_lot_from_buy(buy)

    sell = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.SELL,
        symbol="OGDC",
        quantity=Quantity(Decimal("100")),
        price_per_share=Money(Decimal("110")),
        executed_at=datetime.now(timezone.utc),
    )

    with pytest.raises(InsufficientHoldingsError):
        FIFOMatcher.match_sell(sell, [lot])