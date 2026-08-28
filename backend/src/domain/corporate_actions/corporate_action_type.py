from __future__ import annotations

from enum import Enum


class CorporateActionType(str, Enum):
    """Types of corporate actions on PSX."""

    CASH_DIVIDEND = "CASH_DIVIDEND"
    BONUS_SHARES = "BONUS_SHARES"
    RIGHT_SHARES = "RIGHT_SHARES"
    STOCK_SPLIT = "STOCK_SPLIT"
    REVERSE_SPLIT = "REVERSE_SPLIT"