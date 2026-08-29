from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping, Sequence

from src.domain.accounting.fifo_engine import FIFOMatcher
from src.domain.accounting.tax_lot import LotDepletion, TaxLot
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


@dataclass
class HoldingSnapshot:
    """Snapshot of a holding for a single security."""

    symbol: str
    quantity: Quantity
    total_cost_basis: Money
    cost_per_share: Money
    open_lots: list[TaxLot] = field(default_factory=list)


@dataclass
class PortfolioValuation:
    """Aggregated portfolio performance and holding valuation."""

    holdings: dict[str, HoldingSnapshot]
    cash_balance: Money
    total_cost_basis: Money
    total_market_value: Money
    unrealized_gain: Money
    unrealized_return_pct: Decimal
    realized_gain: Money
    total_fees_paid: Money
    total_dividends: Money
    depletions: list[LotDepletion]


class PortfolioReplayer:
    """Replays transaction history chronologically to reconstruct portfolio holdings and P&L."""

    @staticmethod
    def replay(
        transactions: Sequence[Transaction],
        current_prices: Mapping[str, Money] | None = None,
        base_currency: str = "PKR",
    ) -> PortfolioValuation:
        prices = current_prices or {}
        sorted_txs = sorted(transactions, key=lambda tx: tx.executed_at)

        open_lots_by_symbol: dict[str, list[TaxLot]] = {}
        all_depletions: list[LotDepletion] = []

        cash = Money.zero(base_currency)
        total_fees = Money.zero(base_currency)
        total_dividends = Money.zero(base_currency)
        realized_gain = Money.zero(base_currency)

        for tx in sorted_txs:
            sym = tx.symbol or ""

            if tx.transaction_type == TransactionType.CASH_DEPOSIT:
                cash = cash + tx.price_per_share
            elif tx.transaction_type == TransactionType.CASH_WITHDRAWAL:
                cash = cash - tx.price_per_share
            elif tx.transaction_type == TransactionType.DIVIDEND_CASH:
                # Track dividend income separately from trading cash balance
                total_dividends = total_dividends + (tx.gross_amount - tx.total_fees)
                total_fees = total_fees + tx.total_fees
            elif tx.transaction_type == TransactionType.FEE:
                cash = cash - tx.total_fees
                total_fees = total_fees + tx.total_fees
            elif tx.transaction_type in (
                TransactionType.BUY,
                TransactionType.BONUS_SHARES,
                TransactionType.RIGHT_SHARES,
                TransactionType.TRANSFER_IN,
            ):
                lot = FIFOMatcher.create_lot_from_buy(tx)
                open_lots_by_symbol.setdefault(sym, []).append(lot)
                if tx.transaction_type != TransactionType.TRANSFER_IN:
                    cash = cash - tx.net_amount
                total_fees = total_fees + tx.total_fees
            elif tx.transaction_type == TransactionType.TRANSFER_OUT:
                # Deplete lots without generating capital gains or modifying trading cash
                lots = open_lots_by_symbol.get(sym, [])
                depletions, updated_lots = FIFOMatcher.match_sell(tx, lots)
                open_lots_by_symbol[sym] = updated_lots
                total_fees = total_fees + tx.total_fees
            elif tx.transaction_type == TransactionType.SELL:
                lots = open_lots_by_symbol.get(sym, [])
                depletions, updated_lots = FIFOMatcher.match_sell(tx, lots)
                open_lots_by_symbol[sym] = updated_lots
                all_depletions.extend(depletions)

                for dep in depletions:
                    realized_gain = realized_gain + dep.realized_gain

                cash = cash + tx.net_amount
                total_fees = total_fees + tx.total_fees

        # Aggregate holdings
        holdings: dict[str, HoldingSnapshot] = {}
        total_cost_basis = Money.zero(base_currency)
        total_market_val = Money.zero(base_currency)

        for symbol, lots in open_lots_by_symbol.items():
            active_lots = [lot for lot in lots if lot.remaining_quantity.is_positive()]
            if not active_lots:
                continue

            total_qty_dec = sum((lot.remaining_quantity.value for lot in active_lots), Decimal("0"))
            symbol_cost_basis = sum(
                (lot.remaining_cost_basis for lot in active_lots),
                Money.zero(base_currency),
            )
            cost_per_share = (
                (symbol_cost_basis / total_qty_dec).round(4)
                if total_qty_dec > Decimal("0")
                else Money.zero(base_currency)
            )

            holdings[symbol] = HoldingSnapshot(
                symbol=symbol,
                quantity=Quantity(total_qty_dec),
                total_cost_basis=symbol_cost_basis,
                cost_per_share=cost_per_share,
                open_lots=active_lots,
            )

            total_cost_basis = total_cost_basis + symbol_cost_basis

            # Valuation
            current_price = prices.get(symbol, cost_per_share)
            symbol_market_val = (current_price * total_qty_dec).round(4)
            total_market_val = total_market_val + symbol_market_val

        unrealized_gain = total_market_val - total_cost_basis
        unrealized_return_pct = (
            (unrealized_gain.amount / total_cost_basis.amount * Decimal("100")).quantize(Decimal("0.01"))
            if total_cost_basis.amount > Decimal("0")
            else Decimal("0.00")
        )

        return PortfolioValuation(
            holdings=holdings,
            cash_balance=cash,
            total_cost_basis=total_cost_basis,
            total_market_value=total_market_val,
            unrealized_gain=unrealized_gain,
            unrealized_return_pct=unrealized_return_pct,
            realized_gain=realized_gain,
            total_fees_paid=total_fees,
            total_dividends=total_dividends,
            depletions=all_depletions,
        )