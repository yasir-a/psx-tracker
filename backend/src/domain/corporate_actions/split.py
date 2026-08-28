from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from src.domain.accounting.tax_lot import TaxLot
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def rebase_lots_for_split(
    open_lots: Sequence[TaxLot],
    split_ratio: Decimal,
) -> list[TaxLot]:
    """Re-base open tax lots for a stock split (R > 1) or reverse split (R < 1).

    Invariant: Total cost basis for each lot remains strictly unchanged.
    """
    if split_ratio <= Decimal("0"):
        raise ValueError("Split ratio must be positive")

    rebased: list[TaxLot] = []
    for lot in open_lots:
        new_orig_qty = (lot.original_quantity.value * split_ratio).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        new_rem_qty = (lot.remaining_quantity.value * split_ratio).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # Invariant: cost basis per share = total_cost_basis / new_orig_qty
        if new_orig_qty > Decimal("0"):
            new_cost_per_share = (lot.total_cost_basis / new_orig_qty).round(4)
        else:
            new_cost_per_share = Money.zero(lot.unit_price.currency)

        new_unit_price = (lot.unit_price / split_ratio).round(4)

        lot.original_quantity = Quantity(new_orig_qty)
        lot.remaining_quantity = Quantity(new_rem_qty)
        lot.unit_price = new_unit_price
        lot.cost_basis_per_share = new_cost_per_share
        rebased.append(lot)

    return rebased