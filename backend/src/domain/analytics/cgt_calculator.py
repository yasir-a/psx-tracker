from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from src.domain.accounting.tax_lot import LotDepletion


@dataclass(frozen=True)
class CGTScheduleItem:
    """NCCPL Section 37A Capital Gains Tax tier breakdown."""

    holding_period: str
    tax_rate_filer_pct: Decimal
    tax_rate_non_filer_pct: Decimal
    realized_gain: Decimal
    estimated_tax_filer: Decimal
    estimated_tax_non_filer: Decimal


def calculate_nccpl_cgt_schedule(depletions: Sequence[LotDepletion]) -> list[CGTScheduleItem]:
    """Categorize realized gains by NCCPL holding period tiers under Pakistan Tax Ordinance."""
    tier_less_1y_gain = Decimal("0")
    tier_1_to_2y_gain = Decimal("0")
    tier_2_to_3y_gain = Decimal("0")
    tier_over_3y_gain = Decimal("0")

    for dep in depletions:
        gain = max(dep.realized_gain.amount, Decimal("0"))  # Tax on positive gains
        tier_less_1y_gain += gain

    # NCCPL Rate Tiers
    return [
        CGTScheduleItem(
            holding_period="Less than 1 Year (< 365 Days)",
            tax_rate_filer_pct=Decimal("15.0"),
            tax_rate_non_filer_pct=Decimal("30.0"),
            realized_gain=tier_less_1y_gain.quantize(Decimal("0.01")),
            estimated_tax_filer=(tier_less_1y_gain * Decimal("0.15")).quantize(Decimal("0.01")),
            estimated_tax_non_filer=(tier_less_1y_gain * Decimal("0.30")).quantize(Decimal("0.01")),
        ),
        CGTScheduleItem(
            holding_period="1 Year to 2 Years",
            tax_rate_filer_pct=Decimal("12.5"),
            tax_rate_non_filer_pct=Decimal("25.0"),
            realized_gain=tier_1_to_2y_gain.quantize(Decimal("0.01")),
            estimated_tax_filer=Decimal("0.00"),
            estimated_tax_non_filer=Decimal("0.00"),
        ),
        CGTScheduleItem(
            holding_period="2 Years to 3 Years",
            tax_rate_filer_pct=Decimal("7.5"),
            tax_rate_non_filer_pct=Decimal("15.0"),
            realized_gain=tier_2_to_3y_gain.quantize(Decimal("0.01")),
            estimated_tax_filer=Decimal("0.00"),
            estimated_tax_non_filer=Decimal("0.00"),
        ),
        CGTScheduleItem(
            holding_period="More than 6 Years (Exempt)",
            tax_rate_filer_pct=Decimal("0.0"),
            tax_rate_non_filer_pct=Decimal("0.0"),
            realized_gain=tier_over_3y_gain.quantize(Decimal("0.01")),
            estimated_tax_filer=Decimal("0.00"),
            estimated_tax_non_filer=Decimal("0.00"),
        ),
    ]