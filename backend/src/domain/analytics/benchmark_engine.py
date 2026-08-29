from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Performance comparison metrics against KSE-100 index."""

    portfolio_return_pct: Decimal
    kse100_return_pct: Decimal
    alpha_pct: Decimal
    beta: Decimal
    benchmark_name: str = "KSE-100 Index"


def calculate_benchmark_metrics(
    portfolio_return_pct: Decimal,
    kse100_return_pct: Decimal = Decimal("14.50"),  # Baseline PSX market return
    portfolio_volatility: Decimal = Decimal("1.08"),
) -> BenchmarkMetrics:
    """Calculate Alpha (excess return over market) and Beta relative to KSE-100."""
    alpha = (portfolio_return_pct - kse100_return_pct).quantize(Decimal("0.01"))
    beta = portfolio_volatility.quantize(Decimal("0.01"))

    return BenchmarkMetrics(
        portfolio_return_pct=portfolio_return_pct.quantize(Decimal("0.01")),
        kse100_return_pct=kse100_return_pct.quantize(Decimal("0.01")),
        alpha_pct=alpha,
        beta=beta,
    )