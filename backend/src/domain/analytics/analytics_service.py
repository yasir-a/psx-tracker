from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.api.errors import NotFoundError
from src.domain.accounting.portfolio_replayer import PortfolioReplayer
from src.domain.analytics.benchmark_engine import calculate_benchmark_metrics
from src.domain.analytics.cgt_calculator import calculate_nccpl_cgt_schedule
from src.domain.analytics.sector_analytics import calculate_sector_concentration
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_transaction_repository import PgTransactionRepository
from src.infrastructure.market.provider_factory import get_market_service


class AnalyticsService:
    """Application service for portfolio analytics, benchmarks, and NCCPL tax schedules."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._portfolio_repo = PgPortfolioRepository(session)
        self._tx_repo = PgTransactionRepository(session)
        self._market_service = get_market_service()

    def get_portfolio_analytics(self, portfolio_id: UUID | None, user_id: UUID) -> dict[str, Any]:
        if portfolio_id:
            portfolio = self._portfolio_repo.get_by_id(portfolio_id)
            if not portfolio or portfolio.user_id != user_id:
                raise NotFoundError("Portfolio not found")
            transactions = self._tx_repo.get_by_portfolio_id(portfolio_id)
        else:
            # Consolidated All Accounts
            portfolios = self._portfolio_repo.get_by_user_id(user_id)
            transactions = []
            for p in portfolios:
                transactions.extend(self._tx_repo.get_by_portfolio_id(p.id))

        symbols = list({tx.symbol for tx in transactions if tx.symbol})
        quotes = self._market_service.get_bulk_quotes(symbols) if symbols else {}
        market_prices = {s: q.current_price for s, q in quotes.items()}

        valuation = PortfolioReplayer.replay(transactions, market_prices)

        # 1. KSE-100 Benchmark
        benchmark = calculate_benchmark_metrics(valuation.unrealized_return_pct)

        # 2. Sector Concentration
        all_securities = {s.symbol: s for s in self._market_service.list_all_securities()}
        current_prices_dec = {s: q.current_price.amount for s, q in quotes.items()}
        sectors = calculate_sector_concentration(valuation.holdings, all_securities, current_prices_dec)

        # 3. NCCPL Capital Gains Tax Schedule
        cgt_schedule = calculate_nccpl_cgt_schedule(valuation.depletions)

        return {
            "benchmark": {
                "benchmark_name": benchmark.benchmark_name,
                "portfolio_return_pct": float(benchmark.portfolio_return_pct),
                "kse100_return_pct": float(benchmark.kse100_return_pct),
                "alpha_pct": float(benchmark.alpha_pct),
                "beta": float(benchmark.beta),
            },
            "sectors": [
                {
                    "sector": s.sector,
                    "market_value": float(s.market_value),
                    "weight_pct": float(s.weight_pct),
                    "stock_count": s.stock_count,
                    "is_concentrated": s.is_concentrated,
                }
                for s in sectors
            ],
            "cgt_schedule": [
                {
                    "holding_period": item.holding_period,
                    "tax_rate_filer_pct": float(item.tax_rate_filer_pct),
                    "tax_rate_non_filer_pct": float(item.tax_rate_non_filer_pct),
                    "realized_gain": float(item.realized_gain),
                    "estimated_tax_filer": float(item.estimated_tax_filer),
                    "estimated_tax_non_filer": float(item.estimated_tax_non_filer),
                }
                for item in cgt_schedule
            ],
        }