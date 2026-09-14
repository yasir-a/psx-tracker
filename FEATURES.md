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
| `CORP-001` | Cash Dividend Accounting | **Completed** | `ACC-002` | Dividend income tracking, withholding tax accounting (15% Filer / 30% Non-Filer), yield on cost. |
| `CORP-002` | Bonus Shares Allocation | **Completed** | `ACC-003` | Zero-cost lot generation, cost basis dilution, total quantity adjustments. |
| `CORP-003` | Right Shares Accounting | **Completed** | `ACC-003` | Subscription payments, new lot creation, cost averaging. |
| `CORP-004` | Stock Splits & Reverse Splits | **Completed** | `ACC-003` | Lot quantity multiplication, cost-basis division, symbol history preservation. |

---

## Phase 7: Frontend Foundation (React / Vite / TypeScript)

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `FE-001` | React + Vite + TypeScript Setup | **Completed** | `GOV-003` | Project scaffolding, path aliases, ESLint, Prettier, strict TS configuration. |
| `FE-002` | Design System & UI Primitive Components | **Completed** | `FE-001` | Accessible buttons, inputs, modals, cards, data tables, skeleton loaders. |
| `FE-003` | API Client & Auth State Provider | **Completed** | `FE-001`, `AUTH-002` | Axios/Fetch wrapper with interceptors, token refresh, auth context. |
| `FE-004` | Responsive Layout & Shell Navigation | **Completed** | `FE-002` | Sidebar, header, responsive mobile drawer, breadcrumbs. |

---

## Phase 8: Portfolio UI & Dashboard

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `UI-001` | Portfolio Dashboard Overview | **Completed** | `FE-004`, `ACC-004` | Total value, day return, total P&L, allocation breakdown charts, separated dividend income. |
| `UI-002` | Holdings Table View | **Completed** | `FE-002`, `ACC-004` | Quantity, avg cost, current price, unrealized P&L, day change, expandable FIFO tax lots inspector. |
| `UI-003` | Transaction Entry Modal & Log | **Completed** | `FE-002`, `ACC-002` | Form with real-time fee calculation, validation, and historical transaction list. |
| `UI-004` | Performance & Analytics View | **Completed** | `FE-001`, `ACC-004` | Total return over time, time-weighted returns, FBR Section 150 tax report. |

## Phase 9: Advanced Analytics & PSX Extensions

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
## Phase 12: Comprehensive PSX Market Data Terminal

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `MKT-004` | Security Live Market View | **Completed** | `MKT-001` | Intraday chart, bid/ask, day/52-week sliders, circuit breakers. |
| `MKT-005` | Fundamentals & Valuation Ratios | **Completed** | `MKT-004` | EPS, P/E, Margins (Gross/Net/EBITDA), ROE/ROA, Dividend payouts. |
| `MKT-006` | Technical Indicators & Pivots | **Completed** | `MKT-004` | RSI(14), STOCH, MACD, S1-S3 / R1-R3 Pivot Points, SMA5-150. |
| `MKT-007` | Corporate Announcements & Filings | **Completed** | `MKT-004` | Quarterly reports, corporate briefings, board meetings, PDF downloads. |
| `MKT-008` | Company Profile & Competitors | **Completed** | `MKT-004` | Free float %, market cap, executive team, address, auditor, sector peer comparison. |

## Phase 13: Admin User & Security Management

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `ADM-001` | Role-Based Access Control | **Completed** | `AUTH-001` | `user` vs `admin` roles, `@admin_required` server-side enforcement. |
| `ADM-002` | Admin CLI Setup Tool | **Completed** | `ADM-001` | `setup_admin.py` for promoting or creating dedicated admin accounts. |
| `ADM-003` | Admin User Directory Dashboard | **Completed** | `ADM-001` | Search, user table, role badges, portfolio counts, created timestamp. |
| `ADM-004` | Admin Password Reset | **Completed** | `ADM-001` | Secure Argon2id reset with immediate in-memory token revocation. |
| `ADM-005` | Cascading User Hard Deletion | **Completed** | `ADM-001` | Atomic removal of user, portfolios, ledgers, tax lots, and in-memory cache keys. |
| `ADM-006` | Administrator Self-Protection | **Completed** | `ADM-005` | Block self-deletion and prevent deletion of last remaining admin. |
| `ADM-007` | PostgreSQL Intraday Market Persistence | **Completed** | `MKT-004` | PostgreSQL `intraday_snapshots` table for resilient weekend & off-hours chart continuity. |
| `ADM-008` | Zero-Dependency In-Memory Caching Layer | **Completed** | `BE-001` | Completely eliminated Redis in favor of thread-safe `InMemoryCache` with DB persistence. |

## Phase 14: Account Deductions & Fee Recording

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `TX-005` | Account Fee & Deduction Recording | **Completed** | `ACC-001` | Record 8 predefined deduction types (UIN Fees, CGT Debit, Custody, SST, CDC, Stamp Paper, KYC, SMS) deducting directly from broker/CDC cash balance. |

## Phase 15: Excel / CSV Transaction Ledger Import & Ledger Enhancements

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `TX-006` | Excel / CSV Ledger Dump Import | **Completed** | `TX-005` | Direct import of transaction history dumps into specific broker accounts with schema checks, FIFO inventory simulation, line-by-line validation, and atomic commit. |
| `TX-007` | NCCPL CGT Credit Deposit Handling | **Completed** | `TX-005` | Dedicated deposit type for capital gains tax credits/refunds with distinctive teal badge and automated import classification. |
| `TX-008` | Full Ledger Editability & Transfer Dates | **Completed** | `TX-006` | Full editing support for dates, regulatory fees, notes, and values across Broker and CDC accounts, plus execution date picker for share transfers. |
| `TX-009` | Deduction Category Ledger Badging | **Completed** | `TX-005` | Dynamic extraction and display of deduction types (UIN Fees, CGT Debit, etc.) in the Symbol column with amber styling. |
| `TX-010` | Corporate Actions Eligible Shares Input | **Completed** | `CA-001` | Optional manual override for eligible share count when crediting dividends for securities sold post-book-closure / record date. |
| `TX-011` | Ledger Pagination & Newest-First Sort | **Completed** | `TX-006` | Client-side UI sorting displaying newest transactions on top, combined with paginated ledger controls (10/15/25/50/100 rows per page) and responsive page jump buttons without altering backend FIFO replay order. |

## Phase 16: Live Market Price Sync & Resilient DPS Scraper

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `MKT-009` | Multi-Tiered PSX Market Price Scraper | **Completed** | `MKT-004` | Resolves Market Price defaulting to Avg Cost. Ingests newest intraday tick (`ticks[0]`), falls back to official closing bar (`/timeseries/eod/{sym}`), and falls back to PostgreSQL persisted quotes. |
| `MKT-010` | Thread-Safe Parallel Bulk Ingestion | **Completed** | `MKT-009` | Concurrent parallel quote fetching via `ThreadPoolExecutor` eliminating unsafe Flask thread-local `g.db_session` context crashes. |
| `MKT-011` | On-Demand Live Sync & Cache Invalidation | **Completed** | `MKT-009` | One-click **Live Sync** in Header with cache flush endpoint (`POST /api/v1/market/refresh`), visual spinning indicator, and toast notifications. |
| `MKT-012` | Optimized Transaction Modal UX | **Completed** | `TX-001` | Immediate modal closure upon 201 response, eliminating 20s blocking spinners while valuation refreshes asynchronously. |

## Phase 17: Executive Financial Dashboard & Brokerage Fee Precision

| Feature ID | Feature Name | Status | Dependencies | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `DASH-001` | Executive 10-KPI Dashboard Tiers | **Completed** | `VAL-001` | Replaces single stat rows with two distinct 5-card financial tiers: Tier 1 (Wealth & Performance: Net Portfolio Value, All-Time Net P&L, Total Return %, Today's Change PKR, Today's Return %) and Tier 2 (Capital Flows & Liquidity: Total Injected Capital, Invested Cost, Available Cash, Total Deposited, Total Withdrawn). |
| `DASH-002` | Asset Allocation & Broker Liquidity Distribution | **Completed** | `ACC-001`, `DASH-001` | Visual distribution bar comparing Invested Capital vs Liquid Cash ratio, alongside multi-broker liquidity cards displaying per-broker cash balances, account numbers, and quick-filter interaction. |
| `DASH-003` | Today's Key Movers Spotlight | **Completed** | `DASH-001`, `MKT-009` | Real-time highlight cards showing Top Gainer and Top Drag based on today's rupee and percentage change, with quick symbol badges and direct trade shortcuts. |
| `DASH-004` | Cumulative Cash Ledger Ingestion & Injected Capital Math | **Completed** | `LEDGER-001` | Full tracking of `total_cash_deposited` and `total_cash_withdrawn` across the FIFO replayer and valuation engine, calculating exact `net_injected_capital` and `all_time_net_profit` (Realized P&L + Unrealized P&L + Dividends - Fees). |
| `TX-012` | Brokerage Fee Input Precision | **Completed** | `TX-001` | Fixes transaction creation bug where `brokerage_fee` was hardcoded to 0; now accurately extracts, validates, and persists user-entered brokerage commission for BUY and SELL trades. |


