from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from src.application.services.deduction_analytics_service import DeductionAnalyticsService
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.entities.portfolio import Portfolio
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_deduction_analytics_aggregation() -> None:
    user_id = uuid4()
    portfolio_id = uuid4()

    portfolio = Portfolio(
        id=portfolio_id,
        user_id=user_id,
        name="Darson Securities",
    )

    t0 = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)

    # 1. Trade BUY with Brokerage Fee (150 Rs.) and Regulatory Levy (30 Rs.)
    tx_trade = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.BUY,
        symbol="ENGRO",
        quantity=Quantity(Decimal("100")),
        price_per_share=Money(Decimal("300.00"), "Rs."),
        brokerage_fee=Money(Decimal("150.00"), "Rs."),
        regulatory_fee=Money(Decimal("30.00"), "Rs."),
        executed_at=t0,
    )

    # 2. Predefined Account Fee: UIN Maintenance Fee (300 Rs.)
    tx_fee = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.FEE,
        price_per_share=Money(Decimal("300.00"), "Rs."),
        executed_at=t0 + timedelta(days=15),
        notes="[UIN FEES] Annual maintenance",
    )

    # 3. Dividend with 15% Filer WHT (1,500 Rs.)
    tx_div = Transaction(
        portfolio_id=portfolio_id,
        transaction_type=TransactionType.DIVIDEND_CASH,
        symbol="ENGRO",
        quantity=Quantity(Decimal("1000")),
        price_per_share=Money(Decimal("10.00"), "Rs."),
        brokerage_fee=Money(Decimal("1500.00"), "Rs."),
        executed_at=t0 + timedelta(days=45),
    )

    all_txs = [tx_trade, tx_fee, tx_div]

    mock_session = MagicMock()
    service = DeductionAnalyticsService(mock_session)

    service._portfolio_repo.get_by_id = MagicMock(return_value=portfolio)
    service._portfolio_repo.get_by_user_id = MagicMock(return_value=[portfolio])
    service._tx_repo.get_by_portfolio_id = MagicMock(return_value=all_txs)

    result = service.get_deduction_analytics(user_id=user_id, portfolio_id=portfolio_id)

    summary = result["summary"]
    # Total = 150 (brokerage) + 30 (regulatory) + 300 (fee) + 1500 (wht) = 1,980 Rs.
    assert summary["total_deductions"] == 1980.0
    assert summary["total_brokerage_commission"] == 150.0
    assert summary["total_regulatory_fees"] == 30.0
    assert summary["total_taxes_paid"] == 1500.0
    assert summary["total_account_fees"] == 300.0

    categories = {c["category"] for c in result["by_category"]}
    assert "Brokerage Commission" in categories
    assert "Regulatory Levies (SECP/PSX)" in categories
    assert "UIN FEES" in categories
    assert "Dividend WHT (FBR Sec 150)" in categories

    assert len(result["by_account"]) == 1
    assert result["by_account"][0]["portfolio_name"] == "Darson Securities"