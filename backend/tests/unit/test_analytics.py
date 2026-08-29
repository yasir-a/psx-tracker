from __future__ import annotations

from decimal import Decimal
from src.domain.analytics.benchmark_engine import calculate_benchmark_metrics
from src.domain.analytics.cgt_calculator import calculate_nccpl_cgt_schedule


def test_benchmark_alpha_and_beta_calculation() -> None:
    # Portfolio Return: 22.5%, KSE-100: 14.5% => Alpha = +8.0%
    metrics = calculate_benchmark_metrics(
        portfolio_return_pct=Decimal("22.50"),
        kse100_return_pct=Decimal("14.50"),
        portfolio_volatility=Decimal("1.12"),
    )

    assert metrics.portfolio_return_pct == Decimal("22.50")
    assert metrics.kse100_return_pct == Decimal("14.50")
    assert metrics.alpha_pct == Decimal("8.00")
    assert metrics.beta == Decimal("1.12")


def test_nccpl_cgt_schedule_structure() -> None:
    schedule = calculate_nccpl_cgt_schedule([])
    assert len(schedule) == 4
    assert schedule[0].tax_rate_filer_pct == Decimal("15.0")
    assert schedule[0].tax_rate_non_filer_pct == Decimal("30.0")