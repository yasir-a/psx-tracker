from __future__ import annotations

from enum import Enum


class TransactionType(str, Enum):
    """Supported ledger transaction and corporate action types."""

    BUY = "BUY"
    SELL = "SELL"
    CASH_DEPOSIT = "CASH_DEPOSIT"
    CASH_WITHDRAWAL = "CASH_WITHDRAWAL"
    DIVIDEND_CASH = "DIVIDEND_CASH"
    BONUS_SHARES = "BONUS_SHARES"
    RIGHT_SHARES = "RIGHT_SHARES"
    STOCK_SPLIT = "STOCK_SPLIT"
    FEE = "FEE"