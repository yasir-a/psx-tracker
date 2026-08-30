from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Sequence
from src.domain.market.provider_interface import IMarketDataProvider
from src.domain.market.quote import HistoricalPrice, MarketQuote
from src.domain.market.security import Security, SecuritySector
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
    Security("EFERT", "Engro Fertilizers Limited", SecuritySector.FERTILIZER.value),
    Security("UBL", "United Bank Limited", SecuritySector.COMMERCIAL_BANKS.value),
    Security("BAFL", "Bank Alfalah Limited", SecuritySector.COMMERCIAL_BANKS.value),
    Security("MARI", "Mari Petroleum Company Limited", SecuritySector.OIL_AND_GAS_EXPLORATION.value),
    Security("PPL", "Pakistan Petroleum Limited", SecuritySector.OIL_AND_GAS_EXPLORATION.value),
    Security("DGKC", "D.G. Khan Cement Company Limited", SecuritySector.CEMENT.value),
    Security("FCCL", "Fauji Cement Company Limited", SecuritySector.CEMENT.value),
    Security("MLCF", "Maple Leaf Cement Factory Limited", SecuritySector.CEMENT.value),
    Security("ATRL", "Attock Refinery Limited", SecuritySector.REFINERY.value),
    Security("PRL", "Pakistan Refinery Limited", SecuritySector.REFINERY.value),
    Security("NRL", "National Refinery Limited", SecuritySector.REFINERY.value),
    Security("ILP", "Interloop Limited", SecuritySector.TEXTILE_COMPOSITE.value),
    Security("NML", "Nishat Mills Limited", SecuritySector.TEXTILE_COMPOSITE.value),
    Security("NATF", "National Foods Limited", SecuritySector.FOOD_AND_PERSONAL_CARE.value),
    Security("NESTLE", "Nestle Pakistan Limited", SecuritySector.FOOD_AND_PERSONAL_CARE.value),
    Security("LOTCHEM", "Lotte Chemical Pakistan Limited", SecuritySector.CHEMICAL.value),
    Security("EPCL", "Engro Polymer & Chemicals Limited", SecuritySector.CHEMICAL.value),
    Security("AIRLINK", "Air Link Communication Limited", SecuritySector.TECHNOLOGY_AND_COMMUNICATION.value),
    Security("TRG", "TRG Pakistan Limited", SecuritySector.TECHNOLOGY_AND_COMMUNICATION.value),
    Security("AVN", "Avanceon Limited", SecuritySector.TECHNOLOGY_AND_COMMUNICATION.value),
    Security("KAPCO", "Kot Addu Power Company Limited", SecuritySector.POWER_GENERATION_AND_DISTRIBUTION.value),
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
    "EFERT": (Decimal("172.00"), Decimal("170.50")),
    "UBL": (Decimal("280.00"), Decimal("276.00")),
    "BAFL": (Decimal("65.50"), Decimal("64.80")),
    "MARI": (Decimal("2450.00"), Decimal("2420.00")),
    "PPL": (Decimal("118.00"), Decimal("116.50")),
    "DGKC": (Decimal("85.00"), Decimal("84.20")),
    "FCCL": (Decimal("24.50"), Decimal("24.10")),
    "MLCF": (Decimal("42.00"), Decimal("41.50")),
    "ATRL": (Decimal("380.00"), Decimal("375.00")),
    "PRL": (Decimal("32.50"), Decimal("31.80")),
    "NRL": (Decimal("295.00"), Decimal("291.00")),
    "ILP": (Decimal("78.00"), Decimal("77.20")),
    "NML": (Decimal("82.00"), Decimal("81.00")),
    "NATF": (Decimal("185.00"), Decimal("183.00")),
    "NESTLE": (Decimal("7200.00"), Decimal("7150.00")),
    "LOTCHEM": (Decimal("21.50"), Decimal("21.20")),
    "EPCL": (Decimal("38.00"), Decimal("37.60")),
    "AIRLINK": (Decimal("120.00"), Decimal("118.50")),
    "TRG": (Decimal("54.00"), Decimal("53.20")),
    "AVN": (Decimal("62.00"), Decimal("61.00")),
    "KAPCO": (Decimal("34.50"), Decimal("34.10")),
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
        return {s.upper().strip(): self.get_quote(s) for s in symbols if self.get_quote(s) is not None}

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        sym = symbol.upper().strip()
        base_price = _MOCK_BASE_PRICES.get(sym, (Decimal("100.00"), Decimal("98.00")))[0]
        results: list[HistoricalPrice] = []
        curr = start_date

        while curr <= end_date:
            if curr.weekday() < 5:  # Monday to Friday
                results.append(
                    HistoricalPrice(
                        symbol=sym,
                        trade_date=curr,
                        open_price=Money(base_price, "PKR"),
                        high_price=Money(base_price, "PKR"),
                        low_price=Money(base_price, "PKR"),
                        close_price=Money(base_price, "PKR"),
                        volume=100000,
                    )
                )
            curr += timedelta(days=1)

        return results