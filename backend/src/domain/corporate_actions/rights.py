from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


@dataclass(frozen=True)
class RightsCalculationResult:
    """Breakdown of rights offering subscription."""

    eligible_shares: Quantity
    subscription_price: Money
    total_subscription_cost: Money


def calculate_rights_subscription(
    existing_shares: Quantity,
    rights_ratio: Decimal,
    subscription_price: Money,
) -> RightsCalculationResult:
    """Calculate eligible rights shares and total subscription payment."""
    if not existing_shares.is_positive():
        raise ValueError("Existing shares must be greater than zero")
    if rights_ratio <= Decimal("0"):
        raise ValueError("Rights ratio must be greater than zero")
    if subscription_price.amount <= Decimal("0"):
        raise ValueError("Subscription price must be greater than zero")

    eligible = (existing_shares.value * rights_ratio).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    total_cost = (subscription_price * eligible).round(4)

    return RightsCalculationResult(
        eligible_shares=Quantity(eligible),
        subscription_price=subscription_price,
        total_subscription_cost=total_cost,
    )