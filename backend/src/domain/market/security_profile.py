from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class IntradayPoint:
    time: str
    price: float
    volume: int


@dataclass(frozen=True)
class SecurityQuoteDetails:
    symbol: str
    name: str
    sector: str
    current_price: float
    change: float
    change_percent: float
    open_price: float
    previous_close: float
    day_low: float
    day_high: float
    week_52_low: float
    week_52_high: float
    volume: int
    bid_price: float = 0.0
    bid_volume: int = 0
    ask_price: float = 0.0
    ask_volume: int = 0
    circuit_lower: float = 0.0
    circuit_upper: float = 0.0
    is_shariah_compliant: bool = True
    market_status: str = "REG"
    updated_at: str = ""
    chart_points: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityFundamentals:
    symbol: str
    # Earnings
    eps_annual: float
    eps_quarter: float
    eps_ytd: float
    eps_expected: float
    # P/E & Growth
    pe_annual: float
    pe_expected: float
    expected_growth_pct: float
    peg_ratio: float
    forward_peg: float
    # Margins
    gross_profit_pct: float
    operating_profit_pct: float
    net_profit_pct: float
    ebitda_pct: float
    # Returns
    roe_pct: float
    roa_pct: float
    roce_pct: float
    # Payouts
    dps_annual: float
    dps_quarter: float
    dps_interim: float
    dividend_yield_pct: float
    dividend_cover: float
    payout_ratio_pct: float


@dataclass(frozen=True)
class TechnicalSignal:
    name: str
    value: float
    signal: str  # BUY, SELL, NEUTRAL
    params: str = ""


@dataclass(frozen=True)
class SecurityTechnicals:
    symbol: str
    indicators: list[TechnicalSignal]
    pivot_points: dict[str, float]  # R3, R2, R1, PP, S1, S2, S3
    moving_averages: list[dict[str, Any]]  # SMA5, SMA15, SMA30, etc.


@dataclass(frozen=True)
class CorporateAnnouncement:
    date: str
    time: str
    title: str
    category: str
    pdf_url: str = "#"


@dataclass(frozen=True)
class CompanyExecutive:
    title: str
    name: str


@dataclass(frozen=True)
class CompanyProfile:
    symbol: str
    name: str
    sector: str
    background: str
    market_cap: float
    total_shares: int
    free_float: int
    free_float_pct: float
    executives: list[CompanyExecutive]
    address: str
    website: str
    registrar: str
    auditor: str