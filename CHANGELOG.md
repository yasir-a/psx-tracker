# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
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

