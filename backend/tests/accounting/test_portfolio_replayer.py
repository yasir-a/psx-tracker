from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_full_portfolio_replayer_lifecycle() -> None:
    portfolio_id = uuid4()
    t0 = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)

    transactions = [
        # 1. Deposit 500,000 PKR
        Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            price_per_share=Money(Decimal("500000.00")),
            executed_at=t0,
        ),
        # 2. Buy 1,000 SYS @ 400 + 400 fee = 400,400 PKR
        Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.BUY,
            symbol="SYS",
            quantity=Quantity(Decimal("1000")),
            price_per_share=Money(Decimal("400.00")),
            brokerage_fee=Money(Decimal("400.00")),
            executed_at=t0 + timedelta(days=1),
        ),
        # 3. Cash Dividend from SYS: 5.00/sh = 5,000 PKR - 750 tax = 4,250 net
        Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.DIVIDEND_CASH,
            symbol="SYS",
            quantity=Quantity(Decimal("1000")),
            price_per_share=Money(Decimal("5.00")),
            regulatory_fee=Money(Decimal("750.00")),
            executed_at=t0 + timedelta(days=30),
        ),
        # 4. Sell 400 SYS @ 450 - 200 fee
        Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.SELL,
            symbol="SYS",
            quantity=Quantity(Decimal("400")),
            price_per_share=Money(Decimal("450.00")),
            brokerage_fee=Money(Decimal("200.00")),
            executed_at=t0 + timedelta(days=40),
        ),
    ]

    market_prices = {"SYS": Money(Decimal("480.00"))}

    valuation = PortfolioReplayer.replay(transactions, market_prices)

    # SYS Holding: 600 shares remaining
    sys_holding = valuation.holdings["SYS"]
    assert sys_holding.quantity.value == Decimal("600")
    # Cost per share = (400,400 / 1000) = 400.40
    assert sys_holding.cost_per_share.amount == Decimal("400.4000")
    # Remaining cost basis: 600 * 400.40 = 240,240
    assert sys_holding.total_cost_basis.amount == Decimal("240240.0000")

    # Realized Gain on 400 shares sold:
    # Gross: 400 * 450 = 180,000
    # Cost: 400 * 400.40 = 160,160
    # Fee: 200
    # Realized: 180,000 - 160,160 - 200 = 19,640
    assert valuation.realized_gain.amount == Decimal("19640.0000")

    # Market Value: 600 * 480 = 288,000
    assert valuation.total_market_value.amount == Decimal("288000.0000")
    # Unrealized Gain: 288,000 - 240,240 = 47,760
    assert valuation.unrealized_gain.amount == Decimal("47760.0000")
    # Unrealized %: (47,760 / 240,240) * 100 = 19.88%
    assert valuation.unrealized_return_pct == Decimal("19.88")

    # Cash = 500k deposit - 400,400 buy + 179,800 sell net = 279,400 PKR (dividends tracked separately)
    assert valuation.cash_balance.amount == Decimal("279400.0000")
    assert valuation.total_dividends.amount == Decimal("4250.0000")