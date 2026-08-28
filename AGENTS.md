# AGENTS.md — Persistent Engineering Context & Architecture Guide

> **CRITICAL RULE FOR ALL AI AGENTS:**
> This file is the authoritative persistent context for this project.
> Read this file, along with `FEATURES.md`, `README.md`, and `CHANGELOG.md`, at the beginning of EVERY interaction or session.
> NEVER assume prior conversational context exists. Update this document immediately whenever an architectural decision is made or changed.

---

## 1. Project Purpose & Scope

* **Name:** PSX Portfolio Tracker
* **Description:** A professional, open-source, production-grade portfolio tracking system for securities listed on the Pakistan Stock Exchange (PSX).
* **Core Value:** Ledger-grade financial correctness, transaction-driven portfolio reconstruction, comprehensive corporate action handling (dividends, bonus shares, rights, splits), and strict decoupling of domain logic from external frameworks/APIs.

---

## 2. Foundational Architecture Decisions

### 2.1 Technology Stack Decisions
* **Frontend:** React, Vite, TypeScript. Clean component architecture, accessible UI, no Next.js.
* **Backend Framework:** **Flask** (Python).
  * **Strict Policy:** Do NOT use FastAPI, Litestar, Django, or other frameworks unless explicitly approved by the project owner.
  * Structure using modular Flask **Blueprints** for API domains.
  * Keep dependencies minimal. Use a single unified validation approach (avoid unnecessary dual validation dependencies).
  * Keep domain and accounting logic entirely framework-agnostic.
* **Persistent Database:** **PostgreSQL**.
  * Authoritative source of all financial, user, and portfolio state.
  * Schema managed strictly via migrations (e.g., Alembic).
* **Caching & Ephemeral Layer:** **Redis**.
  * Use for rate limiting, session states, response caching, and task coordination.
  * **Rule:** Redis is NEVER authoritative for financial state. The application must completely recover state from PostgreSQL if Redis data is wiped.
* **License:** **MIT License** (Copyright: Yasir W.).

### 2.2 Financial & Accounting Model Decisions
* **Accounting Methodology:** **FIFO (First-In, First-Out)** lot accounting is the primary and initial methodology.
* **Future-Proofing for WAC:** The domain architecture must isolate lot-matching logic behind clean interfaces so **Weighted Average Cost (WAC)** or Specific Identification can be added later without schema/transaction rewrites.
* **Ledger Reconstruction:** Portfolio values and holdings are derived deterministically from an append-only event ledger (BUY, SELL, DIVIDEND, BONUS, RIGHTS, SPLIT, MERGER, DELISTING, CASH_DEPOSIT, CASH_WITHDRAWAL, FEES).
* **Market Data Decoupling:** Market data feeds must implement an abstract `MarketDataProvider` interface so PSX data providers (scrapers, APIs, static feeds) can be swapped or mocked without touching accounting logic.

---

## 3. Strict Operating Rules for AI Agents

### 3.1 File Modification & Command Execution Policy
* **Markdown Files Only (`*.md`):** The AI agent is authorized to directly create, edit, or delete ONLY markdown documentation files (`README.md`, `AGENTS.md`, `FEATURES.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, etc.).
* **Non-Markdown Files (`.py`, `.ts`, `.tsx`, `.sql`, `.json`, `.yml`, `.env`, etc.):**
  * **DO NOT** modify, create, or overwrite these files automatically.
  * The agent must provide the exact file path, exact location/line number, exact code snippet, justification, and manual validation instructions for the human developer to apply.
* **Terminal Commands:** Do not run terminal/shell commands automatically. Always provide the exact command line strings for the human developer to execute manually.

### 3.2 Feature Lifecycle Checklist
For every feature or task, follow these steps strictly:
1. Review requirement, `AGENTS.md`, `FEATURES.md`, and relevant architecture docs.
2. Define acceptance criteria and test coverage plan.
3. Identify affected files, database changes, API contracts, and UI states.
4. Update relevant documentation (e.g., `FEATURES.md`, `CHANGELOG.md`).
5. Provide precise code snippets and instructions for non-Markdown files.
6. Verify via automated tests and manual check steps.
7. Confirm with the user before finalizing commits/PRs.

---

## 4. Repository & Codebase Directory Structure

```text
psx-tracker/
├── docs/                     # Specifications & deep-dive architecture docs
│   ├── architecture/         # System design, accounting model, Redis usage
│   ├── psx/                  # PSX trading rules, tax & fee structures, corporate actions
│   └── api/                  # API v1 contract specs
├── backend/
│   ├── src/
│   │   ├── api/              # Flask Blueprints, route handlers, serializers
│   │   ├── application/      # Use-cases, orchestration, application DTOs
│   │   ├── domain/           # Pure business logic (Ledger, FIFO matcher, Entities, Money VO)
│   │   ├── infrastructure/   # DB models, PostgreSQL repositories, Redis client, MarketData adapters
│   │   └── config.py         # Type-safe configuration and environment loading
│   ├── tests/
│   │   ├── unit/             # Isolated unit tests (domain logic, money math)
│   │   ├── accounting/       # Deterministic accounting & FIFO scenario test suite
│   │   └── integration/      # API and database repository tests
│   └── migrations/           # Database schema migration scripts
├── frontend/
│   ├── src/
│   │   ├── components/       # Shared UI primitives
│   │   ├── features/         # Domain-specific UI (holdings, transactions, analytics)
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API HTTP client
│   │   └── types/            # TypeScript interfaces and models
├── .github/
│   ├── workflows/            # GitHub Actions CI pipelines
│   ├── ISSUE_TEMPLATE/       # Bug report & feature templates
│   └── PULL_REQUEST_TEMPLATE.md
├── AGENTS.md                 # Agent context & rules (this file)
├── FEATURES.md               # Living feature registry and tracking
├── CHANGELOG.md              # Keep a Changelog formatted history
├── CONTRIBUTING.md           # Contribution and commit conventions
├── SECURITY.md               # Security reporting and guidelines
├── CODE_OF_CONDUCT.md        # Contributor Covenant v2.1
├── LICENSE                   # MIT License
├── .gitignore
└── .env.example
```

---

## 5. Coding & Architectural Conventions

### 5.1 Backend (Python / Flask)
* **Type Annotations:** 100% type hint coverage (`typing` / Python 3.11+ built-in types).
* **Pure Domain Layer:** Code in `backend/src/domain/` MUST NOT import Flask, database ORMs, or external I/O libraries. Domain entities and accounting engines operate solely on pure Python objects / data structures.
* **Money Representation:** Use `Decimal` (or a dedicated `Money` value object) for all monetary calculations. **NEVER use floating-point types (`float`) for currency or financial ledger quantities.**
* **API Versioning:** All endpoints prefixed with `/api/v1/`. Consistent error payload format:
  ```json
  {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "Human readable description",
      "details": {}
    }
  }
  ```

### 5.2 Git & Commit Conventions
* **Branch Strategy:** `main` is protected. Work in `feature/*`, `fix/*`, `docs/*`, `test/*`, `chore/*`.
* **Commit Messages:** Follow Conventional Commits:
  * `feat: ...`
  * `fix: ...`
  * `docs: ...`
  * `test: ...`
  * `refactor: ...`
  * `chore: ...`
  * `security: ...`

---

## 6. Current Implementation Status

* **Current Phase:** **Phase 7 — Complete; Ready for Phase 8 (Portfolio UI & Dashboard)**
* **Status:** React 18, Vite, strict TypeScript, Tailwind CSS design tokens, accessible UI primitives, authenticated API client with token refresh interceptors, AuthContext, and responsive shell navigation layout verified and running.
* **Next Steps:**
  1. Begin Phase 8: Implement interactive Portfolio Dashboard, Holdings Table with live gains, Transaction Entry modals (BUY/SELL/CASH), Corporate Actions forms (with WHT 15%/30%), and performance charts.
