from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.domain.corporate_actions.tax_status import TaxStatus
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


@dataclass(frozen=True)
class DividendCalculationResult:
    """Detailed breakdown of dividend calculation, withholding tax, and net proceeds."""

    shares_held: Quantity
    dividend_per_share: Money
    gross_dividend: Money
    tax_status: TaxStatus
    wht_rate_pct: Decimal
    wht_amount: Money
    zakat_amount: Money
    net_dividend_credited: Money


def calculate_dividend(
    shares_held: Quantity,
    dividend_per_share: Money,
    tax_status: TaxStatus = TaxStatus.FILER,
    custom_wht_rate: Decimal | None = None,
    zakat_deducted: Money | None = None,
) -> DividendCalculationResult:
    """Calculate gross dividend, withholding tax, and net payout based on FBR filer/non-filer rate."""
    if not shares_held.is_positive():
        raise ValueError("Shares held must be greater than zero to receive dividends")
    if dividend_per_share.amount <= Decimal("0"):
        raise ValueError("Dividend per share must be greater than zero")

    gross = (dividend_per_share * shares_held.value).round(4)

    # Determine WHT Rate
    if tax_status == TaxStatus.CUSTOM and custom_wht_rate is not None:
        wht_rate = Decimal(str(custom_wht_rate))
    else:
        wht_rate = tax_status.default_rate

    # Calculate WHT
    wht_amt = (gross * (wht_rate / Decimal("100"))).round(4)
    zakat = zakat_deducted or Money.zero(dividend_per_share.currency)

    net_credited = (gross - wht_amt - zakat).round(4)
    if net_credited.amount < Decimal("0"):
        raise ValueError("Total deductions exceed gross dividend amount")

    return DividendCalculationResult(
        shares_held=shares_held,
        dividend_per_share=dividend_per_share,
        gross_dividend=gross,
        tax_status=tax_status,
        wht_rate_pct=wht_rate,
        wht_amount=wht_amt,
        zakat_amount=zakat,
        net_dividend_credited=net_credited,
    )