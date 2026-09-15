from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.application.services.transaction_import_service import TransactionImportService
from src.domain.entities.portfolio import Portfolio
from src.api.errors import ValidationError
from src.domain.values.money import Money


def test_import_valid_csv_stream() -> None:
    portfolio_id = uuid4()
    mock_port = Portfolio(
        id=portfolio_id,
        user_id=uuid4(),
        name="Darson Securities",
        currency="Rs.",
        cash_balance=Money(Decimal("100000.00")),
    )

    port_repo = MagicMock()
    port_repo.get_by_id.return_value = mock_port

    tx_repo = MagicMock()
    tx_repo.get_by_portfolio_id.return_value = []

    service = TransactionImportService(port_repo, tx_repo)

    csv_data = """Date,Type,Symbol,Quantity,Price per Share (Rs.),Fees (Rs.),Notes
2026-01-01,CASH_DEPOSIT,,0,200000.00,0,Capital added
2026-01-02,BUY,SYS,100,400.00,100.00,Broker buy
2026-01-05,SELL,SYS,50,450.00,50.00,Take profit
2026-01-10,FEE,,0,300.00,0,[UIN FEES] Account fee
"""

    res = service.import_from_csv(portfolio_id, csv_data)
    assert res["imported_count"] == 4
    assert tx_repo.save.call_count == 4
    assert port_repo.update_cash_balance.called


def test_import_rejects_insufficient_shares_sell() -> None:
    portfolio_id = uuid4()
    mock_port = Portfolio(
        id=portfolio_id,
        user_id=uuid4(),
        name="Darson",
        currency="Rs.",
        cash_balance=Money.zero(),
    )

    port_repo = MagicMock()
    port_repo.get_by_id.return_value = mock_port

    tx_repo = MagicMock()
    tx_repo.get_by_portfolio_id.return_value = []

    service = TransactionImportService(port_repo, tx_repo)

    # Attempting to sell 200 shares when only 100 were bought
    bad_csv = """Date,Type,Symbol,Quantity,Price per Share (Rs.),Fees (Rs.),Notes
2026-01-01,BUY,SYS,100,400.00,0,Buy order
2026-01-02,SELL,SYS,200,450.00,0,Oversell order
"""

    with pytest.raises(ValidationError) as exc:
        service.import_from_csv(portfolio_id, bad_csv)
    assert "Insufficient shares" in str(exc.value)