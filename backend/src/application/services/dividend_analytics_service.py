from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.domain.values.money import Money
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_security_repository import PgSecurityRepository
from src.infrastructure.db.repositories.pg_transaction_repository import PgTransactionRepository
from src.infrastructure.market.provider_factory import get_market_service


def _extract_dividend_deductions(tx: Transaction) -> tuple[Decimal, Decimal]:
    """
    Extracts (wht_amount, zakat_amount) from a DIVIDEND_CASH transaction.
    Handles transactions where WHT is in brokerage_fee or combined in regulatory_fee.
    """
    notes = tx.notes or ""
    zakat = Decimal("0")

    # 1. If explicitly separated in brokerage_fee and regulatory_fee
    if tx.brokerage_fee.amount > Decimal("0"):
        wht = tx.brokerage_fee.amount
        zakat = tx.regulatory_fee.amount
        return (wht, zakat)

    # 2. Check notes for "Zakat: Rs. <val>"
    zakat_match = re.search(r"Zakat:\s*Rs.\s*([\d\.]+)", notes)
    if zakat_match:
        try:
            zakat = Decimal(zakat_match.group(1))
        except Exception:
            zakat = Decimal("0")

    total_deduction = tx.total_fees.amount
    if total_deduction == Decimal("0"):
        total_deduction = tx.gross_amount.amount - tx.net_amount.amount

    wht = max(Decimal("0"), total_deduction - zakat)
    return (wht, zakat)


class DividendAnalyticsService:
    """Aggregates dividend events and computes yield intelligence metrics."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._tx_repo = PgTransactionRepository(session)
        self._portfolio_repo = PgPortfolioRepository(session)
        self._security_repo = PgSecurityRepository(session)
        self._market_service = get_market_service()

    def get_dividend_analytics(
        self,
        user_id: UUID,
        portfolio_id: UUID | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """
        Calculates dividend yield metrics, stock-by-stock breakdowns,
        monthly/annual timelines, and recent payout ledger.
        """
        # 1. Resolve portfolios and fetch transactions
        if portfolio_id:
            user_portfolios = [self._portfolio_repo.get_by_id(portfolio_id)]
            user_portfolios = [p for p in user_portfolios if p and p.user_id == user_id]
        else:
            user_portfolios = self._portfolio_repo.get_by_user_id(user_id)

        portfolio_map = {p.id: p.name for p in user_portfolios if p}

        all_txs: list[Transaction] = []
        for p in user_portfolios:
            if p:
                all_txs.extend(self._tx_repo.get_by_portfolio_id(p.id))

        # 2. Get current active holdings & acquisition cost via FIFO replayer
        valuation = PortfolioReplayer.replay(all_txs, {})
        current_holdings = valuation.holdings

        # Fetch live market quotes for all held and dividend-paying symbols
        all_symbols = list(
            {tx.symbol for tx in all_txs if tx.symbol and tx.transaction_type == TransactionType.DIVIDEND_CASH}
            | set(current_holdings.keys())
        )
        quotes = self._market_service.get_bulk_quotes(all_symbols) if all_symbols else {}

        # 3. Filter dividend transactions
        div_txs = [
            tx for tx in all_txs
            if tx.transaction_type == TransactionType.DIVIDEND_CASH
        ]

        if year:
            div_txs = [tx for tx in div_txs if tx.executed_at.year == year]

        # Sort dividends chronologically (newest first for distribution log)
        div_txs.sort(key=lambda t: t.executed_at, reverse=True)

        # 4. Compute Totals
        total_gross = Decimal("0")
        total_wht = Decimal("0")
        total_zakat = Decimal("0")
        total_net = Decimal("0")

        symbol_groups: dict[str, list[Transaction]] = {}
        monthly_groups: dict[tuple[int, int], Decimal] = {}
        yearly_groups: dict[int, dict[str, Decimal]] = {}

        for tx in div_txs:
            sym = tx.symbol or "UNKNOWN"
            symbol_groups.setdefault(sym, []).append(tx)

            gross = tx.gross_amount.amount
            net = tx.net_amount.amount
            wht, zakat = _extract_dividend_deductions(tx)

            total_gross += gross
            total_wht += wht
            total_zakat += zakat
            total_net += net

            # Group monthly
            month_key = (tx.executed_at.year, tx.executed_at.month)
            monthly_groups[month_key] = monthly_groups.get(month_key, Decimal("0")) + net

            # Group yearly
            y = tx.executed_at.year
            if y not in yearly_groups:
                yearly_groups[y] = {"gross": Decimal("0"), "wht": Decimal("0"), "zakat": Decimal("0"), "net": Decimal("0")}
            yearly_groups[y]["gross"] += gross
            yearly_groups[y]["wht"] += wht
            yearly_groups[y]["zakat"] += zakat
            yearly_groups[y]["net"] += net

        # 5. Build by_stock summary list
        by_stock: list[dict[str, Any]] = []
        total_invested_cost = Decimal("0")
        total_market_val = Decimal("0")

        for sym, holding in current_holdings.items():
            total_invested_cost += holding.total_cost_basis.amount
            q = quotes.get(sym)
            curr_p = q.current_price.amount if q else holding.cost_per_share.amount
            total_market_val += curr_p * holding.quantity.value

        for sym, tx_list in symbol_groups.items():
            sym_gross = sum((t.gross_amount.amount for t in tx_list), Decimal("0"))
            sym_wht = sum((_extract_dividend_deductions(t)[0] for t in tx_list), Decimal("0"))
            sym_zakat = sum((_extract_dividend_deductions(t)[1] for t in tx_list), Decimal("0"))
            sym_net = sum((t.net_amount.amount for t in tx_list), Decimal("0"))
            last_date = max((t.executed_at for t in tx_list)).isoformat()

            holding = current_holdings.get(sym)
            quote = quotes.get(sym)

            curr_shares = float(holding.quantity.value) if holding else 0.0
            invested_cost = float(holding.total_cost_basis.amount) if holding else 0.0
            curr_price = float(quote.current_price.amount) if quote else (float(holding.cost_per_share.amount) if holding else 0.0)
            curr_mkt_val = curr_shares * curr_price

            yoc_pct = round((float(sym_net) / invested_cost) * 100, 2) if invested_cost > 0 else 0.0
            curr_yield_pct = round((float(sym_net) / curr_mkt_val) * 100, 2) if curr_mkt_val > 0 else 0.0
            contribution_pct = round((float(sym_net) / float(total_net)) * 100, 2) if total_net > Decimal("0") else 0.0

            sec_meta = self._security_repo.get_by_symbol(sym)
            company_name = sec_meta.name if sec_meta and sec_meta.name else sym

            by_stock.append({
                "symbol": sym,
                "company_name": company_name,
                "payout_count": len(tx_list),
                "total_gross": float(sym_gross),
                "total_wht": float(sym_wht),
                "total_zakat": float(sym_zakat),
                "total_net": float(sym_net),
                "current_shares": curr_shares,
                "invested_cost": invested_cost,
                "current_market_value": round(curr_mkt_val, 2),
                "yield_on_cost_pct": yoc_pct,
                "current_yield_pct": curr_yield_pct,
                "portfolio_share_pct": contribution_pct,
                "last_payment_date": last_date,
            })

        by_stock.sort(key=lambda s: s["total_net"], reverse=True)

        # 6. Overall Weighted Yields
        overall_yoc = (
            round((float(total_net) / float(total_invested_cost)) * 100, 2)
            if total_invested_cost > Decimal("0")
            else 0.0
        )
        overall_curr_yield = (
            round((float(total_net) / float(total_market_val)) * 100, 2)
            if total_market_val > Decimal("0")
            else 0.0
        )

        # 7. Projected Annual Dividend
        projected_annual = Decimal("0")
        for sym, holding in current_holdings.items():
            sym_txs = [t for t in all_txs if t.symbol == sym and t.transaction_type == TransactionType.DIVIDEND_CASH]
            if sym_txs:
                now = datetime.now(timezone.utc)
                last_365_dps = sum(
                    (t.price_per_share.amount for t in sym_txs if (now - t.executed_at).days <= 365),
                    Decimal("0"),
                )
                projected_annual += last_365_dps * holding.quantity.value

        # 8. Monthly & Annual Breakdown
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        sorted_months = sorted(monthly_groups.keys())
        monthly_breakdown = [
            {
                "year": ym[0],
                "month": ym[1],
                "month_name": month_names[ym[1]],
                "net_amount": float(monthly_groups[ym]),
            }
            for ym in sorted_months
        ]

        yearly_breakdown = [
            {
                "year": y,
                "gross": float(vals["gross"]),
                "wht": float(vals["wht"]),
                "zakat": float(vals["zakat"]),
                "net": float(vals["net"]),
            }
            for y, vals in sorted(yearly_groups.items())
        ]

        # 9. Recent Distributions (latest 30)
        recent_distributions = []
        for tx in div_txs[:30]:
            wht_val, zakat_val = _extract_dividend_deductions(tx)
            recent_distributions.append({
                "id": str(tx.id),
                "executed_at": tx.executed_at.isoformat(),
                "portfolio_name": portfolio_map.get(tx.portfolio_id, "Broker Account"),
                "symbol": tx.symbol,
                "eligible_shares": float(tx.quantity.value),
                "dividend_per_share": float(tx.price_per_share.amount),
                "gross_amount": float(tx.gross_amount.amount),
                "wht_amount": float(wht_val),
                "zakat_amount": float(zakat_val),
                "net_amount": float(tx.net_amount.amount),
                "notes": tx.notes or "",
            })

        return {
            "summary": {
                "total_gross_dividends": float(total_gross),
                "total_wht_deducted": float(total_wht),
                "total_zakat_deducted": float(total_zakat),
                "total_net_dividends": float(total_net),
                "overall_yield_on_cost_pct": overall_yoc,
                "overall_current_yield_pct": overall_curr_yield,
                "distribution_count": len(div_txs),
                "projected_annual_dividend": round(float(projected_annual), 2),
            },
            "by_stock": by_stock,
            "monthly_breakdown": monthly_breakdown,
            "yearly_breakdown": yearly_breakdown,
            "recent_distributions": recent_distributions,
        }