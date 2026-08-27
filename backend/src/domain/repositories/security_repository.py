from __future__ import annotations

from abc import ABC, abstractmethod
from src.domain.market.security import Security


class ISecurityRepository(ABC):
    """Abstract interface for securities catalog persistence."""

    @abstractmethod
    def save(self, security: Security) -> Security:
        """Persist or update a security."""
        pass

    @abstractmethod
    def save_bulk(self, securities: list[Security]) -> int:
        """Persist multiple securities. Returns count saved."""
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: str) -> Security | None:
        """Retrieve security by uppercase symbol."""
        pass

    @abstractmethod
    def search(self, query: str | None = None, sector: str | None = None, limit: int = 50) -> list[Security]:
        """Search securities by symbol/name and sector."""
        pass