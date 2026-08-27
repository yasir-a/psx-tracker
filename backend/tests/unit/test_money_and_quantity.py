from __future__ import annotations

from decimal import Decimal
import pytest

from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_money_arithmetic_and_immutability() -> None:
    m1 = Money(Decimal("100.50"), "PKR")
    m2 = Money(Decimal("49.50"), "PKR")

    # Add
    assert (m1 + m2).amount == Decimal("150.00")
    # Sub
    assert (m1 - m2).amount == Decimal("51.00")
    # Mul
    assert (m1 * Decimal("2")).amount == Decimal("201.00")
    # Div
    assert (m1 / Decimal("2")).round(2).amount == Decimal("50.25")


def test_money_disallows_floats() -> None:
    with pytest.raises(TypeError):
        Money(100.50, "PKR")  # type: ignore[arg-type]


def test_money_currency_mismatch() -> None:
    m1 = Money(Decimal("100.00"), "PKR")
    m2 = Money(Decimal("100.00"), "USD")
    with pytest.raises(ValueError):
        _ = m1 + m2


def test_quantity_arithmetic() -> None:
    q1 = Quantity(Decimal("100"))
    q2 = Quantity(Decimal("50"))

    assert (q1 + q2).value == Decimal("150")
    assert (q1 - q2).value == Decimal("50")
    assert (q1 * 2).value == Decimal("200")
    assert (q1 / 2).value == Decimal("50")