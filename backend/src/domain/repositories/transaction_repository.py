from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.accounting.transaction import Transaction


class ITransactionRepository(ABC):
    """Abstract interface for Transaction repository."""

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction:
        """Persist a new transaction."""
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Retrieve transaction by ID."""
        pass

    @abstractmethod
    def get_by_portfolio_id(self, portfolio_id: UUID) -> list[Transaction]:
        """Retrieve all transactions for a portfolio ordered by execution date."""
        pass