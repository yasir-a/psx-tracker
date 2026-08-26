from __future__ import annotations

from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.domain.entities.portfolio import CashBalance, Portfolio
from src.domain.repositories.portfolio_repository import IPortfolioRepository
from src.infrastructure.db.models.portfolio_model import CashBalanceModel, PortfolioModel


class PgPortfolioRepository(IPortfolioRepository):
    """PostgreSQL implementation of IPortfolioRepository using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: PortfolioModel) -> Portfolio:
        cash = None
        if model.cash_balance:
            cash = CashBalance(
                id=model.cash_balance.id,
                portfolio_id=model.cash_balance.portfolio_id,
                currency=model.cash_balance.currency,
                amount=model.cash_balance.amount,
                updated_at=model.cash_balance.updated_at,
            )
        return Portfolio(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            currency=model.currency,
            is_default=model.is_default,
            cash_balance=cash,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, portfolio: Portfolio) -> Portfolio:
        model = self._session.get(PortfolioModel, portfolio.id)
        if model is None:
            model = PortfolioModel(
                id=portfolio.id,
                user_id=portfolio.user_id,
                name=portfolio.name,
                description=portfolio.description,
                currency=portfolio.currency,
                is_default=portfolio.is_default,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at,
            )
            self._session.add(model)
            if portfolio.cash_balance:
                cash_model = CashBalanceModel(
                    id=portfolio.cash_balance.id,
                    portfolio_id=portfolio.id,
                    currency=portfolio.cash_balance.currency,
                    amount=portfolio.cash_balance.amount,
                    updated_at=portfolio.cash_balance.updated_at,
                )
                self._session.add(cash_model)
        else:
            model.name = portfolio.name
            model.description = portfolio.description
            model.currency = portfolio.currency
            model.is_default = portfolio.is_default
            model.updated_at = portfolio.updated_at
        self._session.flush()
        return self._to_entity(model)

    def get_by_id(self, portfolio_id: UUID) -> Portfolio | None:
        stmt = (
            select(PortfolioModel)
            .options(joinedload(PortfolioModel.cash_balance))
            .where(PortfolioModel.id == portfolio_id)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def get_by_user_id(self, user_id: UUID) -> list[Portfolio]:
        stmt = (
            select(PortfolioModel)
            .options(joinedload(PortfolioModel.cash_balance))
            .where(PortfolioModel.user_id == user_id)
            .order_by(PortfolioModel.created_at.asc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]

    def get_user_portfolio_by_name(self, user_id: UUID, name: str) -> Portfolio | None:
        stmt = (
            select(PortfolioModel)
            .options(joinedload(PortfolioModel.cash_balance))
            .where(PortfolioModel.user_id == user_id, PortfolioModel.name == name)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def update_cash_balance(self, portfolio_id: UUID, new_amount: Decimal) -> CashBalance | None:
        stmt = select(CashBalanceModel).where(CashBalanceModel.portfolio_id == portfolio_id)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model:
            model.amount = new_amount
            self._session.flush()
            return CashBalance(
                id=model.id,
                portfolio_id=model.portfolio_id,
                currency=model.currency,
                amount=model.amount,
                updated_at=model.updated_at,
            )
        return None

    def delete(self, portfolio_id: UUID) -> bool:
        model = self._session.get(PortfolioModel, portfolio_id)
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False