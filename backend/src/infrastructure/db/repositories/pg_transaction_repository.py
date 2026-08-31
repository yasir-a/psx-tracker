from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.repositories.transaction_repository import ITransactionRepository
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity
from src.infrastructure.db.models.transaction_model import TransactionModel


class PgTransactionRepository(ITransactionRepository):
    """PostgreSQL implementation of ITransactionRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            portfolio_id=model.portfolio_id,
            transaction_type=TransactionType(model.transaction_type),
            symbol=model.symbol,
            quantity=Quantity(model.quantity),
            price_per_share=Money(model.price_per_share),
            brokerage_fee=Money(model.brokerage_fee),
            regulatory_fee=Money(model.regulatory_fee),
            executed_at=model.executed_at,
            notes=model.notes,
            created_at=model.created_at,
        )

    def save(self, transaction: Transaction) -> Transaction:
        model = self._session.get(TransactionModel, transaction.id)
        if model is None:
            model = TransactionModel(
                id=transaction.id,
                portfolio_id=transaction.portfolio_id,
                symbol=transaction.symbol,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity.value,
                price_per_share=transaction.price_per_share.amount,
                brokerage_fee=transaction.brokerage_fee.amount,
                regulatory_fee=transaction.regulatory_fee.amount,
                executed_at=transaction.executed_at,
                notes=transaction.notes,
            )
            self._session.add(model)
        else:
            model.symbol = transaction.symbol
            model.quantity = transaction.quantity.value
            model.price_per_share = transaction.price_per_share.amount
            model.brokerage_fee = transaction.brokerage_fee.amount
            model.regulatory_fee = transaction.regulatory_fee.amount
            model.notes = transaction.notes
            model.executed_at = transaction.executed_at

        self._session.flush()
        return self._to_entity(model)

    def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        model = self._session.get(TransactionModel, transaction_id)
        return self._to_entity(model) if model else None

    def get_by_portfolio_id(self, portfolio_id: UUID) -> list[Transaction]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.portfolio_id == portfolio_id)
            .order_by(TransactionModel.executed_at.asc(), TransactionModel.created_at.asc())
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def delete(self, transaction_id: UUID) -> bool:
        model = self._session.get(TransactionModel, transaction_id)
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False