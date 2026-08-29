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

## Local Development & Setup

### 1. Prerequisites
* **Python**: 3.11+
* **Node.js**: 18+ & npm
* **PostgreSQL**: 15+ (installed locally or via lightweight installer)

---

### 2. PostgreSQL Local Database Setup (Easy Windows Guide)

You can set up local PostgreSQL in one of two simple ways:

#### Method A: Direct Windows Installer (Recommended for Local Dev)
1. Download the official installer from [PostgreSQL Windows Downloads (EDB)](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
2. Run the installer and choose a password for the default `postgres` user (e.g. `psx_password` or your preferred password).
3. Open **SQL Shell (psql)** or **pgAdmin** from your Windows Start Menu and run:
   ```sql
   CREATE DATABASE psx_portfolio;
   CREATE USER psx_user WITH ENCRYPTED PASSWORD 'psx_password';
   GRANT ALL PRIVILEGES ON DATABASE psx_portfolio TO psx_user;
   ALTER DATABASE psx_portfolio OWNER TO psx_user;
   ```
4. Verify your local connection string in your `.env` file:
   ```env
   DATABASE_URL=postgresql://psx_user:psx_password@localhost:5432/psx_portfolio
   ```

#### Method B: Standalone Windows Portable / Scoop / Winget
Using Windows package manager:
```powershell
winget install PostgreSQL.PostgreSQL
```

---

### 3. Running the Backend

```powershell
# 1. Activate Python virtual environment
.venv\Scripts\Activate.ps1

# 2. Install backend dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# 3. Apply database migrations
cd backend
alembic upgrade head
cd ..

# 4. Start Flask server (runs on http://127.0.0.1:5000)
python backend/wsgi.py
```

---

### 4. Running the Frontend

```powershell
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

---

## Development Phases

* **Phase 0: Repository & Governance** *(Completed)*
* **Phase 1: Backend Foundation** *(Completed)*
* **Phase 2: Database & Migrations** *(Completed)*
* **Phase 3: Authentication & Users** *(Completed)*
* **Phase 4: Portfolio Accounting Domain** *(Completed)*
* **Phase 5: PSX Market Data** *(Completed)*
* **Phase 6: Dividends & Corporate Actions** *(Completed)*
* **Phase 7: Frontend Foundation** *(Completed)*
* **Phase 8: Portfolio UI & Dashboard** *(Next)*
* **Phase 9: Advanced Analytics & Reporting** *(Planned)*

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

