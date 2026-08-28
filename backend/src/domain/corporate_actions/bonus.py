from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from src.domain.values.quantity import Quantity


def calculate_bonus_shares(
    existing_shares: Quantity,
    bonus_ratio: Decimal,
) -> Quantity:
    """Calculate integer bonus shares allocated based on bonus ratio (e.g. 0.10 for 10% bonus)."""
    if not existing_shares.is_positive():
        raise ValueError("Existing shares must be greater than zero to receive bonus shares")
    if bonus_ratio <= Decimal("0"):
        raise ValueError("Bonus ratio must be greater than zero")

    allocated = (existing_shares.value * bonus_ratio).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return Quantity(allocated)