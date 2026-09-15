from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Sequence

from src.config import Settings, get_settings
from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import HistoricalPrice, MarketQuote
from src.domain.market.security import Security
from src.domain.values.money import Money
from src.infrastructure.cache.memory_cache import get_cache


class CachedMarketService:
    """High-throughput Redis caching decorator wrapping any IMarketDataProvider."""

    def __init__(self, provider: IMarketDataProvider, settings: Settings | None = None) -> None:
        self._provider = provider
        self._settings = settings or get_settings()

    def _serialize_quote(self, quote: MarketQuote) -> str:
        return json.dumps({
            "symbol": quote.symbol,
            "current_price": str(quote.current_price.amount),
            "previous_close": str(quote.previous_close.amount),
            "change": str(quote.change.amount),
            "change_percent": str(quote.change_percent),
            "volume": quote.volume,
            "updated_at": quote.updated_at.isoformat(),
            "status": quote.status.value,
        })

    def _deserialize_quote(self, data: str) -> MarketQuote:
        d = json.loads(data)
        return MarketQuote(
            symbol=d["symbol"],
            current_price=Money(Decimal(d["current_price"]), "Rs."),
            previous_close=Money(Decimal(d["previous_close"]), "Rs."),
            change=Money(Decimal(d["change"]), "Rs."),
            change_percent=Decimal(d["change_percent"]),
            volume=int(d["volume"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
            status=DataStatus(d.get("status", "FRESH")),
        )

    def get_quote(self, symbol: str) -> MarketQuote | None:
        sym = symbol.upper().strip()
        client = get_cache()

        if client is not None:
            try:
                cached = client.get(f"mkt:quote:{sym}")
                if cached:
                    return self._deserialize_quote(cached)
            except Exception:
                pass

        quote = self._provider.get_quote(sym)
        if quote and client is not None:
            try:
                client.setex(
                    f"mkt:quote:{sym}",
                    self._settings.MARKET_DATA_CACHE_TTL_SECONDS,
                    self._serialize_quote(quote),
                )
            except Exception:
                pass

        return quote

    def get_bulk_quotes(self, symbols: Sequence[str]) -> dict[str, MarketQuote]:
        syms = [s.upper().strip() for s in symbols]
        if not syms:
            return {}

        client = get_cache()
        quotes: dict[str, MarketQuote] = {}
        missing_symbols: list[str] = []

        if client is not None:
            try:
                keys = [f"mkt:quote:{s}" for s in syms]
                cached_values = client.mget(keys)
                for sym, val in zip(syms, cached_values):
                    if val:
                        quotes[sym] = self._deserialize_quote(val)
                    else:
                        missing_symbols.append(sym)
            except Exception:
                missing_symbols = syms
        else:
            missing_symbols = syms

        if missing_symbols:
            fetched = self._provider.get_bulk_quotes(missing_symbols)
            for sym, quote in fetched.items():
                quotes[sym] = quote
                if client is not None:
                    try:
                        client.setex(
                            f"mkt:quote:{sym}",
                            self._settings.MARKET_DATA_CACHE_TTL_SECONDS,
                            self._serialize_quote(quote),
                        )
                    except Exception:
                        pass
        return quotes

    def list_all_securities(self) -> list[Security]:
        return self._provider.list_all_securities()

    def get_security_metadata(self, symbol: str) -> Security | None:
        return self._provider.get_security_metadata(symbol)

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        return self._provider.get_historical_prices(symbol, start_date=start_date, end_date=end_date)

    def get_security_details(self, symbol: str) -> dict[str, Any]:
        """Fetch comprehensive details with 15-minute Redis cache to protect PSX from IP blocking."""
        sym = symbol.upper().strip()
        client = get_cache()

        # 1. Check Redis Cache
        if client is not None:
            try:
                cached = client.get(f"mkt:details:{sym}")
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

        # 2. Query provider (scrapes real live PSX DPS data)
        if hasattr(self._provider, "get_security_details"):
            data = self._provider.get_security_details(sym)
        else:
            from src.infrastructure.market.detailed_market_data import get_detailed_stock_intelligence
            data = get_detailed_stock_intelligence(sym)

        # 3. Store in Redis with 15-minute TTL (900 seconds)
        if client is not None and data:
            try:
                client.setex(f"mkt:details:{sym}", 900, json.dumps(data))
            except Exception:
                pass

        return data