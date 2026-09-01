# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Phase 12: Comprehensive PSX Market Data Terminal**
  - Interactive full-featured financial terminal for PSX equities modeled on mobile terminal reference designs.
  - **Live Sub-Tab**: Real-time quotes, intraday SVG wave chart with multi-timeframe toggles (`1D`, `1M`, `6M`, `YTD`, `1Y`, `3Y`, `5Y`), volume, open price, last day close, Bid/Ask quotes, interactive Day Range slider, 52-Week Range slider, and circuit breakers.
  - **Fundamentals Sub-Tab**: EPS breakdown (Annual 2025, Last Quarter Q2, YTD, Expected FY), P/E ratios, Expected growth %, PEG ratios, Profit margins (Gross, Operating, Net, EBITDA), Return on Capital (ROE, ROA, ROCE), and Dividend Payout metrics (DPS, Dividend Yield, Dividend Cover, Payout Ratio).
  - **Technicals Sub-Tab**: Real-time indicators with signal badges (RSI 14, STOCH, MACD), Standard Pivot Points (S3 through R3), and Simple Moving Averages (SMA5 to SMA150) with trend ratings.
  - **Announcements Sub-Tab**: Official PSX corporate filings and disclosures with date/time stamps, category tags, and downloadable PDF report links.
  - **Profile Sub-Tab**: Company background narrative, Equity profile (Market Cap, Total Shares, Free Float, Free Float %), Top Executive management (Chairperson, CEO, Secretary), Registered Head Office address, official website link, share registrar, and statutory auditor.
  - **Competitors Sub-Tab**: Peer comparison table comparing peers within the same PSX sector on Price, P/E, Market Cap, Dividend Yield, and 1-Day Return with one-click analysis router.
  - Backend detailed stock intelligence domain model and endpoint `GET /api/v1/market/details/<symbol>`.
- **Phase 11: System Backups, Ledger Export & Corporate Action Custom Dates**
  - One-click PostgreSQL backup utility via `POST /api/v1/system/backup-db` creating timestamped SQL dumps saved into `C:\psx-tracker-backup`.
  - Transaction ledger Excel / CSV export functionality with formatted columns and UTF-8 BOM encoding.
  - Custom execution dates and record-date aware holding validation in Corporate Actions.
  - Transaction editing and deletion support for dividends with automatic lot and cash balance recalculations.
  - KSE-100 index performance benchmark comparison engine calculating Portfolio Alpha (α) and Beta (β) in `backend/src/domain/analytics/benchmark_engine.py`.
  - PSX Sector concentration and diversification risk visualizer with >35% single-sector alerts in `backend/src/domain/analytics/sector_analytics.py`.
  - NCCPL Section 37A Capital Gains Tax (CGT) holding period schedule calculator for Filer (15%) and Non-Filer (30%) in `backend/src/domain/analytics/cgt_calculator.py`.
  - Analytics application service `AnalyticsService` and REST endpoint `/api/v1/analytics/summary`.
  - Interactive frontend `AnalyticsView` with KPI cards, dynamic sector weighting progress bars, and NCCPL tax table.
  - Unit test suite in `backend/tests/unit/test_analytics.py` (38 passing tests).
- **Phase 8: Portfolio UI & Dashboard**
  - Interactive Portfolio Dashboard with 5 KPI cards (Total Valuation, Unrealized P&L, Realized Profit, Trading Cash, and Dividend Income).
  - Interactive Holdings view with live market prices, gain/loss badges, and expandable FIFO open tax lot inspector.
  - Modal dialog for executing trades (`BUY`, `SELL` with short-selling validation) and cash movements (`CASH_DEPOSIT`, `CASH_WITHDRAWAL`).
  - Immutable Transaction Ledger view with type filtering.
  - Corporate Actions view supporting Cash Dividends with Withholding Tax (15% Filer / 30% Non-Filer / Custom rate) and Zakat deduction at source.
  - FBR Section 150 annual dividend tax return summary report.
  - Live PSX market quote browser.
  - Backend `PortfolioAccountingService` and REST endpoints under `/api/v1/portfolio/mine`, `/<id>/valuation`, and `/<id>/transactions`.
- **Phase 7: Frontend Foundation (React / Vite / TypeScript)**
  - React 18 + Vite + TypeScript scaffolding with strict typing and `@/*` path aliases.
  - Tailwind CSS design system with custom PSX color tokens and typography.
  - Accessible UI primitives (`Button`, `Input`, `Card`, `Badge`, `Skeleton`).
  - Authenticated API client with token injection and automatic 401 refresh token interceptor in `frontend/src/services/api.ts`.
  - Global `AuthContext` and `useAuth()` hook for state persistence in `frontend/src/contexts/AuthContext.tsx`.
  - Responsive app shell layout (`Sidebar`, `Header`, `Shell`) with Lucide icons.
  - Registration and Login page views with form validation.
- **Phase 6: Dividends & Corporate Actions Engine**
  - Cash dividend accounting with user-selectable Withholding Tax (15% Filer / 30% Non-Filer / Custom rate) and Zakat deduction at source in `backend/src/domain/corporate_actions/dividend.py`.
  - Bonus shares zero-cost tax lot generation and position expansion in `backend/src/domain/corporate_actions/bonus.py`.
  - Right shares subscription execution and cash debiting in `backend/src/domain/corporate_actions/rights.py`.
  - Stock splits and reverse splits lot re-basing strictly preserving total cost basis invariants in `backend/src/domain/corporate_actions/split.py`.
  - Corporate action orchestration service `CorporateActionService` and REST endpoints (`/api/v1/corporate-actions/dividend`, `/bonus`, `/tax-report/<portfolio_id>`).
  - Alembic migration (`004_corporate_actions.py`) and `CorporateActionModel`.
  - Unit and deterministic accounting test suite (35 total passing tests across codebase).
- **Phase 5: PSX Market Data Layer**
  - Abstract market data provider interface `IMarketDataProvider` in `backend/src/domain/market/provider_interface.py`.
  - PSX security catalog entity `Security` and `MarketQuote` / `HistoricalPrice` value objects in `backend/src/domain/market/`.
  - Alembic migration (`003_securities_and_prices.py`), SQLAlchemy models (`SecurityModel`, `HistoricalPriceModel`), and repository (`PgSecurityRepository`).
  - Offline `MockMarketDataProvider` and live adapter `PSXScraperMarketDataProvider`.
  - Redis caching decorator `CachedMarketService` with batched `MGET` queries and configurable TTL.
  - Market data REST API endpoints (`/api/v1/market/symbols`, `/quote/<symbol>`, `/quotes`, `/historical/<symbol>`).
  - Unit and API integration test suite for market domain and caching (31 total passing tests across codebase).
- **Phase 4: Portfolio Accounting Domain (FIFO Engine)**
  - Financial value objects (`Money` and `Quantity`) with immutable `Decimal` arithmetic and strict currency safety in `backend/src/domain/values/`.
  - Immutable transaction models (`Transaction`, `TransactionType`) and tax lot entities (`TaxLot`, `LotDepletion`, `LotStatus`) in `backend/src/domain/accounting/`.
  - Deterministic FIFO Lot Matching & Depletion Engine (`FIFOMatcher`) with accurate cost-basis tracking, sell fee proration, and short-selling prevention in `backend/src/domain/accounting/fifo_engine.py`.
  - Deterministic Portfolio Replayer Engine (`PortfolioReplayer`) deriving real-time holdings, average cost per share, realized P&L, dividend income, and market valuations in `backend/src/domain/accounting/portfolio_replayer.py`.
  - Alembic migration (`002_transactions_and_tax_lots.py`), SQLAlchemy models, and PostgreSQL repository (`PgTransactionRepository`).
  - Comprehensive unit and deterministic accounting test suite under `backend/tests/accounting/` (25 passing tests across codebase).
- **Phase 3: Authentication & Security**
  - Argon2id password hashing and verification in `backend/src/infrastructure/security/password.py`.
  - PyJWT access and refresh token management with UUID `jti` in `backend/src/infrastructure/security/token_service.py`.
  - Redis token revocation blacklist and sliding window rate limiter in `backend/src/infrastructure/security/rate_limiter.py`.
  - Authentication guard `@jwt_required` and rate limiting `@rate_limit` decorators in `backend/src/api/decorators.py`.
  - Auth application use-case service `AuthService` in `backend/src/application/services/auth_service.py`.
  - Auth REST API endpoints (`/api/v1/auth/register`, `/login`, `/refresh`, `/logout`, `/me`).
  - Redis ping verification added to `/api/v1/ready` readiness probe.
  - Comprehensive unit and end-to-end auth integration test suite (18 passing tests).
- **Phase 2: Database & Migrations (PostgreSQL)**
  - SQLAlchemy 2.0 connection pooling and Flask request-scoped session teardown in `backend/src/infrastructure/db/session.py`.
  - Alembic database migration environment and initial core schema migration (`001_initial_core_schema.py`) for `users`, `portfolios`, and `cash_balances`.
  - Pure domain entities (`User`, `Portfolio`, `CashBalance`) in `backend/src/domain/entities/`.
  - Pure abstract repository interfaces (`IUserRepository`, `IPortfolioRepository`) in `backend/src/domain/repositories/`.
  - Concrete PostgreSQL repository implementations (`PgUserRepository`, `PgPortfolioRepository`) in `backend/src/infrastructure/db/repositories/`.
  - Live PostgreSQL database ping verification added to `/api/v1/ready` readiness probe.
  - Comprehensive unit and database integration test suite (14 passing tests).
- **Phase 1: Backend Foundation (Flask)**
  - Application factory pattern in `backend/src/app.py`.
  - Type-safe, environment-aware configuration via `pydantic-settings` in `backend/src/config.py`.
  - Structured error hierarchy (`AppError`, `ValidationError`, `NotFoundError`, `UnauthorizedError`, `ForbiddenError`) and JSON error handlers in `backend/src/api/errors.py`.
  - Request ID injection and latency logging middleware in `backend/src/api/middleware.py`.
  - Health (`/api/v1/health`) and Readiness (`/api/v1/ready`) endpoints in `backend/src/api/v1/health.py`.
  - Pytest unit test suite covering configuration, error handlers, and health endpoints.
- **Phase 0: Governance & Architecture Baseline**
  - Project governance documents: `README.md`, `AGENTS.md`, `FEATURES.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE`.
  - Issue templates for bug reports and feature requests.
  - Pull request template.
  - Initial architecture blueprints defining modular monolith, FIFO lot accounting, Flask backend layout, PostgreSQL persistence, and Redis caching boundary.

