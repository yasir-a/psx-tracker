from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Sequence
import httpx

from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import DataStatus, HistoricalPrice, MarketQuote
from src.domain.market.security import Security, SecuritySector
from src.domain.values.money import Money
from src.infrastructure.db.repositories.pg_security_repository import PgSecurityRepository
from src.infrastructure.db.session import get_db_session

logger = logging.getLogger(__name__)


class PSXScraperMarketDataProvider(IMarketDataProvider):
    """Production adapter ingesting real live data from PSX Data Portal (dps.psx.com.pk).

    Architecture Invariants:
    1. Ingests real live price ticks from DPS endpoints.
    2. Persists successful price ticks to PostgreSQL.
    3. If PSX is down / off-hours / rate-limited, falls back to the latest valid PostgreSQL price marked STALE.
    4. NEVER silently fabricates mock prices in production.
    """

    BASE_URL = "https://dps.psx.com.pk"

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://dps.psx.com.pk/",
            },
            timeout=self._timeout,
        )

    def _get_repo(self) -> PgSecurityRepository:
        session = get_db_session()
        return PgSecurityRepository(session)

    def get_security_metadata(self, symbol: str) -> Security | None:
        repo = self._get_repo()
        sec = repo.get_by_symbol(symbol)
        if sec:
            return sec
        return Security(
            symbol=symbol.upper().strip(),
            name=f"{symbol.upper().strip()} Limited",
            sector=SecuritySector.COMMERCIAL_BANKS.value,
        )

    def list_all_securities(self) -> list[Security]:
        repo = self._get_repo()
        securities = repo.list_all(active_only=True)
        if securities:
            return securities

        try:
            resp = self._client.get("/data/market-watch")
            if resp.status_code == 200:
                data = resp.json()
                stocks = []
                for item in data.get("data", []):
                    sym = item.get("symbol") or item.get("symbol_code")
                    name = item.get("name") or sym
                    sector = item.get("sector_name") or "Equities"
                    if sym:
                        stocks.append(Security(symbol=sym, name=name, sector=sector))
                if stocks:
                    repo.save_bulk(stocks)
                    get_db_session().commit()
                    return stocks
        except Exception as e:
            logger.warning("Failed to fetch all securities from PSX market-watch: %s", str(e))
        return []

    def get_quote(self, symbol: str) -> MarketQuote | None:
        sym = symbol.upper().strip()
        repo = self._get_repo()

        try:
            # 1. Fetch live intraday time-series from PSX
            resp = self._client.get(f"/timeseries/intraday/{sym}")
            if resp.status_code == 200:
                data = resp.json()
                ticks = data.get("data", [])
                if ticks:
                    # PSX DPS returns newest tick at index 0
                    latest_tick = ticks[0]  # [timestamp, price, volume, open]
                    prev_tick = ticks[1] if len(ticks) > 1 else latest_tick

                    current_price = Decimal(str(latest_tick[1]))
                    prev_close = Decimal(str(prev_tick[1]))
                    volume = int(latest_tick[2]) if len(latest_tick) > 2 else 0

                    quote = MarketQuote.create(
                        symbol=sym,
                        current_price=Money(current_price, "PKR"),
                        previous_close=Money(prev_close, "PKR"),
                        volume=volume,
                        updated_at=datetime.now(timezone.utc),
                        status=DataStatus.FRESH,
                    )

                    # Persist to PostgreSQL historical prices
                    today = date.today()
                    open_p = Decimal(str(latest_tick[3])) if len(latest_tick) > 3 else current_price
                    all_prices = [Decimal(str(t[1])) for t in ticks if len(t) > 1]
                    high_p = max(all_prices) if all_prices else current_price
                    low_p = min(all_prices) if all_prices else current_price

                    repo.save_historical_price(
                        HistoricalPrice(
                            symbol=sym,
                            trade_date=today,
                            open_price=Money(open_p, "PKR"),
                            high_price=Money(high_p, "PKR"),
                            low_price=Money(low_p, "PKR"),
                            close_price=Money(current_price, "PKR"),
                            volume=volume,
                        )
                    )
                    get_db_session().commit()
                    return quote
        except Exception as e:
            logger.warning("PSX live quote fetch failed for %s: %s. Attempting PostgreSQL fallback.", sym, str(e))

        # 2. Resilient Fallback: Retrieve last known valid price from PostgreSQL
        fallback_quote = repo.get_latest_persisted_quote(sym)
        if fallback_quote:
            logger.info("Serving PostgreSQL persisted fallback quote for %s (STALE)", sym)
            return fallback_quote

        logger.error("No market quote or PostgreSQL price available for %s", sym)
        return None

    def get_bulk_quotes(self, symbols: Sequence[str]) -> dict[str, MarketQuote]:
        results: dict[str, MarketQuote] = {}
        for s in symbols:
            q = self.get_quote(s)
            if q is not None:
                results[s.upper().strip()] = q
        return results

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        sym = symbol.upper().strip()
        repo = self._get_repo()

        try:
            resp = self._client.get(f"/timeseries/eod/{sym}")
            if resp.status_code == 200:
                data = resp.json()
                for bar in data.get("data", []):
                    t_date = datetime.fromtimestamp(bar[0], tz=timezone.utc).date()
                    if start_date <= t_date <= end_date:
                        hp = HistoricalPrice(
                            symbol=sym,
                            trade_date=t_date,
                            open_price=Money(Decimal(str(bar[1])), "PKR"),
                            high_price=Money(Decimal(str(bar[2])), "PKR"),
                            low_price=Money(Decimal(str(bar[3])), "PKR"),
                            close_price=Money(Decimal(str(bar[4])), "PKR"),
                            volume=int(bar[5]),
                        )
                        repo.save_historical_price(hp)
                get_db_session().commit()
        except Exception as e:
            logger.warning("Failed to fetch historical prices from PSX for %s: %s", sym, str(e))

        return repo.get_historical_prices(sym, start_date=start_date, end_date=end_date)