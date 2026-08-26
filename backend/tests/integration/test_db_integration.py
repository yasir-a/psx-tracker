from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session
from src.domain.entities.user import User
from src.domain.entities.portfolio import Portfolio, CashBalance
from src.infrastructure.db.repositories.pg_user_repository import PgUserRepository
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository


def test_user_repository_crud(db_session: Session) -> None:
    repo = PgUserRepository(db_session)
    user = User(
        email="test_user@example.com",
        password_hash="secret_hash",
        full_name="Tariq Khan",
    )

    # Save
    saved_user = repo.save(user)
    assert saved_user.id == user.id

    # Find by ID
    found_user = repo.get_by_id(user.id)
    assert found_user is not None
    assert found_user.email == "test_user@example.com"

    # Find by Email
    found_by_email = repo.get_by_email("test_user@example.com")
    assert found_by_email is not None
    assert found_by_email.id == user.id

    # Delete
    deleted = repo.delete(user.id)
    assert deleted is True
    assert repo.get_by_id(user.id) is None


def test_portfolio_repository_crud_with_cash(db_session: Session) -> None:
    user_repo = PgUserRepository(db_session)
    portfolio_repo = PgPortfolioRepository(db_session)

    user = user_repo.save(
        User(
            email="portfolio_owner@example.com",
            password_hash="secret_hash",
            full_name="Fatima Ali",
        )
    )

    portfolio = Portfolio(
        user_id=user.id,
        name="Dividend Portfolio",
        is_default=True,
    )
    portfolio.cash_balance = CashBalance(
        portfolio_id=portfolio.id,
        amount=Decimal("250000.0000"),
    )

    # Save portfolio with cash
    saved = portfolio_repo.save(portfolio)
    assert saved.name == "Dividend Portfolio"

    # Retrieve
    retrieved = portfolio_repo.get_by_id(portfolio.id)
    assert retrieved is not None
    assert retrieved.cash_balance is not None
    assert retrieved.cash_balance.amount == Decimal("250000.0000")

    # Update cash balance
    updated_cash = portfolio_repo.update_cash_balance(portfolio.id, Decimal("300000.0000"))
    assert updated_cash is not None
    assert updated_cash.amount == Decimal("300000.0000")

    # Get by user ID
    user_portfolios = portfolio_repo.get_by_user_id(user.id)
    assert len(user_portfolios) == 1
    assert user_portfolios[0].id == portfolio.id