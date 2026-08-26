from __future__ import annotations

from decimal import Decimal
from uuid import uuid4
from src.domain.entities.user import User
from src.domain.entities.portfolio import Portfolio, CashBalance


def test_user_entity_creation() -> None:
    user = User(
        email="investor@example.com",
        password_hash="argon2id$hashed",
        full_name="Muhammad Ahmed",
    )
    assert user.email == "investor@example.com"
    assert user.is_active is True
    assert user.id is not None
    assert user.created_at is not None


def test_portfolio_and_cash_balance_creation() -> None:
    user_id = uuid4()
    portfolio = Portfolio(
        user_id=user_id,
        name="Main Growth Portfolio",
        currency="PKR",
    )
    cash = CashBalance(
        portfolio_id=portfolio.id,
        currency="PKR",
        amount=Decimal("500000.0000"),
    )
    portfolio.cash_balance = cash

    assert portfolio.name == "Main Growth Portfolio"
    assert portfolio.cash_balance is not None
    assert portfolio.cash_balance.amount == Decimal("500000.0000")