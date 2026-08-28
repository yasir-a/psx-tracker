from __future__ import annotations

from decimal import Decimal
from src.domain.corporate_actions.dividend import calculate_dividend
from src.domain.corporate_actions.tax_status import TaxStatus
from src.domain.values.money import Money
from src.domain.values.quantity import Quantity


def test_filer_15_percent_wht() -> None:
    # 1,000 shares @ 10 PKR DPS = 10,000 PKR Gross
    shares = Quantity(Decimal("1000"))
    dps = Money(Decimal("10.00"), "PKR")

    res = calculate_dividend(shares, dps, tax_status=TaxStatus.FILER)

    assert res.gross_dividend.amount == Decimal("10000.0000")
    # 15% WHT = 1,500 PKR
    assert res.wht_amount.amount == Decimal("1500.0000")
    # Net = 8,500 PKR
    assert res.net_dividend_credited.amount == Decimal("8500.0000")


def test_non_filer_30_percent_wht() -> None:
    shares = Quantity(Decimal("1000"))
    dps = Money(Decimal("10.00"), "PKR")

    res = calculate_dividend(shares, dps, tax_status=TaxStatus.NON_FILER)

    assert res.gross_dividend.amount == Decimal("10000.0000")
    # 30% WHT = 3,000 PKR
    assert res.wht_amount.amount == Decimal("3000.0000")
    # Net = 7,000 PKR
    assert res.net_dividend_credited.amount == Decimal("7000.0000")


def test_custom_wht_with_zakat() -> None:
    shares = Quantity(Decimal("500"))
    dps = Money(Decimal("20.00"), "PKR")  # 10,000 PKR Gross
    zakat = Money(Decimal("250.00"), "PKR")

    res = calculate_dividend(
        shares,
        dps,
        tax_status=TaxStatus.CUSTOM,
        custom_wht_rate=Decimal("12.5"),
        zakat_deducted=zakat,
    )

    assert res.gross_dividend.amount == Decimal("10000.0000")
    # 12.5% = 1,250 PKR
    assert res.wht_amount.amount == Decimal("1250.0000")
    assert res.zakat_amount.amount == Decimal("250.0000")
    # Net = 10,000 - 1,250 - 250 = 8,500 PKR
    assert res.net_dividend_credited.amount == Decimal("8500.0000")