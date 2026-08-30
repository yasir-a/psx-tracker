from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.api.errors import ForbiddenError, NotFoundError, ValidationError
from src.domain.accounting.portfolio_replayer import PortfolioReplayer, PortfolioValuation
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.entities.portfolio import Portfolio
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_transaction_repository import PgTransactionRepository
from src.infrastructure.market.provider_factory import get_market_service


class PortfolioAccountingService:
    """Application service for portfolio valuation, transaction replay, and multi-broker accounts."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._portfolio_repo = PgPortfolioRepository(session)
        self._tx_repo = PgTransactionRepository(session)
        self._market_service = get_market_service()

    def get_user_portfolios(self, user_id: UUID) -> list[dict[str, Any]]:
        portfolios = self._portfolio_repo.get_by_user_id(user_id)
        results = []

        for p in portfolios:
            txs = self._tx_repo.get_by_portfolio_id(p.id)
            replayed_valuation = PortfolioReplayer.replay(txs, {})
            current_cash = float(replayed_valuation.cash_balance.amount)

            results.append({
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "currency": p.currency,
                "is_default": p.is_default,
                "cash_balance": current_cash,
                "created_at": p.created_at.isoformat(),
            })

        return results

    def create_portfolio(
        self,
        user_id: UUID,
        name: str,
        description: str | None = None,
        is_default: bool = False,
    ) -> dict[str, Any]:
        existing = self._portfolio_repo.get_user_portfolio_by_name(user_id, name.strip())
        if existing:
            raise ValidationError(f"An account named '{name.strip()}' already exists")

        portfolio = Portfolio(
            user_id=user_id,
            name=name.strip(),
            description=description.strip() if description else None,
            is_default=is_default,
        )
        saved = self._portfolio_repo.save(portfolio)
        return {
            "id": str(saved.id),
            "name": saved.name,
            "description": saved.description,
            "currency": saved.currency,
            "is_default": saved.is_default,
        }

    def delete_portfolio(self, portfolio_id: UUID, user_id: UUID) -> None:
        self.verify_ownership(portfolio_id, user_id)
        txs = self._tx_repo.get_by_portfolio_id(portfolio_id)
        if txs:
            val = PortfolioReplayer.replay(txs, {})
            if val.holdings:
                raise ValidationError(
                    "Cannot delete this account because it contains active securities. Please transfer or sell your shares first."
                )

        self._portfolio_repo.delete(portfolio_id)

    def delete_transaction(self, portfolio_id: UUID, transaction_id: UUID, user_id: UUID) -> None:
        self.verify_ownership(portfolio_id, user_id)
        self._tx_repo.delete(transaction_id)

    def verify_ownership(self, portfolio_id: UUID, user_id: UUID) -> None:
        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise NotFoundError("Portfolio not found")
        if portfolio.user_id != user_id:
            raise ForbiddenError("You do not have access to this portfolio")

    def update_transaction(
        self,
        portfolio_id: UUID,
        transaction_id: UUID,
        user_id: UUID,
        symbol: str | None = None,
        quantity: Decimal = Decimal("0"),
        price_per_share: Decimal = Decimal("0"),
        brokerage_fee: Decimal = Decimal("0"),
        notes: str | None = None,
    ) -> dict[str, Any]:
        self.verify_ownership(portfolio_id, user_id)
        existing_tx = self._tx_repo.get_by_id(transaction_id)
        if not existing_tx or existing_tx.portfolio_id != portfolio_id:
            raise NotFoundError("Transaction not found")

        sym = symbol.upper().strip() if symbol else existing_tx.symbol
        updated_tx = Transaction(
            id=existing_tx.id,
            portfolio_id=portfolio_id,
            transaction_type=existing_tx.transaction_type,
            symbol=sym,
            quantity=Quantity(quantity) if quantity > 0 else existing_tx.quantity,
            price_per_share=Money(price_per_share, "PKR") if price_per_share > 0 else existing_tx.price_per_share,
            brokerage_fee=Money(brokerage_fee, "PKR"),
            regulatory_fee=existing_tx.regulatory_fee,
            executed_at=existing_tx.executed_at,
            notes=notes,
        )

        saved = self._tx_repo.save(updated_tx)
        return {
            "id": str(saved.id),
            "transaction_type": saved.transaction_type.value,
            "symbol": saved.symbol,
            "quantity": float(saved.quantity.value),
            "price_per_share": float(saved.price_per_share.amount),
            "brokerage_fee": float(saved.brokerage_fee.amount),
            "notes": saved.notes,
        }

    def get_portfolio_transactions(self, portfolio_id: UUID) -> list[dict[str, Any]]:
        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise NotFoundError("Portfolio not found")

        txs = self._tx_repo.get_by_portfolio_id(portfolio_id)
        return [
            {
                "id": str(tx.id),
                "portfolio_id": str(tx.portfolio_id),
                "portfolio_name": portfolio.name,
                "transaction_type": tx.transaction_type.value,
                "symbol": tx.symbol,
                "quantity": float(tx.quantity.value),
                "price_per_share": float(tx.price_per_share.amount),
                "brokerage_fee": float(tx.brokerage_fee.amount),
                "regulatory_fee": float(tx.regulatory_fee.amount),
                "gross_amount": float(tx.gross_amount.amount),
                "net_amount": float(tx.net_amount.amount),
                "executed_at": tx.executed_at.isoformat(),
                "notes": tx.notes,
            }
            for tx in txs
        ]

    def record_transaction(
        self,
        portfolio_id: UUID,
        transaction_type: TransactionType,
        symbol: str | None = None,
        quantity: Decimal = Decimal("0"),
        price_per_share: Decimal = Decimal("0"),
        brokerage_fee: Decimal = Decimal("0"),
        regulatory_fee: Decimal = Decimal("0"),
        executed_at: datetime | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        sym = symbol.upper().strip() if symbol else None
        exec_time = executed_at or datetime.now(timezone.utc)

        tx = Transaction(
            portfolio_id=portfolio_id,
            transaction_type=transaction_type,
            symbol=sym,
            quantity=Quantity(quantity),
            price_per_share=Money(price_per_share, "PKR"),
            brokerage_fee=Money(brokerage_fee, "PKR"),
            regulatory_fee=Money(regulatory_fee, "PKR"),
            executed_at=exec_time,
            notes=notes,
        )

        if transaction_type in (TransactionType.SELL, TransactionType.TRANSFER_OUT):
            existing_txs = self._tx_repo.get_by_portfolio_id(portfolio_id)
            valuation = PortfolioReplayer.replay(existing_txs)
            holding = valuation.holdings.get(sym or "")
            available_qty = holding.quantity.value if holding else Decimal("0")
            if available_qty < quantity:
                raise ValidationError(
                    f"Insufficient shares: available {available_qty}, requested {quantity}"
                )

        saved_tx = self._tx_repo.save(tx)

        if transaction_type in (
            TransactionType.BUY,
            TransactionType.SELL,
            TransactionType.CASH_DEPOSIT,
            TransactionType.CASH_WITHDRAWAL,
            TransactionType.FEE,
        ):
            portfolio = self._portfolio_repo.get_by_id(portfolio_id)
            if portfolio and portfolio.cash_balance:
                new_cash = portfolio.cash_balance.amount + tx.net_amount.amount
                self._portfolio_repo.update_cash_balance(portfolio_id, new_cash)

        return {
            "id": str(saved_tx.id),
            "portfolio_id": str(portfolio_id),
            "transaction_type": saved_tx.transaction_type.value,
            "symbol": saved_tx.symbol,
            "quantity": float(saved_tx.quantity.value),
            "price_per_share": float(saved_tx.price_per_share.amount),
            "brokerage_fee": float(saved_tx.brokerage_fee.amount),
            "regulatory_fee": float(saved_tx.regulatory_fee.amount),
            "gross_amount": float(saved_tx.gross_amount.amount),
            "net_amount": float(saved_tx.net_amount.amount),
            "executed_at": saved_tx.executed_at.isoformat(),
            "notes": saved_tx.notes,
        }

    def transfer_shares_between_portfolios(
        self,
        user_id: UUID,
        from_portfolio_id: UUID,
        to_portfolio_id: UUID,
        symbol: str,
        quantity: Decimal,
        cdc_transfer_fee: Decimal = Decimal("0"),
        notes: str | None = None,
    ) -> dict[str, Any]:
        self.verify_ownership(from_portfolio_id, user_id)
        self.verify_ownership(to_portfolio_id, user_id)

        if from_portfolio_id == to_portfolio_id:
            raise ValidationError("Source and destination portfolios cannot be the same")

        sym = symbol.upper().strip()
        from_txs = self._tx_repo.get_by_portfolio_id(from_portfolio_id)
        from_val = PortfolioReplayer.replay(from_txs)
        holding = from_val.holdings.get(sym)

        if not holding or holding.quantity.value < quantity:
            avail = holding.quantity.value if holding else Decimal("0")
            raise ValidationError(
                f"Insufficient shares of {sym} in source portfolio: available {avail}, requested {quantity}"
            )

        now = datetime.now(timezone.utc)
        effective_cost_per_share = holding.cost_per_share.amount

        from_portfolio = self._portfolio_repo.get_by_id(from_portfolio_id)
        to_portfolio = self._portfolio_repo.get_by_id(to_portfolio_id)
        to_name = to_portfolio.name if to_portfolio else "destination"
        from_name = from_portfolio.name if from_portfolio else "source"

        tx_out = Transaction(
            portfolio_id=from_portfolio_id,
            transaction_type=TransactionType.TRANSFER_OUT,
            symbol=sym,
            quantity=Quantity(quantity),
            price_per_share=Money(effective_cost_per_share, "PKR"),
            regulatory_fee=Money(cdc_transfer_fee, "PKR"),
            executed_at=now,
            notes=notes or f"Transferred to {to_name}",
        )
        self._tx_repo.save(tx_out)

        tx_in = Transaction(
            portfolio_id=to_portfolio_id,
            transaction_type=TransactionType.TRANSFER_IN,
            symbol=sym,
            quantity=Quantity(quantity),
            price_per_share=Money(effective_cost_per_share, "PKR"),
            executed_at=now,
            notes=notes or f"Transferred from {from_name}",
        )
        self._tx_repo.save(tx_in)

        return {
            "symbol": sym,
            "quantity_transferred": float(quantity),
            "effective_cost_per_share": float(effective_cost_per_share),
            "from_portfolio_id": str(from_portfolio_id),
            "to_portfolio_id": str(to_portfolio_id),
            "cdc_fee": float(cdc_transfer_fee),
        }

    def get_portfolio_valuation(self, portfolio_id: UUID) -> dict[str, Any]:
        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise NotFoundError("Portfolio not found")

        transactions = self._tx_repo.get_by_portfolio_id(portfolio_id)
        return self._compute_valuation_response(portfolio.id, portfolio.name, portfolio.currency, transactions)

    def get_consolidated_valuation(self, user_id: UUID) -> dict[str, Any]:
        portfolios = self._portfolio_repo.get_by_user_id(user_id)
        all_transactions: list[Transaction] = []

        for p in portfolios:
            all_transactions.extend(self._tx_repo.get_by_portfolio_id(p.id))

        return self._compute_valuation_response(
            None,
            "All Accounts (Consolidated)",
            "PKR",
            all_transactions,
            is_consolidated=True,
            account_count=len(portfolios),
        )

    def _compute_valuation_response(
        self,
        portfolio_id: UUID | None,
        name: str,
        currency: str,
        transactions: list[Transaction],
        is_consolidated: bool = False,
        account_count: int = 1,
    ) -> dict[str, Any]:
        symbols = list({tx.symbol for tx in transactions if tx.symbol})
        quotes = self._market_service.get_bulk_quotes(symbols) if symbols else {}
        market_prices = {s: q.current_price for s, q in quotes.items()}

        valuation: PortfolioValuation = PortfolioReplayer.replay(transactions, market_prices)
        total_portfolio_val = valuation.total_market_value + valuation.cash_balance

        holdings_list = []
        for sym, h in valuation.holdings.items():
            quote = quotes.get(sym)
            curr_price = float(quote.current_price.amount) if quote else float(h.cost_per_share.amount)
            market_val = curr_price * float(h.quantity.value)
            cost_basis = float(h.total_cost_basis.amount)
            unrealized = market_val - cost_basis
            unrealized_pct = ((unrealized / cost_basis) * 100) if cost_basis > 0 else 0.0
            day_change = float(quote.change.amount) if quote else 0.0
            day_change_pct = float(quote.change_percent) if quote else 0.0

            lots_data = [
                {
                    "lot_id": str(lot.id),
                    "original_quantity": float(lot.original_quantity.value),
                    "remaining_quantity": float(lot.remaining_quantity.value),
                    "unit_price": float(lot.unit_price.amount),
                    "cost_basis_per_share": float(lot.cost_basis_per_share.amount),
                    "remaining_cost_basis": float(lot.remaining_cost_basis.amount),
                    "status": lot.status.value,
                    "executed_at": lot.executed_at.isoformat(),
                }
                for lot in h.open_lots
            ]

            holdings_list.append({
                "symbol": sym,
                "quantity": float(h.quantity.value),
                "cost_per_share": float(h.cost_per_share.amount),
                "total_cost_basis": cost_basis,
                "current_price": curr_price,
                "market_value": market_val,
                "unrealized_gain": unrealized,
                "unrealized_return_pct": unrealized_pct,
                "day_change": day_change,
                "day_change_pct": day_change_pct,
                "open_lots": lots_data,
            })

        return {
            "portfolio": {
                "id": str(portfolio_id) if portfolio_id else "consolidated",
                "name": name,
                "currency": currency,
                "is_consolidated": is_consolidated,
                "account_count": account_count,
            },
            "summary": {
                "total_portfolio_value": float(total_portfolio_val.amount),
                "total_stock_value": float(valuation.total_market_value.amount),
                "total_cost_basis": float(valuation.total_cost_basis.amount),
                "cash_balance": float(valuation.cash_balance.amount),
                "unrealized_gain": float(valuation.unrealized_gain.amount),
                "unrealized_return_pct": float(valuation.unrealized_return_pct),
                "realized_gain": float(valuation.realized_gain.amount),
                "total_fees_paid": float(valuation.total_fees_paid.amount),
                "total_dividends_earned": float(valuation.total_dividends.amount),
            },
            "holdings": holdings_list,
        }