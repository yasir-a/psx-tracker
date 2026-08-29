from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.corporate_actions.bonus import calculate_bonus_shares
from src.domain.corporate_actions.dividend import calculate_dividend
from src.domain.corporate_actions.tax_status import TaxStatus
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_corporate_actions_full_lifecycle_replay() -> None:
    portfolio_id = uuid4()
    t0 = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)

    # 1. Buy 1,000 shares ENGRO @ 300 PKR
    tx_buy = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="ENGRO",
        quantity=Quantity(Decimal("1000")),
        price_per_share=Money(Decimal("300.00")),
        brokerage_fee=Money(Decimal("300.00")),
        executed_at=t0,
    )

    # 2. 10% Bonus shares issued (100 shares @ 0 cost)
    tx_bonus = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BONUS_SHARES,
        symbol="ENGRO",
        quantity=Quantity(Decimal("100")),
        price_per_share=Money.zero("PKR"),
        executed_at=t0 + timedelta(days=30),
    )

    # 3. Cash Dividend of 5.00 PKR/sh on 1,100 shares with 15% Filer WHT
    # Gross: 1,100 * 5 = 5,500 PKR. WHT: 825 PKR. Net: 4,675 PKR
    tx_div = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.DIVIDEND_CASH,
        symbol="ENGRO",
        quantity=Quantity(Decimal("1100")),
        price_per_share=Money(Decimal("5.00")),
        brokerage_fee=Money(Decimal("825.00")),
        executed_at=t0 + timedelta(days=60),
    )

    # 4. Sell 600 shares @ 350 PKR - 200 fee
    tx_sell = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.SELL,
        symbol="ENGRO",
        quantity=Quantity(Decimal("600")),
        price_per_share=Money(Decimal("350.00")),
        brokerage_fee=Money(Decimal("200.00")),
        executed_at=t0 + timedelta(days=90),
    )

    valuation = PortfolioReplayer.replay([tx_buy, tx_bonus, tx_div, tx_sell])

    # Remaining shares = 1,100 - 600 = 500 shares (400 in Lot 1 @ 300.30/sh, 100 in Lot 2 @ 0/sh)
    holding = valuation.holdings["ENGRO"]
    assert holding.quantity.value == Decimal("500")

    # Total remaining cost basis: 400 * 300.30 = 120,120 PKR
    assert holding.total_cost_basis.amount == Decimal("120120.0000")

    # Net Dividends recorded: 5,500 gross - 825 WHT = 4,675 PKR
    assert valuation.total_dividends.amount == Decimal("4675.0000")