from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class SecurityType(str, Enum):
    EQUITY = "EQUITY"
    MUTUAL_FUND = "MUTUAL_FUND"
    ETF = "ETF"
    SUKUK = "SUKUK"
    BOND = "BOND"


class SecuritySector(str, Enum):
    COMMERCIAL_BANKS = "Commercial Banks"
    OIL_AND_GAS_EXPLORATION = "Oil & Gas Exploration Companies"
    OIL_AND_GAS_MARKETING = "Oil & Gas Marketing Companies"
    FERTILIZER = "Fertilizer"
    CEMENT = "Cement"
    TECHNOLOGY_AND_COMMUNICATION = "Technology & Communication"
    POWER_GENERATION_AND_DISTRIBUTION = "Power Generation & Distribution"
    CHEMICAL = "Chemical"
    PHARMACEUTICALS = "Pharmaceuticals"
    AUTOMOBILE_ASSEMBLER = "Automobile Assembler"
    FOOD_AND_PERSONAL_CARE = "Food & Personal Care Products"
    TEXTILE_COMPOSITE = "Textile Composite"
    REFINERY = "Refinery"
    MISCELLANEOUS = "Miscellaneous"


@dataclass
class Security:
    """Pure domain entity representing a listed security on PSX."""

    symbol: str
    name: str
    sector: str = SecuritySector.MISCELLANEOUS.value
    security_type: SecurityType = SecurityType.EQUITY
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", self.symbol.upper().strip())