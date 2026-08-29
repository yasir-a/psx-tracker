from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence

from src.config import Settings, get_settings
from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import MarketQuote
from src.domain.market.security import Security
from src.domain.values.money import Money
from src.infrastructure.cache.redis_client import get_redis_client


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
        })

    def _deserialize_quote(self, data: str) -> MarketQuote:
        d = json.loads(data)
        return MarketQuote(
            symbol=d["symbol"],
            current_price=Money(Decimal(d["current_price"]), "PKR"),
            previous_close=Money(Decimal(d["previous_close"]), "PKR"),
            change=Money(Decimal(d["change"]), "PKR"),
            change_percent=Decimal(d["change_percent"]),
            volume=int(d["volume"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
        )

    def get_quote(self, symbol: str) -> MarketQuote | None:
        sym = symbol.upper().strip()
        client = get_redis_client(self._settings)

        # 1. Try Redis cache
        if client is not None:
            try:
                cached = client.get(f"mkt:quote:{sym}")
                if cached:
                    return self._deserialize_quote(cached)
            except Exception:
                pass

        # 2. Fetch from underlying provider
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

        client = get_redis_client(self._settings)
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

        # Fetch missing symbols
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