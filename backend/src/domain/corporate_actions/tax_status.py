from __future__ import annotations

from decimal import Decimal
from enum import Enum


class TaxStatus(str, Enum):
    """Taxpayer status under Pakistan FBR income tax ordinance (Section 150)."""

    FILER = "FILER"          # 15% Withholding Tax
    NON_FILER = "NON_FILER"  # 30% Withholding Tax
    EXEMPT = "EXEMPT"        # 0% Withholding Tax
    CUSTOM = "CUSTOM"        # User defined percentage

    @property
    def default_rate(self) -> Decimal:
        if self == TaxStatus.FILER:
            return Decimal("15.0")
        elif self == TaxStatus.NON_FILER:
            return Decimal("30.0")
        return Decimal("0.0")