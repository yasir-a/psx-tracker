# PSX Portfolio Tracker

A professional, open-source portfolio tracking application for stocks listed on the Pakistan Stock Exchange (PSX).

Designed with ledger-grade financial accounting, full support for PSX-specific corporate actions, an immutable transaction model, and decoupled architecture.

---

## Key Features (Planned & Roadmap)

* **Ledger-Grade Accounting**: Complete portfolio state reconstruction from transaction logs (FIFO lot tracking).
* **PSX Market Support**: PSX symbol mapping, historical and daily price feeds, and sector classifications.
* **Corporate Actions**: Proper accounting for cash dividends, bonus shares, right shares, stock splits, and symbol changes.
* **Performance & Analytics**: Realized vs. unrealized P&L, day return, total return, dividend yields, sector exposure, and benchmark comparison against KSE-100.
* **Security & Reliability**: PostgreSQL authoritative storage, Redis for rate limiting and caching, isolated domain logic.

---

## Technology Stack

* **Frontend**: React, Vite, TypeScript
* **Backend**: Python, Flask (Modular Blueprints, clean Domain/Service/Repository layer)
* **Database**: PostgreSQL (Authoritative persistent data store with migration strategy)
* **Cache / Ephemeral Store**: Redis (Sessions, rate limiting, task coordination, caching)

---

## Project Structure Overview

```text
psx-tracker/
├── docs/                # Architecture, PSX rules, and API specifications
├── backend/             # Python / Flask modular REST API
├── frontend/            # React / Vite / TypeScript client application
├── docker/              # Local development container definitions
├── AGENTS.md            # Persistent engineering context for AI agents
├── FEATURES.md          # Feature status and acceptance criteria registry
├── CHANGELOG.md         # Project history and release log
├── CONTRIBUTING.md      # Development and contribution guidelines
├── SECURITY.md          # Security policy and vulnerability disclosure
└── LICENSE              # MIT License
```

---

## Development Phases

* **Phase 0: Repository & Governance** *(In Progress)*
* **Phase 1: Backend Foundation** *(Flask structure, config, logging, health check)*
* **Phase 2: Database & Migrations** *(PostgreSQL, models, repositories)*
* **Phase 3: Authentication & Users** *(JWT/Session, user isolation, security controls)*
* **Phase 4: Portfolio Accounting Domain** *(FIFO lots, ledger, transactions, P&L)*
* **Phase 5: PSX Market Data** *(Decoupled provider abstraction, daily/historical prices)*
* **Phase 6: Dividends & Corporate Actions** *(Bonus, rights, splits, cash dividends)*
* **Phase 7: Frontend Foundation** *(React, Vite, TS, routing, UI library)*
* **Phase 8: Portfolio UI** *(Dashboard, holdings, transaction entry, analytics)*
* **Phase 9: Advanced Analytics & Reporting** *(Benchmarks, alerts, tax reports)*

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

