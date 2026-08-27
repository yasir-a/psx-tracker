from __future__ import annotations

from decimal import Decimal
from src.domain.market.quote import MarketQuote
from src.domain.market.security import Security, SecuritySector
from src.domain.values.money import Money


def test_market_quote_calculations() -> None:
    curr = Money(Decimal("350.00"), "PKR")
    prev = Money(Decimal("340.00"), "PKR")
    quote = MarketQuote.create("ENGRO", curr, prev, volume=10000)

    assert quote.symbol == "ENGRO"
    assert quote.change.amount == Decimal("10.00")
    # Change %: (10 / 340) * 100 = 2.94%
    assert quote.change_percent == Decimal("2.94")


def test_security_entity_initialization() -> None:
    sec = Security("SYS", "Systems Limited", SecuritySector.TECHNOLOGY_AND_COMMUNICATION.value)
    assert sec.symbol == "SYS"
    assert sec.is_active is True
    assert sec.sector == "Technology & Communication"