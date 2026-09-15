from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.accounting.transaction import Transaction
from src.domain.accounting.transaction_type import TransactionType

from src.api.errors import ValidationError
from src.domain.repositories.portfolio_repository import IPortfolioRepository
from src.domain.repositories.transaction_repository import ITransactionRepository
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


class TransactionImportService:
    """Validates and imports transaction history CSV dumps atomically."""

    def __init__(
        self,
        portfolio_repo: IPortfolioRepository,
        transaction_repo: ITransactionRepository,
    ) -> None:
        self._portfolio_repo = portfolio_repo
        self._tx_repo = transaction_repo

    def import_from_csv(self, portfolio_id: UUID, csv_text: str) -> dict[str, Any]:
        portfolio = self._portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValidationError("Portfolio not found")

        reader = csv.reader(io.StringIO(csv_text.strip()))
        rows = list(reader)
        if not rows or len(rows) < 2:
            raise ValidationError("CSV file is empty or missing data rows")

        # 1. Header mapping (case-insensitive, whitespace-trimmed)
        raw_headers = [h.strip().lower() for h in rows[0]]
        col_map = self._map_headers(raw_headers)

        # 2. Parse and validate each row
        parsed_entries: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for idx, row in enumerate(rows[1:], start=2):
            if not row or all(not cell.strip() for cell in row):
                continue

            try:
                entry = self._parse_row(row, col_map, idx)
                parsed_entries.append(entry)
            except ValidationError as ve:
                errors.append({"row": idx, "error": str(ve)})

        if errors:
            raise ValidationError(
                f"Validation failed on {len(errors)} rows. No transactions were imported.",
                details={"errors": errors},
            )

        if not parsed_entries:
            raise ValidationError("No valid transactions found in file.")

        # 3. Sort chronologically by execution date, with intraday priority
        # (Deposits & Buys before Sells on the same day)
        type_priority = {
            TransactionType.CASH_DEPOSIT: 1,
            TransactionType.BUY: 2,
            TransactionType.BONUS_SHARES: 2,
            TransactionType.RIGHT_SHARES: 2,
            TransactionType.TRANSFER_IN: 2,
            TransactionType.DIVIDEND_CASH: 3,
            TransactionType.FEE: 4,
            TransactionType.SELL: 5,
            TransactionType.TRANSFER_OUT: 5,
            TransactionType.CASH_WITHDRAWAL: 6,
        }
        parsed_entries.sort(key=lambda x: (x["executed_at"], type_priority.get(x["transaction_type"], 99)))

        # 4. FIFO Inventory Simulation: verify SELL transactions don't exceed held shares
        existing_txs = list(self._tx_repo.get_by_portfolio_id(portfolio_id))
        all_txs_simulation = list(existing_txs)

        for entry in parsed_entries:
            tx = Transaction(
                portfolio_id=portfolio_id,
                transaction_type=entry["transaction_type"],
                symbol=entry["symbol"],
                quantity=Quantity(entry["quantity"]),
                price_per_share=Money(entry["price_per_share"], "Rs."),
                brokerage_fee=Money(entry["brokerage_fee"], "Rs."),
                regulatory_fee=Money(entry["regulatory_fee"], "Rs."),
                executed_at=entry["executed_at"],
                notes=entry["notes"],
            )

            if tx.transaction_type in (TransactionType.SELL, TransactionType.TRANSFER_OUT):
                val = PortfolioReplayer.replay(all_txs_simulation)
                holding = val.holdings.get(tx.symbol or "")
                available = holding.quantity.value if holding else Decimal("0")
                if available < tx.quantity.value:
                    raise ValidationError(
                        f"Row {entry['row_num']}: Insufficient shares for {tx.symbol}. "
                        f"Requested sell {tx.quantity.value}, but only {available} available at {tx.executed_at.date()}."
                    )

            all_txs_simulation.append(tx)

        # 5. Atomic persistence & Cash balance update
        total_cash_impact = Decimal("0")
        saved_count = 0

        for entry in parsed_entries:
            tx = Transaction(
                portfolio_id=portfolio_id,
                transaction_type=entry["transaction_type"],
                symbol=entry["symbol"],
                quantity=Quantity(entry["quantity"]),
                price_per_share=Money(entry["price_per_share"], "Rs."),
                brokerage_fee=Money(entry["brokerage_fee"], "Rs."),
                regulatory_fee=Money(entry["regulatory_fee"], "Rs."),
                executed_at=entry["executed_at"],
                notes=entry["notes"],
            )
            self._tx_repo.save(tx)
            saved_count += 1

            if tx.transaction_type in (
                TransactionType.BUY,
                TransactionType.SELL,
                TransactionType.CASH_DEPOSIT,
                TransactionType.CASH_WITHDRAWAL,
                TransactionType.FEE,
            ):
                total_cash_impact += tx.net_amount.amount

        # Update cash balance safely with Decimal('0') fallback
        current_cash = portfolio.cash_balance.amount if (portfolio and portfolio.cash_balance) else Decimal("0")
        new_cash = current_cash + total_cash_impact
        self._portfolio_repo.update_cash_balance(portfolio_id, new_cash)

        return {
            "imported_count": saved_count,
            "portfolio_id": str(portfolio_id),
            "new_cash_balance": float(new_cash),
        }

    def _map_headers(self, headers: list[str]) -> dict[str, int]:
        col_map: dict[str, int] = {}
        for idx, h in enumerate(headers):
            if "date" in h:
                col_map["date"] = idx
            elif "type" in h:
                col_map["type"] = idx
            elif "symbol" in h or "ticker" in h:
                col_map["symbol"] = idx
            elif "qty" in h or "quantity" in h or "shares" in h:
                col_map["quantity"] = idx
            elif "price" in h or "rate" in h or "dps" in h:
                col_map["price"] = idx
            elif "fee" in h or "charges" in h or "tax" in h:
                col_map["fees"] = idx
            elif "net" in h:
                col_map["net"] = idx
            elif "note" in h or "remark" in h or "desc" in h:
                col_map["notes"] = idx

        if "date" not in col_map:
            raise ValidationError("Missing required column: 'Date'")
        if "type" not in col_map:
            raise ValidationError("Missing required column: 'Type'")

        return col_map

    def _parse_row(self, row: list[str], col_map: dict[str, int], row_num: int) -> dict[str, Any]:
        def get_val(key: str, default: str = "") -> str:
            idx = col_map.get(key)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return default

        # Parse Date
        date_str = get_val("date")
        if not date_str:
            raise ValidationError("Date is required")

        parsed_date = self._parse_date(date_str)

        notes = get_val("notes")

        # Parse Type & Symbol
        raw_type = get_val("type").upper().replace(" ", "_")
        raw_sym = get_val("symbol").upper()

        if "CGT_CREDIT" in raw_type or "CGT_CREDIT" in raw_sym:
            tx_type = TransactionType.CASH_DEPOSIT
            notes = f"[CGT Credit] {notes}" if notes else "[CGT Credit] NCCPL tax credit/refund"
        elif raw_type in ("DEDUCTION", "FEE", "CHARGES"):
            tx_type = TransactionType.FEE
        else:
            try:
                tx_type = TransactionType(raw_type)
            except ValueError:
                raise ValidationError(f"Invalid transaction type: '{raw_type}'")

        # Clean Symbol
        symbol = raw_sym
        if symbol in ("CASH", "—", "-", "CGT CREDIT", "CGT_CREDIT"):
            symbol = ""

        if tx_type in (
            TransactionType.BUY,
            TransactionType.SELL,
            TransactionType.BONUS_SHARES,
            TransactionType.RIGHT_SHARES,
        ):
            if not symbol:
                raise ValidationError(f"Symbol is required for {tx_type.value}")

        # Parse Quantity
        raw_qty = get_val("quantity", "0").replace(",", "")
        try:
            quantity = Decimal(raw_qty) if raw_qty else Decimal("0")
        except Exception:
            raise ValidationError(f"Invalid quantity: '{raw_qty}'")

        if tx_type in (TransactionType.BUY, TransactionType.SELL) and quantity <= 0:
            raise ValidationError(f"Quantity must be greater than 0 for {tx_type.value}")

        # Parse Price & Fees
        raw_price = get_val("price", "0").replace(",", "")
        try:
            price = Decimal(raw_price) if raw_price else Decimal("0")
        except Exception:
            raise ValidationError(f"Invalid price: '{raw_price}'")

        raw_fees = get_val("fees", "0").replace(",", "")
        try:
            fees = Decimal(raw_fees) if raw_fees else Decimal("0")
        except Exception:
            raise ValidationError(f"Invalid fees: '{raw_fees}'")

        # For FEE transactions, map price or fees to regulatory_fee
        reg_fee = Decimal("0")
        if tx_type == TransactionType.FEE:
            fee_amount = price if price > Decimal("0") else fees
            if fee_amount <= Decimal("0"):
                raw_net = get_val("net", "0").replace(",", "").replace("-", "")
                try:
                    fee_amount = Decimal(raw_net)
                except Exception:
                    fee_amount = Decimal("0")
            reg_fee = fee_amount
            price = fee_amount

        return {
            "row_num": row_num,
            "executed_at": parsed_date,
            "transaction_type": tx_type,
            "symbol": symbol if symbol else None,
            "quantity": quantity,
            "price_per_share": price,
            "brokerage_fee": Decimal("0") if tx_type == TransactionType.FEE else fees,
            "regulatory_fee": reg_fee,
            "notes": notes if notes else None,
        }

    def _parse_date(self, s: str) -> datetime:
        clean_s = s.strip().strip('"').strip("'")
        clean_s = clean_s.split("T")[0] if "T" in clean_s else clean_s

        # Handle slash-separated dates like 9/7/2026 or 8/30/2026
        if "/" in clean_s:
            parts = clean_s.split("/")
            if len(parts) == 3:
                try:
                    p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2])
                    # If first number > 12 (e.g. 30/8/2026), it's DD/MM/YYYY
                    if p1 > 12:
                        return datetime(p3, p2, p1, 10, 0, 0, tzinfo=timezone.utc)
                    # If second number > 12 (e.g. 8/30/2026), it's MM/DD/YYYY
                    elif p2 > 12:
                        return datetime(p3, p1, p2, 10, 0, 0, tzinfo=timezone.utc)
                    else:
                        # e.g. 9/7/2026 exported from JS toLocaleDateString() is MM/DD/YYYY (Sept 7)
                        return datetime(p3, p1, p2, 10, 0, 0, tzinfo=timezone.utc)
                except Exception:
                    pass

        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(clean_s, fmt)
                return dt.replace(hour=10, minute=0, second=0, tzinfo=timezone.utc)
            except ValueError:
                continue
        raise ValidationError(f"Unsupported date format: '{s}'. Use YYYY-MM-DD or MM/DD/YYYY.")