from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.api.errors import ValidationError
from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.corporate_actions.bonus import calculate_bonus_shares
from src.domain.corporate_actions.corporate_action_type import CorporateActionType
from src.domain.corporate_actions.dividend import calculate_dividend
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
        tx_date = executed_at or datetime.now(timezone.utc)
        
        # 1. Fetch all transactions for this portfolio
        transactions = self._tx_repo.get_by_portfolio_id(portfolio_id)
        
        # 2. Filter transactions up to the dividend execution date
        prior_txs = [tx for tx in transactions if tx.executed_at <= tx_date]
        valuation = PortfolioReplayer.replay(prior_txs)
        holding = valuation.holdings.get(sym)

        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        pname = portfolio.name if portfolio else "this account"

        if not holding or not holding.quantity.is_positive():
            date_str = tx_date.strftime("%m/%d/%Y")
            raise ValidationError(
                f"'{sym}' security did not exist in {pname} on {date_str}. You can only credit dividends for shares held on or before the dividend record date."
            )

        eligible_qty = holding.quantity

        div_calc = calculate_dividend(
            shares_held=eligible_qty,
            dividend_per_share=dividend_per_share,
            tax_status=tax_status,
            custom_wht_rate=custom_wht_rate,
            zakat_deducted=zakat_deducted or Money.zero(dividend_per_share.currency),
        )

        dividend_tx = Transaction(
            portfolio_id=portfolio_id,
            transaction_type=TransactionType.DIVIDEND_CASH,
            symbol=sym,
            quantity=eligible_qty,
            price_per_share=dividend_per_share,
            regulatory_fee=div_calc.wht_amount + div_calc.zakat_amount,
            executed_at=tx_date,
            notes=f"DPS: PKR {dividend_per_share.amount} | Tax: {tax_status.value} ({div_calc.wht_rate_pct}%) | Zakat: PKR {div_calc.zakat_amount.amount}",
        )
        saved_tx = self._tx_repo.save(dividend_tx)

        return {
            "transaction_id": str(saved_tx.id),
            "symbol": sym,
            "shares_held": float(eligible_qty.value),
            "dividend_per_share": float(dividend_per_share.amount),
            "gross_dividend": float(div_calc.gross_dividend.amount),
            "wht_amount": float(div_calc.wht_amount.amount),
            "zakat_deducted": float(div_calc.zakat_amount.amount),
            "net_dividend": float(div_calc.net_dividend_credited.amount),
            "executed_at": tx_date.isoformat(),
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