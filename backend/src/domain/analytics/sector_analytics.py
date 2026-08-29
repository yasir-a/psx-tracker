from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from src.domain.accounting.portfolio_replayer import HoldingSnapshot
from src.domain.market.security import Security


@dataclass(frozen=True)
class SectorExposure:
    """Weight and valuation of a sector in the portfolio."""

    sector: str
    market_value: Decimal
    weight_pct: Decimal
    stock_count: int
    is_concentrated: bool  # True if sector > 35% of total stock portfolio


def calculate_sector_concentration(
    holdings: Mapping[str, HoldingSnapshot],
    securities_metadata: Mapping[str, Security],
    current_prices: Mapping[str, Decimal],
) -> list[SectorExposure]:
    """Aggregate portfolio holdings into PSX sector weightings and identify concentration risks."""
    sector_values: dict[str, Decimal] = {}
    sector_counts: dict[str, int] = {}
    total_val = Decimal("0")

    for sym, h in holdings.items():
        price = current_prices.get(sym, h.cost_per_share.amount)
        val = price * h.quantity.value
        total_val += val

        meta = securities_metadata.get(sym)
        sector_name = meta.sector if meta else "Miscellaneous / Others"

        sector_values[sector_name] = sector_values.get(sector_name, Decimal("0")) + val
        sector_counts[sector_name] = sector_counts.get(sector_name, 0) + 1

    exposures: list[SectorExposure] = []
    for sector, val in sorted(sector_values.items(), key=lambda item: item[1], reverse=True):
        weight = (val / total_val * Decimal("100")).quantize(Decimal("0.01")) if total_val > Decimal("0") else Decimal("0.00")
        is_conc = weight >= Decimal("35.00")

        exposures.append(
            SectorExposure(
                sector=sector,
                market_value=val.quantize(Decimal("0.01")),
                weight_pct=weight,
                stock_count=sector_counts[sector],
                is_concentrated=is_conc,
            )
        )

    return exposures