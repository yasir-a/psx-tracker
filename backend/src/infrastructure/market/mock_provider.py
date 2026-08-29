from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Sequence

from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import HistoricalPrice, MarketQuote
from src.domain.market.security import Security, SecuritySector, SecurityType
from src.domain.values.money import Money


_DEFAULT_PSX_SECURITIES = [
    Security("ENGRO", "Engro Corporation Limited", SecuritySector.FERTILIZER.value),
    Security("SYS", "Systems Limited", SecuritySector.TECHNOLOGY_AND_COMMUNICATION.value),
    Security("OGDC", "Oil & Gas Development Company Limited", SecuritySector.OIL_AND_GAS_EXPLORATION.value),
    Security("LUCK", "Lucky Cement Limited", SecuritySector.CEMENT.value),
    Security("HUBC", "Hub Power Company Limited", SecuritySector.POWER_GENERATION_AND_DISTRIBUTION.value),
    Security("MCB", "MCB Bank Limited", SecuritySector.COMMERCIAL_BANKS.value),
    Security("FFC", "Fauji Fertilizer Company Limited", SecuritySector.FERTILIZER.value),
    Security("HBL", "Habib Bank Limited", SecuritySector.COMMERCIAL_BANKS.value),
    Security("MEBL", "Meezan Bank Limited", SecuritySector.COMMERCIAL_BANKS.value),
    Security("PSO", "Pakistan State Oil Company Limited", SecuritySector.OIL_AND_GAS_MARKETING.value),
]

_MOCK_BASE_PRICES: dict[str, tuple[Decimal, Decimal]] = {
    "ENGRO": (Decimal("340.50"), Decimal("335.00")),
    "SYS": (Decimal("485.00"), Decimal("478.20")),
    "OGDC": (Decimal("142.80"), Decimal("140.00")),
    "LUCK": (Decimal("820.00"), Decimal("810.50")),
    "HUBC": (Decimal("138.50"), Decimal("137.00")),
    "MCB": (Decimal("210.00"), Decimal("208.50")),
    "FFC": (Decimal("552.00"), Decimal("548.00")),
    "HBL": (Decimal("125.00"), Decimal("124.50")),
    "MEBL": (Decimal("220.00"), Decimal("218.00")),
    "PSO": (Decimal("195.00"), Decimal("192.00")),
}


class MockMarketDataProvider(IMarketDataProvider):
    """Deterministic offline market data provider for development and testing."""

    def __init__(self) -> None:
        self._securities = {s.symbol: s for s in _DEFAULT_PSX_SECURITIES}

    def get_security_metadata(self, symbol: str) -> Security | None:
        sym = symbol.upper().strip()
        return self._securities.get(sym, Security(sym, f"{sym} Corporation", SecuritySector.MISCELLANEOUS.value))

    def list_all_securities(self) -> list[Security]:
        return list(self._securities.values())

    def get_quote(self, symbol: str) -> MarketQuote | None:
        sym = symbol.upper().strip()
        curr_price, prev_close = _MOCK_BASE_PRICES.get(sym, (Decimal("100.00"), Decimal("98.00")))
        return MarketQuote.create(
            symbol=sym,
            current_price=Money(curr_price, "PKR"),
            previous_close=Money(prev_close, "PKR"),
            volume=500000,
            updated_at=datetime.now(timezone.utc),
        )

    def get_bulk_quotes(self, symbols: Sequence[str]) -> dict[str, MarketQuote]:
        return {s.upper().strip(): q for s in symbols if (q := self.get_quote(s)) is not None}

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        sym = symbol.upper().strip()
        base_p, _ = _MOCK_BASE_PRICES.get(sym, (Decimal("100.00"), Decimal("98.00")))
        prices: list[HistoricalPrice] = []

        cur_date = start_date
        while cur_date <= end_date:
            # Skip weekends (approximate PSX trading days)
            if cur_date.weekday() < 5:
                prices.append(
                    HistoricalPrice(
                        symbol=sym,
                        trade_date=cur_date,
                        open_price=Money(base_p - Decimal("1.50"), "PKR"),
                        high_price=Money(base_p + Decimal("2.00"), "PKR"),
                        low_price=Money(base_p - Decimal("2.00"), "PKR"),
                        close_price=Money(base_p, "PKR"),
                        volume=150000,
                    )
                )
            cur_date += timedelta(days=1)
        return prices