from __future__ import annotations

from decimal import Decimal
from typing import Sequence
from uuid import UUID

from src.domain.accounting.tax_lot import LotDepletion, LotStatus, TaxLot
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


class InsufficientHoldingsError(Exception):
    """Raised when attempting to sell more shares than currently held."""
    pass


class FIFOMatcher:
    """Pure FIFO Tax Lot Matching & Depletion Engine."""

    @staticmethod
    def create_lot_from_buy(transaction: Transaction) -> TaxLot:
        """Generate a new open TaxLot from a BUY transaction."""
        if transaction.transaction_type not in (
            TransactionType.BUY,
            TransactionType.BONUS_SHARES,
            TransactionType.RIGHT_SHARES,
        ):
            raise ValueError(f"Cannot create tax lot from transaction type {transaction.transaction_type}")

        if transaction.quantity.is_zero() or not transaction.quantity.is_positive():
            raise ValueError("Lot quantity must be greater than zero")

        if transaction.transaction_type == TransactionType.BONUS_SHARES:
            total_cost = Money.zero(transaction.price_per_share.currency)
            cost_per_share = Money.zero(transaction.price_per_share.currency)
        else:
            total_cost = (transaction.gross_amount + transaction.total_fees).round(4)
            cost_per_share = (total_cost / transaction.quantity.value).round(4)

        return TaxLot(
            id=transaction.id,
            portfolio_id=transaction.portfolio_id,
            symbol=transaction.symbol or "",
            original_quantity=transaction.quantity,
            remaining_quantity=transaction.quantity,
            unit_price=transaction.price_per_share,
            total_cost_basis=total_cost,
            cost_basis_per_share=cost_per_share,
            executed_at=transaction.executed_at,
            transaction_id=transaction.id,
            status=LotStatus.OPEN,
        )

    @staticmethod
    def match_sell(
        sell_transaction: Transaction,
        open_lots: Sequence[TaxLot],
    ) -> tuple[list[LotDepletion], list[TaxLot]]:
        """Match a SELL transaction against open tax lots in strict FIFO order."""
        if sell_transaction.transaction_type != TransactionType.SELL:
            raise ValueError("FIFOMatcher.match_sell requires a SELL transaction")

        available_qty = sum((lot.remaining_quantity.value for lot in open_lots), Decimal("0"))
        sell_qty_decimal = sell_transaction.quantity.value

        if available_qty < sell_qty_decimal:
            raise InsufficientHoldingsError(
                f"Insufficient shares for {sell_transaction.symbol}: available {available_qty}, requested {sell_qty_decimal}"
            )

        depletions: list[LotDepletion] = []
        updated_lots: list[TaxLot] = []
        unmatched_sell_qty = sell_qty_decimal

        # Sort open lots by executed_at ascending (FIFO)
        sorted_lots = sorted(open_lots, key=lambda lot: lot.executed_at)

        for lot in sorted_lots:
            if unmatched_sell_qty <= Decimal("0"):
                updated_lots.append(lot)
                continue

            lot_rem_qty = lot.remaining_quantity.value
            shares_to_deplete = min(lot_rem_qty, unmatched_sell_qty)

            # Cost basis proportion
            depleted_cost = (lot.cost_basis_per_share * shares_to_deplete).round(4)
            gross_proceeds = (sell_transaction.price_per_share * shares_to_deplete).round(4)

            # Prorated sell fees
            fee_ratio = shares_to_deplete / sell_qty_decimal
            allocated_fee = (sell_transaction.total_fees * fee_ratio).round(4)

            # Realized P&L
            realized_gain = (gross_proceeds - depleted_cost - allocated_fee).round(4)

            depletion = LotDepletion(
                lot_id=lot.id,
                sell_transaction_id=sell_transaction.id,
                depleted_quantity=Quantity(shares_to_deplete),
                cost_basis_depleted=depleted_cost,
                gross_proceeds=gross_proceeds,
                allocated_fee=allocated_fee,
                realized_gain=realized_gain,
                executed_at=sell_transaction.executed_at,
            )
            depletions.append(depletion)

            new_rem_qty = lot_rem_qty - shares_to_deplete
            lot.remaining_quantity = Quantity(new_rem_qty)
            if new_rem_qty == Decimal("0"):
                lot.status = LotStatus.CLOSED
            else:
                updated_lots.append(lot)

            unmatched_sell_qty -= shares_to_deplete

        return depletions, updated_lots