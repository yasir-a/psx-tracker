from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from src.application.services.dividend_analytics_service import DividendAnalyticsService
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.entities.portfolio import Portfolio
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_dividend_analytics_aggregation_and_yield() -> None:
    user_id = uuid4()
    portfolio_id = uuid4()

    portfolio = Portfolio(
        id=portfolio_id,
        user_id=user_id,
        name="Darson Securities",
    )

    t0 = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)

    # 1. Buy 1,000 shares of ENGRO @ 300 Rs. (Cost Basis = 300,000 Rs.)
    tx_buy_engro = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="ENGRO",
        quantity=Quantity(Decimal("1000")),
        price_per_share=Money(Decimal("300.00"), "Rs."),
        brokerage_fee=Money(Decimal("150.00"), "Rs."),
        executed_at=t0,
    )

    # 2. Buy 2,000 shares of HUBC @ 120 Rs. (Cost Basis = 240,000 Rs.)
    tx_buy_hubc = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="HUBC",
        quantity=Quantity(Decimal("2000")),
        price_per_share=Money(Decimal("120.00"), "Rs."),
        brokerage_fee=Money(Decimal("120.00"), "Rs."),
        executed_at=t0,
    )

    # 3. Dividend for ENGRO: 10 Rs. DPS on 1,000 shares
    # Gross: 10,000 Rs., WHT 15%: 1,500 Rs., Net: 8,500 Rs.
    tx_div_engro = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.DIVIDEND_CASH,
        symbol="ENGRO",
        quantity=Quantity(Decimal("1000")),
        price_per_share=Money(Decimal("10.00"), "Rs."),
        brokerage_fee=Money(Decimal("1500.00"), "Rs."),
        executed_at=t0 + timedelta(days=60),  # March 2026
    )

    # 4. Dividend for HUBC: 5 Rs. DPS on 2,000 shares
    # Gross: 10,000 Rs., WHT 15%: 1,500 Rs., Net: 8,500 Rs.
    tx_div_hubc = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.DIVIDEND_CASH,
        symbol="HUBC",
        quantity=Quantity(Decimal("2000")),
        price_per_share=Money(Decimal("5.00"), "Rs."),
        brokerage_fee=Money(Decimal("1500.00"), "Rs."),
        executed_at=t0 + timedelta(days=150),  # June 2026
    )

    all_txs = [tx_buy_engro, tx_buy_hubc, tx_div_engro, tx_div_hubc]

    # Mock database session & repositories
    mock_session = MagicMock()
    service = DividendAnalyticsService(mock_session)

    service._portfolio_repo.get_by_id = MagicMock(return_value=portfolio)
    service._portfolio_repo.get_by_user_id = MagicMock(return_value=[portfolio])
    service._tx_repo.get_by_portfolio_id = MagicMock(return_value=all_txs)
    service._security_repo.get_by_symbol = MagicMock(return_value=None)
    service._market_service.get_bulk_quotes = MagicMock(return_value={})

    # Execute analytics
    result = service.get_dividend_analytics(user_id=user_id, portfolio_id=portfolio_id)

    # Assert Summary Totals
    summary = result["summary"]
    assert summary["distribution_count"] == 2
    assert summary["total_gross_dividends"] == 20000.0
    assert summary["total_wht_deducted"] == 3000.0
    assert summary["total_net_dividends"] == 17000.0

    # Total Invested Cost: 300,150 (ENGRO) + 240,120 (HUBC) = ~540,270
    # Overall YoC % = (17,000 / 540,270) * 100 = ~3.15%
    assert summary["overall_yield_on_cost_pct"] > 0

    # Assert Stock Breakdown
    by_stock = result["by_stock"]
    assert len(by_stock) == 2
    symbols = {s["symbol"] for s in by_stock}
    assert symbols == {"ENGRO", "HUBC"}

    engro_stat = next(s for s in by_stock if s["symbol"] == "ENGRO")
    assert engro_stat["total_gross"] == 10000.0
    assert engro_stat["total_net"] == 8500.0
    assert engro_stat["total_wht"] == 1500.0
    assert engro_stat["current_shares"] == 1000.0
    # ENGRO Net (8,500) / Cost (~300,150) = ~2.83%
    assert engro_stat["yield_on_cost_pct"] > 0
    # Each stock earned 8,500 out of 17,000 (50% contribution each)
    assert engro_stat["portfolio_share_pct"] == 50.0

    # Assert Monthly Breakdown
    monthly = result["monthly_breakdown"]
    assert len(monthly) == 2
    months = {m["month"] for m in monthly}
    assert months == {3, 6}  # March and June