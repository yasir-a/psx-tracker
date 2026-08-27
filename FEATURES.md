# Features Registry

This document tracks all features across their full lifecycle for the PSX Portfolio Tracker.

Status definitions:
* **Completed**: Implemented, automated tests passing, documented, PR merged.
* **In Progress**: Actively being worked on in the current phase/branch.
* **Planned**: Prioritized for upcoming phases in the development roadmap.
* **Proposed**: Under consideration and architectural discussion.
* **Deferred**: Backlogged for later evaluation.

---

## Phase 0: Repository & Governance Foundation

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `GOV-001` | Governance & Documentation Baseline | **Completed** | None | Created `AGENTS.md`, `README.md`, `FEATURES.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `docs/architecture/accounting-model.md`. |
| `GOV-002` | Issue & PR Templates | **Completed** | `GOV-001` | Standard bug report, feature request, and pull request checklist templates created. |
| `GOV-003` | Git Baseline & Environment Setup | **Completed** | `GOV-001` | `.gitignore`, `.env.example`, and directory structure baseline established and committed to `main`. |
| `GOV-004` | Baseline CI Pipeline Definitions | **Completed** | `GOV-003` | GitHub Actions workflow for backend CI (`.github/workflows/backend-ci.yml`) established. |

---

## Phase 1: Backend Foundation (Flask)

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `BE-001` | Modular Flask Application Factory | **Completed** | `GOV-004` | Blueprints layout, app factory pattern, structured config management. |
| `BE-002` | Structured Error Handling & Response Format | **Completed** | `BE-001` | Uniform error handler and standard API response envelope. |
| `BE-003` | Health Check & System Readiness Endpoints | **Completed** | `BE-001` | `/api/v1/health` and `/api/v1/ready` endpoints verifying DB and Redis liveness. |
| `BE-004` | Structured Logging & Request Tracing | **Completed** | `BE-001` | Request ID injection and context logging (no sensitive data). |

---

## Phase 2: Database & Migrations (PostgreSQL)

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `DB-001` | PostgreSQL Connection & Session Management | **Completed** | `BE-001` | Engine setup, connection pooling, transactional unit-of-work. |
| `DB-002` | Alembic Migration Setup | **Completed** | `DB-001` | Migration scripts directory, version tracking, downgrade support. |
| `DB-003` | Core Schema: Users & Portfolios | **Completed** | `DB-002` | Initial schema tables, unique constraints, foreign keys, index optimization. |
| `DB-004` | Repository Pattern Implementation | **Completed** | `DB-003` | Abstract base repositories and PostgreSQL implementations. |

---

## Phase 3: Authentication & Security

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `AUTH-001` | User Registration & Argon2 Password Hashing | **Completed** | `DB-003` | Secure hashing, email normalization, validation. |
| `AUTH-002` | Session Management & Token Handling | **Completed** | `AUTH-001` | Secure HTTP-only cookies, Redis token revocation/session tracking. |
| `AUTH-003` | Redis Rate Limiting | **Completed** | `BE-001` | IP and user rate limiting middleware for sensitive endpoints. |
| `AUTH-004` | User-Owned Resource Authorization | **Completed** | `AUTH-002` | Strict checks ensuring users can only access their own portfolios/transactions. |

---

## Phase 4: Portfolio Accounting Domain (FIFO Engine)

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `ACC-001` | Financial Value Objects (Decimal Money/Quantities) | **Completed** | `BE-001` | High-precision arithmetic, rounding rules, currency validation. |
| `ACC-002` | Transaction & Ledger Event Model | **Completed** | `DB-003` | Immutable transaction records (BUY, SELL, CASH movements, FEES). |
| `ACC-003` | FIFO Lot Matching Engine | **Completed** | `ACC-001`, `ACC-002` | Deterministic lot depletion, cost basis tracking, realized gain calculation on sells. |
| `ACC-004` | Holdings & Unrealized P&L Calculation | **Completed** | `ACC-003` | Average acquisition cost, market valuation, day return, unrealized P&L. |
| `ACC-005` | Accounting Test Suite | **Completed** | `ACC-003` | Comprehensive deterministic test scenarios (multiple buys, partial sells, same-day trades). |

---

## Phase 5: PSX Market Data Layer

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `MKT-001` | MarketDataProvider Abstraction | **Completed** | `BE-001` | Clean abstract interface for symbols, historical prices, and daily quotes. |
| `MKT-002` | PSX Security & Symbol Registry | **Completed** | `DB-003`, `MKT-001` | Sector classifications, active/suspended/delisted status tracking. |
| `MKT-003` | PSX Market Data Adapter & Caching | **Completed** | `MKT-001` | Ingestion adapter with Redis caching for real-time and end-of-day quotes. |
## Phase 6: Dividends & Corporate Actions

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `CORP-001` | Cash Dividend Accounting | Planned | `ACC-002` | Dividend income tracking, withholding tax accounting, yield on cost. |
| `CORP-002` | Bonus Shares Allocation | Planned | `ACC-003` | Zero-cost lot generation, cost basis dilution, total quantity adjustments. |
| `CORP-003` | Right Shares Accounting | Planned | `ACC-003` | Subscription payments, new lot creation, cost averaging. |
| `CORP-004` | Stock Splits & Reverse Splits | Planned | `ACC-003` | Lot quantity multiplication, cost-basis division, symbol history preservation. |

---

## Phase 7: Frontend Foundation (React / Vite / TypeScript)

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `FE-001` | React + Vite + TypeScript Setup | Planned | `GOV-003` | Project scaffolding, path aliases, ESLint, Prettier, strict TS configuration. |
| `FE-002` | Design System & UI Primitive Components | Planned | `FE-001` | Accessible buttons, inputs, modals, cards, data tables, skeleton loaders. |
| `FE-003` | API Client & Auth State Provider | Planned | `FE-001`, `AUTH-002` | Axios/Fetch wrapper with interceptors, token refresh, auth context. |
| `FE-004` | Responsive Layout & Shell Navigation | Planned | `FE-002` | Sidebar, header, responsive mobile drawer, breadcrumbs. |

---

## Phase 8: Portfolio UI & Dashboard

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `UI-001` | Portfolio Dashboard Overview | Planned | `FE-004`, `ACC-004` | Total value, day return, total P&L, allocation breakdown charts. |
| `UI-002` | Holdings Table View | Planned | `FE-002`, `ACC-004` | Quantity, avg cost, current price, unrealized P&L, day change, sector tags. |
| `UI-003` | Transaction Entry Modal & Log | Planned | `FE-002`, `ACC-002` | Form with real-time fee calculation, validation, and historical transaction list. |
| `UI-004` | Performance & Analytics View | Planned | `FE-001`, `ACC-004` | Total return over time, time-weighted returns, sector concentration. |

---

## Phase 9: Advanced Analytics & PSX Extensions

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `ADV-001` | KSE-100 Benchmark Comparison | Planned | `UI-004`, `MKT-003` | Relative portfolio alpha/beta and performance overlay against index. |
| `ADV-002` | Watchlists & Price Alerts | Planned | `MKT-003`, `FE-004` | Custom watchlists with real-time price monitoring and alerts. |
| `ADV-003` | Tax & Capital Gains Summary Reports | Planned | `ACC-003` | PSX NCCPL tax rate calculation (Filer vs. Non-Filer capital gains reports). |
