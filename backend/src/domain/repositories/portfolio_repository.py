from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.domain.entities.portfolio import CashBalance, Portfolio


class IPortfolioRepository(ABC):
    """Abstract interface for portfolio data operations."""

    @abstractmethod
    def save(self, portfolio: Portfolio) -> Portfolio:
        """Persist a new or modified portfolio."""
        pass

    @abstractmethod
    def get_by_id(self, portfolio_id: UUID) -> Portfolio | None:
        """Retrieve portfolio by UUID including cash balance."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[Portfolio]:
        """Retrieve all portfolios owned by a specific user."""
        pass

    @abstractmethod
    def get_user_portfolio_by_name(self, user_id: UUID, name: str) -> Portfolio | None:
        """Retrieve portfolio by user and name."""
        pass

    @abstractmethod
    def update_cash_balance(self, portfolio_id: UUID, new_amount: Decimal) -> CashBalance | None:
        """Update available cash balance for a portfolio."""
        pass

    @abstractmethod
    def delete(self, portfolio_id: UUID) -> bool:
        """Delete portfolio by ID."""
        pass