from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from src.domain.market.quote import HistoricalPrice, MarketQuote
from src.domain.market.security import Security


class IMarketDataProvider(ABC):
    """Abstract interface for external PSX market data feeds."""

    @abstractmethod
    def get_security_metadata(self, symbol: str) -> Security | None:
        """Fetch metadata for a given PSX symbol."""
        pass

    @abstractmethod
    def list_all_securities(self) -> list[Security]:
        """Fetch all securities listed on PSX."""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> MarketQuote | None:
        """Fetch the latest price quote for a single symbol."""
        pass

    @abstractmethod
    def get_bulk_quotes(self, symbols: Sequence[str]) -> dict[str, MarketQuote]:
        """Fetch price quotes in bulk for multiple symbols."""
        pass

    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        """Fetch historical daily price bars for a date range."""
        pass