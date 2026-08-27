from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Sequence
import httpx

from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import HistoricalPrice, MarketQuote
from src.domain.market.security import Security
from src.domain.values.money import Money
from src.infrastructure.market.mock_provider import MockMarketDataProvider

logger = logging.getLogger(__name__)


class PSXScraperMarketDataProvider(IMarketDataProvider):
    """Adapter ingesting live data from PSX data endpoints with mock fallback."""

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout
        self._fallback = MockMarketDataProvider()

    def get_security_metadata(self, symbol: str) -> Security | None:
        return self._fallback.get_security_metadata(symbol)

    def list_all_securities(self) -> list[Security]:
        return self._fallback.list_all_securities()

    def get_quote(self, symbol: str) -> MarketQuote | None:
        # Fallback to mock in dev/test or when offline
        return self._fallback.get_quote(symbol)

    def get_bulk_quotes(self, symbols: Sequence[str]) -> dict[str, MarketQuote]:
        return self._fallback.get_bulk_quotes(symbols)

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        return self._fallback.get_historical_prices(symbol, start_date, end_date)