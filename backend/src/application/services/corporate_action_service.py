from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from src.api.errors import AppError, NotFoundError, ValidationError
from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.corporate_actions.bonus import calculate_bonus_shares
from src.domain.corporate_actions.corporate_action_type import CorporateActionType
from src.domain.corporate_actions.dividend import calculate_dividend
from src.domain.corporate_actions.rights import calculate_rights_subscription
from src.domain.corporate_actions.split import rebase_lots_for_split
from src.domain.corporate_actions.tax_status import TaxStatus
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity
from src.infrastructure.db.models.corporate_action_model import CorporateActionModel
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_transaction_repository import PgTransactionRepository


class CorporateActionService:
    """Application service coordinating corporate actions on portfolios."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._portfolio_repo = PgPortfolioRepository(session)
        self._tx_repo = PgTransactionRepository(session)

    def _get_holding_qty(self, portfolio_id: UUID, symbol: str) -> Quantity:
        transactions = self._tx_repo.get_by_portfolio_id(portfolio_id)
        valuation = PortfolioReplayer.replay(transactions)
        holding = valuation.holdings.get(symbol.upper().strip())
        return holding.quantity if holding else Quantity.zero()

    def apply_cash_dividend(
        self,
        portfolio_id: UUID,
        symbol: str,
        dividend_per_share: Money,
        tax_status: TaxStatus = TaxStatus.FILER,
        custom_wht_rate: Decimal | None = None,
        zakat_deducted: Money | None = None,
        executed_at: datetime | None = None,
    ) -> dict[str, Any]:
        sym = symbol.upper().strip()
        shares = self._get_holding_qty(portfolio_id, sym)
        if shares.is_zero():
            raise ValidationError(f"No active holdings of {sym} found to receive dividends")

        calc = calculate_dividend(
            shares_held=shares,
            dividend_per_share=dividend_per_share,
            tax_status=tax_status,
            custom_wht_rate=custom_wht_rate,
            zakat_deducted=zakat_deducted,
        )

        exec_time = executed_at or datetime.now(timezone.utc)

        # 1. Record Transaction in ledger
        tx = Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.DIVIDEND_CASH,
            symbol=sym,
            quantity=shares,
            price_per_share=dividend_per_share,
            brokerage_fee=calc.wht_amount,
            regulatory_fee=calc.zakat_amount,
            executed_at=exec_time,
            notes=f"Cash Dividend ({tax_status.value} {calc.wht_rate_pct}%)",
        )
        self._tx_repo.save(tx)

        # 2. Update Cash Balance
        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        if portfolio and portfolio.cash_balance:
            new_cash = portfolio.cash_balance.amount + calc.net_dividend_credited.amount
            self._portfolio_repo.update_cash_balance(portfolio_id, new_cash)

        # 3. Log Corporate Action Record
        ca_log = CorporateActionModel(
            portfolio_id=portfolio_id,
            symbol=sym,
            action_type=CorporateActionType.CASH_DIVIDEND,
            tax_status=tax_status,
            gross_amount=calc.gross_dividend.amount,
            tax_deducted=calc.wht_amount.amount,
            zakat_deducted=calc.zakat_amount.amount,
            net_amount=calc.net_dividend_credited.amount,
            quantity_adjusted=shares.value,
            executed_at=exec_time,
        )
        self._session.add(ca_log)
        self._session.flush()

        return {
            "symbol": sym,
            "shares_held": float(shares.value),
            "dividend_per_share": float(dividend_per_share.amount),
            "gross_dividend": float(calc.gross_dividend.amount),
            "wht_rate_percent": float(calc.wht_rate_pct),
            "wht_deducted": float(calc.wht_amount.amount),
            "zakat_deducted": float(calc.zakat_amount.amount),
            "net_credited": float(calc.net_dividend_credited.amount),
        }

    def apply_bonus_shares(
        self,
        portfolio_id: UUID,
        symbol: str,
        bonus_ratio: Decimal,
        executed_at: datetime | None = None,
    ) -> dict[str, Any]:
        sym = symbol.upper().strip()
        shares = self._get_holding_qty(portfolio_id, sym)
        if shares.is_zero():
            raise ValidationError(f"No active holdings of {sym} found to receive bonus shares")

        bonus_qty = calculate_bonus_shares(shares, bonus_ratio)
        exec_time = executed_at or datetime.now(timezone.utc)

        tx = Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.BONUS_SHARES,
            symbol=sym,
            quantity=bonus_qty,
            price_per_share=Money.zero("PKR"),
            executed_at=exec_time,
            notes=f"Bonus Shares ({bonus_ratio * 100}%)",
        )
        self._tx_repo.save(tx)

        ca_log = CorporateActionModel(
            portfolio_id=portfolio_id,
            symbol=sym,
            action_type=CorporateActionType.BONUS_SHARES,
            quantity_adjusted=bonus_qty.value,
            ratio=bonus_ratio,
            executed_at=exec_time,
        )
        self._session.add(ca_log)
        self._session.flush()

        return {
            "symbol": sym,
            "existing_shares": float(shares.value),
            "bonus_shares_allocated": float(bonus_qty.value),
            "new_total_shares": float(shares.value + bonus_qty.value),
        }

    def get_tax_report(self, portfolio_id: UUID, tax_year: int) -> dict[str, Any]:
        """Generate annual tax return summary under FBR Section 150."""
        transactions = self._tx_repo.get_by_portfolio_id(portfolio_id)
        div_txs = [
            tx for tx in transactions
            if tx.transaction_type == TransactionType.DIVIDEND_CASH and tx.executed_at.year == tax_year
        ]

        total_gross = sum((tx.gross_amount.amount for tx in div_txs), Decimal("0"))
        total_wht = sum((tx.brokerage_fee.amount for tx in div_txs), Decimal("0"))
        total_zakat = sum((tx.regulatory_fee.amount for tx in div_txs), Decimal("0"))
        total_net = sum((tx.net_amount.amount for tx in div_txs), Decimal("0"))

        return {
            "portfolio_id": str(portfolio_id),
            "tax_year": tax_year,
            "dividend_count": len(div_txs),
            "total_gross_dividend": float(total_gross),
            "total_withholding_tax_paid": float(total_wht),
            "total_zakat_deducted": float(total_zakat),
            "net_dividend_income": float(total_net),
        }