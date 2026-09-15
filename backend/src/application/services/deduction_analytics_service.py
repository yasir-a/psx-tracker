from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_transaction_repository import PgTransactionRepository


def _get_account_fee_category(notes: str | None) -> str:
    """Extracts deduction category from notes (e.g. '[UIN FEES] ...' -> 'UIN FEES')."""
    if not notes:
        return "Other Fee / Charge"
    match = re.match(r"^\[(.*?)\]", notes.strip())
    if match:
        return match.group(1).strip()
    return "Other Fee / Charge"


def _extract_dividend_deductions(tx: Transaction) -> tuple[Decimal, Decimal]:
    """Extracts (wht_amount, zakat_amount) from a DIVIDEND_CASH transaction."""
    notes = tx.notes or ""
    zakat = Decimal("0")

    if tx.brokerage_fee.amount > Decimal("0"):
        return (tx.brokerage_fee.amount, tx.regulatory_fee.amount)

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


class DeductionAnalyticsService:
    """Aggregates and analyzes all portfolio deductions, broker commissions, taxes, and levies."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._tx_repo = PgTransactionRepository(session)
        self._portfolio_repo = PgPortfolioRepository(session)

    def get_deduction_analytics(
        self,
        user_id: UUID,
        portfolio_id: UUID | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Calculates total friction, category breakdown, per-broker cost, and monthly timelines."""
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

        if year:
            all_txs = [tx for tx in all_txs if tx.executed_at.year == year]

        # Tracking accumulators
        total_brokerage = Decimal("0")
        total_regulatory = Decimal("0")
        total_taxes = Decimal("0")
        total_account_fees = Decimal("0")
        total_traded_volume = Decimal("0")

        # Category mapping: category_name -> {"count": int, "total": Decimal, "group": str, "recipient": str}
        categories: dict[str, dict[str, Any]] = {}

        # Broker mapping: portfolio_id -> {"trading": Decimal, "taxes": Decimal, "account": Decimal}
        broker_costs: dict[UUID, dict[str, Decimal]] = {
            p.id: {"trading": Decimal("0"), "taxes": Decimal("0"), "account": Decimal("0")}
            for p in user_portfolios if p
        }

        # Monthly mapping: (year, month) -> {"trading": Decimal, "taxes": Decimal, "account": Decimal, "total": Decimal}
        monthly_groups: dict[tuple[int, int], dict[str, Decimal]] = {}
        # Yearly mapping: year -> {"trading": Decimal, "taxes": Decimal, "account": Decimal, "total": Decimal}
        yearly_groups: dict[int, dict[str, Decimal]] = {}

        # Ledger records for audit trail
        ledger_records: list[dict[str, Any]] = []

        def record_fee_event(
            tx_id: str,
            exec_time: datetime,
            pid: UUID,
            cat: str,
            grp: str,
            recipient: str,
            amount: Decimal,
            symbol: str | None,
            notes: str | None,
        ) -> None:
            if amount <= Decimal("0"):
                return

            # Update category aggregation
            if cat not in categories:
                categories[cat] = {"count": 0, "total": Decimal("0"), "group": grp, "recipient": recipient}
            categories[cat]["count"] += 1
            categories[cat]["total"] += amount

            # Update broker cost
            if pid in broker_costs:
                if grp == "Trading Friction":
                    broker_costs[pid]["trading"] += amount
                elif grp == "Taxes":
                    broker_costs[pid]["taxes"] += amount
                else:
                    broker_costs[pid]["account"] += amount

            # Update monthly
            ym = (exec_time.year, exec_time.month)
            if ym not in monthly_groups:
                monthly_groups[ym] = {"trading": Decimal("0"), "taxes": Decimal("0"), "account": Decimal("0"), "total": Decimal("0")}
            if grp == "Trading Friction":
                monthly_groups[ym]["trading"] += amount
            elif grp == "Taxes":
                monthly_groups[ym]["taxes"] += amount
            else:
                monthly_groups[ym]["account"] += amount
            monthly_groups[ym]["total"] += amount

            # Update yearly
            y = exec_time.year
            if y not in yearly_groups:
                yearly_groups[y] = {"trading": Decimal("0"), "taxes": Decimal("0"), "account": Decimal("0"), "total": Decimal("0")}
            if grp == "Trading Friction":
                yearly_groups[y]["trading"] += amount
            elif grp == "Taxes":
                yearly_groups[y]["taxes"] += amount
            else:
                yearly_groups[y]["account"] += amount
            yearly_groups[y]["total"] += amount

            # Audit ledger entry
            ledger_records.append({
                "id": tx_id,
                "executed_at": exec_time.isoformat(),
                "portfolio_name": portfolio_map.get(pid, "Broker Account"),
                "category": cat,
                "group": grp,
                "recipient": recipient,
                "symbol": symbol or "—",
                "amount": float(amount),
                "notes": notes or "",
            })

        for tx in all_txs:
            # 1. Trading Fees from BUY & SELL
            if tx.transaction_type in (TransactionType.BUY, TransactionType.SELL):
                total_traded_volume += tx.gross_amount.amount

                if tx.brokerage_fee.amount > Decimal("0"):
                    total_brokerage += tx.brokerage_fee.amount
                    record_fee_event(
                        str(tx.id), tx.executed_at, tx.portfolio_id,
                        "Brokerage Commission", "Trading Friction", "Broker",
                        tx.brokerage_fee.amount, tx.symbol, tx.notes
                    )

                if tx.regulatory_fee.amount > Decimal("0"):
                    total_regulatory += tx.regulatory_fee.amount
                    record_fee_event(
                        str(tx.id), tx.executed_at, tx.portfolio_id,
                        "Regulatory Levies (SECP/PSX)", "Trading Friction", "SECP / PSX",
                        tx.regulatory_fee.amount, tx.symbol, tx.notes
                    )

            # 2. Account Deductions (FEE transactions)
            elif tx.transaction_type == TransactionType.FEE:
                fee_val = tx.total_fees.amount if tx.total_fees.amount > Decimal("0") else tx.price_per_share.amount
                cat_name = _get_account_fee_category(tx.notes)

                # Classify group and recipient
                if "CGT" in cat_name.upper():
                    grp = "Taxes"
                    recipient = "NCCPL / FBR"
                    total_taxes += fee_val
                elif "SST" in cat_name.upper():
                    grp = "Taxes"
                    recipient = "Provincial Revenue Board"
                    total_taxes += fee_val
                elif "CDC" in cat_name.upper() or "CUSTODY" in cat_name.upper():
                    grp = "Account & Custody"
                    recipient = "CDC / Broker"
                    total_account_fees += fee_val
                elif "UIN" in cat_name.upper():
                    grp = "Account & Custody"
                    recipient = "NCCPL"
                    total_account_fees += fee_val
                else:
                    grp = "Account & Custody"
                    recipient = "Broker / Bank"
                    total_account_fees += fee_val

                record_fee_event(
                    str(tx.id), tx.executed_at, tx.portfolio_id,
                    cat_name, grp, recipient,
                    fee_val, None, tx.notes
                )

            # 3. Dividend Withholding Tax & Zakat
            elif tx.transaction_type == TransactionType.DIVIDEND_CASH:
                wht, zakat = _extract_dividend_deductions(tx)

                if wht > Decimal("0"):
                    total_taxes += wht
                    record_fee_event(
                        str(tx.id), tx.executed_at, tx.portfolio_id,
                        "Dividend WHT (FBR Sec 150)", "Taxes", "FBR",
                        wht, tx.symbol, tx.notes
                    )

                if zakat > Decimal("0"):
                    total_taxes += zakat
                    record_fee_event(
                        str(tx.id), tx.executed_at, tx.portfolio_id,
                        "Zakat Deduction", "Taxes", "Zakat Fund",
                        zakat, tx.symbol, tx.notes
                    )

            # 4. Inter-Account Transfer CDC Fees
            elif tx.transaction_type == TransactionType.TRANSFER_OUT and tx.regulatory_fee.amount > Decimal("0"):
                total_account_fees += tx.regulatory_fee.amount
                record_fee_event(
                    str(tx.id), tx.executed_at, tx.portfolio_id,
                    "CDC Share Transfer Fee", "Account & Custody", "CDC",
                    tx.regulatory_fee.amount, tx.symbol, tx.notes
                )

        total_deductions = total_brokerage + total_regulatory + total_taxes + total_account_fees

        # Compute category list with percentage shares
        category_list: list[dict[str, Any]] = []
        for cat_name, cat_data in categories.items():
            amt = float(cat_data["total"])
            share = round((amt / float(total_deductions)) * 100, 2) if total_deductions > Decimal("0") else 0.0
            category_list.append({
                "category": cat_name,
                "group": cat_data["group"],
                "recipient": cat_data["recipient"],
                "count": cat_data["count"],
                "total_amount": amt,
                "share_pct": share,
            })
        category_list.sort(key=lambda c: c["total_amount"], reverse=True)

        # Compute broker breakdown
        broker_list: list[dict[str, Any]] = []
        for pid, costs in broker_costs.items():
            b_total = costs["trading"] + costs["taxes"] + costs["account"]
            if b_total > Decimal("0"):
                share = round((float(b_total) / float(total_deductions)) * 100, 2) if total_deductions > Decimal("0") else 0.0
                broker_list.append({
                    "portfolio_id": str(pid),
                    "portfolio_name": portfolio_map.get(pid, "Broker Account"),
                    "total_amount": float(b_total),
                    "trading_fees": float(costs["trading"]),
                    "taxes": float(costs["taxes"]),
                    "account_fees": float(costs["account"]),
                    "share_pct": share,
                })
        broker_list.sort(key=lambda b: b["total_amount"], reverse=True)

        # Monthly & Yearly lists
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_breakdown = [
            {
                "year": ym[0],
                "month": ym[1],
                "month_name": month_names[ym[1]],
                "trading_fees": float(data["trading"]),
                "taxes": float(data["taxes"]),
                "account_fees": float(data["account"]),
                "total_amount": float(data["total"]),
            }
            for ym, data in sorted(monthly_groups.items())
        ]

        yearly_breakdown = [
            {
                "year": y,
                "trading_fees": float(data["trading"]),
                "taxes": float(data["taxes"]),
                "account_fees": float(data["account"]),
                "total_amount": float(data["total"]),
            }
            for y, data in sorted(yearly_groups.items())
        ]

        # Fee drag percentage = (Total Fees / Total Traded Turnover) * 100
        fee_drag_pct = (
            round((float(total_deductions) / float(total_traded_volume)) * 100, 2)
            if total_traded_volume > Decimal("0")
            else 0.0
        )

        # Sort audit ledger newest first
        ledger_records.sort(key=lambda r: r["executed_at"], reverse=True)

        return {
            "summary": {
                "total_deductions": float(total_deductions),
                "total_brokerage_commission": float(total_brokerage),
                "total_regulatory_fees": float(total_regulatory),
                "total_taxes_paid": float(total_taxes),
                "total_account_fees": float(total_account_fees),
                "total_traded_volume": float(total_traded_volume),
                "fee_drag_pct": fee_drag_pct,
                "total_event_count": len(ledger_records),
            },
            "by_category": category_list,
            "by_account": broker_list,
            "monthly_breakdown": monthly_breakdown,
            "yearly_breakdown": yearly_breakdown,
            "recent_deductions": ledger_records[:50],
        }