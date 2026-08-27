from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Quantity:
    """Immutable share/asset quantity value object."""

    value: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.value, float):
            raise TypeError("Floating point numbers are not allowed for Quantity. Use Decimal, int, or str.")
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    @classmethod
    def zero(cls) -> Quantity:
        return cls(Decimal("0.0000"))

    def __add__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        return Quantity(self.value + other.value)

    def __sub__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        return Quantity(self.value - other.value)

    def __mul__(self, scalar: Union[Decimal, int, str]) -> Quantity:
        if isinstance(scalar, float):
            raise TypeError("Cannot multiply Quantity by float.")
        return Quantity(self.value * Decimal(str(scalar)))

    def __truediv__(self, scalar: Union[Decimal, int, str]) -> Quantity:
        if isinstance(scalar, float):
            raise TypeError("Cannot divide Quantity by float.")
        dec_scalar = Decimal(str(scalar))
        if dec_scalar == Decimal("0"):
            raise ZeroDivisionError("Cannot divide Quantity by zero")
        return Quantity(self.value / dec_scalar)

    def __lt__(self, other: Quantity) -> bool:
        return self.value < other.value

    def __le__(self, other: Quantity) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Quantity) -> bool:
        return self.value > other.value

    def __ge__(self, other: Quantity) -> bool:
        return self.value >= other.value

    def is_zero(self) -> bool:
        return self.value == Decimal("0")

    def is_positive(self) -> bool:
        return self.value > Decimal("0")

    def to_decimal(self, places: int = 4) -> Decimal:
        exponent = Decimal(10) ** -places
        return self.value.quantize(exponent, rounding=ROUND_HALF_UP)

    def to_int(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        return f"{self.to_decimal(2):,}"