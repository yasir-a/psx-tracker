from __future__ import annotations

from decimal import Decimal
from typing import Sequence
from uuid import uuid4

from src.domain.accounting.tax_lot import LotDepletion, LotStatus, TaxLot
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


class InsufficientHoldingsError(Exception):
    """Raised when a sell or transfer order exceeds total available open lot quantity."""
    pass


class FIFOMatcher:
    """Core FIFO (First-In, First-Out) lot matching engine for securities."""

    @staticmethod
    def create_lot_from_buy(transaction: Transaction) -> TaxLot:
        """Create a new TaxLot from a BUY, BONUS, RIGHTS, or TRANSFER_IN transaction."""
        valid_types = (
            TransactionType.BUY,
            TransactionType.BONUS_SHARES,
            TransactionType.RIGHT_SHARES,
            TransactionType.TRANSFER_IN,
        )
        if transaction.transaction_type not in valid_types:
            raise ValueError(f"Cannot create tax lot from transaction type {transaction.transaction_type}")

        if transaction.symbol is None:
            raise ValueError("Transaction must have a symbol to create a tax lot")

        # Total Cost Basis = Net Amount spent (gross + brokerage + regulatory fees)
        if transaction.transaction_type == TransactionType.TRANSFER_IN:
            total_basis = (transaction.price_per_share * transaction.quantity.value).round(4)
        else:
            total_basis = transaction.net_amount

        cost_per_share = (
            (total_basis / transaction.quantity.value).round(4)
            if transaction.quantity.is_positive()
            else Money.zero(transaction.price_per_share.currency)
        )

        return TaxLot(
            portfolio_id=transaction.portfolio_id,
            transaction_id=transaction.id,
            symbol=transaction.symbol,
            original_quantity=transaction.quantity,
            remaining_quantity=transaction.quantity,
            unit_price=transaction.price_per_share,
            total_cost_basis=total_basis,
            cost_basis_per_share=cost_per_share,
            executed_at=transaction.executed_at,
            status=LotStatus.OPEN,
        )

    @staticmethod
    def match_sell(
        sell_transaction: Transaction,
        open_lots: Sequence[TaxLot],
    ) -> tuple[list[LotDepletion], list[TaxLot]]:
        """Match a SELL or TRANSFER_OUT transaction against existing open lots in strict FIFO order."""
        valid_types = (TransactionType.SELL, TransactionType.TRANSFER_OUT)
        if sell_transaction.transaction_type not in valid_types:
            raise ValueError("FIFOMatcher.match_sell requires a SELL or TRANSFER_OUT transaction")

        remaining_to_sell = sell_transaction.quantity.value
        total_open_qty = sum((lot.remaining_quantity.value for lot in open_lots if lot.status == LotStatus.OPEN), Decimal("0"))

        if remaining_to_sell > total_open_qty:
            raise InsufficientHoldingsError(
                f"Insufficient open shares ({total_open_qty}) to fulfill transaction for {remaining_to_sell} shares"
            )

        depletions: list[LotDepletion] = []
        updated_lots: list[TaxLot] = []

        # Sort lots strictly by executed_at (FIFO order)
        sorted_lots = sorted(open_lots, key=lambda lot: lot.executed_at)

        for lot in sorted_lots:
            if remaining_to_sell <= Decimal("0"):
                if lot.remaining_quantity.is_positive():
                    updated_lots.append(lot)
                continue

            available_in_lot = lot.remaining_quantity.value

            if available_in_lot <= remaining_to_sell:
                # Fully deplete this lot
                depleted_qty = available_in_lot
                remaining_to_sell -= depleted_qty
                cost_basis_depleted = (lot.cost_basis_per_share * depleted_qty).round(4)

                lot.remaining_quantity = Quantity.zero()
                lot.status = LotStatus.CLOSED
            else:
                # Partially deplete this lot
                depleted_qty = remaining_to_sell
                remaining_to_sell = Decimal("0")
                cost_basis_depleted = (lot.cost_basis_per_share * depleted_qty).round(4)

                lot.remaining_quantity = Quantity(available_in_lot - depleted_qty)
                lot.status = LotStatus.OPEN
                updated_lots.append(lot)

            # Pro-rate sell fees and proceeds across depletions
            portion = depleted_qty / sell_transaction.quantity.value
            gross_proceeds = (sell_transaction.price_per_share * depleted_qty).round(4)
            allocated_fee = (sell_transaction.total_fees * portion).round(4)

            if sell_transaction.transaction_type == TransactionType.TRANSFER_OUT:
                realized_gain = Money.zero(sell_transaction.price_per_share.currency)
            else:
                realized_gain = (gross_proceeds - cost_basis_depleted - allocated_fee).round(4)

            depletion = LotDepletion(
                id=uuid4(),
                lot_id=lot.id,
                sell_transaction_id=sell_transaction.id,
                depleted_quantity=Quantity(depleted_qty),
                cost_basis_depleted=cost_basis_depleted,
                gross_proceeds=gross_proceeds,
                allocated_fee=allocated_fee,
                realized_gain=realized_gain,
                executed_at=sell_transaction.executed_at,
            )
            depletions.append(depletion)

        return depletions, updated_lots