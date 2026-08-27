from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Union


@dataclass(frozen=True)
class Money:
    """Immutable monetary value object enforcing Decimal precision and currency safety."""

    amount: Decimal
    currency: str = "PKR"

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise TypeError("Floating point numbers are not allowed for Money amount. Use Decimal or str.")
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code (e.g., 'PKR')")
        object.__setattr__(self, "currency", self.currency.upper())

    @classmethod
    def zero(cls, currency: str = "PKR") -> Money:
        return cls(amount=Decimal("0.0000"), currency=currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: cannot operate on {self.currency} and {other.currency}")

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._ensure_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._ensure_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, scalar: Union[Decimal, int, str]) -> Money:
        if isinstance(scalar, float):
            raise TypeError("Cannot multiply Money by float. Use Decimal or int.")
        dec_scalar = Decimal(str(scalar))
        return Money(self.amount * dec_scalar, self.currency)

    def __truediv__(self, scalar: Union[Decimal, int, str]) -> Money:
        if isinstance(scalar, float):
            raise TypeError("Cannot divide Money by float. Use Decimal or int.")
        dec_scalar = Decimal(str(scalar))
        if dec_scalar == Decimal("0"):
            raise ZeroDivisionError("Cannot divide Money by zero")
        return Money(self.amount / dec_scalar, self.currency)

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __lt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def round(self, places: int = 4) -> Money:
        """Round monetary amount using ROUND_HALF_UP."""
        exponent = Decimal(10) ** -places
        rounded = self.amount.quantize(exponent, rounding=ROUND_HALF_UP)
        return Money(rounded, self.currency)

    def to_decimal(self, places: int = 4) -> Decimal:
        return self.round(places).amount

    def __str__(self) -> str:
        return f"{self.currency} {self.round(2).amount:,.2f}"