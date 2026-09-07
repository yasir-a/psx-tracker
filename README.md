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

---

## Importing Transaction Dumps (Excel / CSV Guidelines)

The application supports importing historical transaction ledgers directly into any Broker or CDC account via `.csv` dumps (compatible with Excel).

### 1. Column Structure & Specifications

The file should include a header row matching the standard export columns (case-insensitive, order-agnostic):

| Column Name | Required | Example | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `Date` | **Yes** | `2026-01-15` or `15/01/2026` | Date of execution. Supports ISO `YYYY-MM-DD`, `DD/MM/YYYY`, and `MM/DD/YYYY`. Must not be in the future. |
| `Type` | **Yes** | `BUY` | Transaction type: `BUY`, `SELL`, `CASH_DEPOSIT`, `CASH_WITHDRAWAL`, `DIVIDEND_CASH`, `BONUS_SHARES`, `RIGHT_SHARES`, `FEE` (or `DEDUCTION`). |
| `Symbol` | Conditional | `SYS` | Required for `BUY`, `SELL`, `BONUS_SHARES`, `RIGHT_SHARES`. Leave blank for cash/fee events. |
| `Quantity` | Conditional | `500` | Number of shares. Must be a positive integer for share trades. |
| `Price per Share (PKR)` | Conditional | `420.50` | Execution price per share for trades, or Dividend Per Share (DPS), or Deposit/Withdrawal/Fee amount. |
| `Fees (PKR)` | No | `125.00` | Total brokerage commission + regulatory taxes. Defaults to `0.00`. |
| `Notes` | No | `Initial buy order` | Optional reference note or description. |

### 2. CSV Template Example

```csv
Date,Type,Symbol,Quantity,Price per Share (PKR),Fees (PKR),Notes
2026-01-01,CASH_DEPOSIT,,0,500000.00,0,Initial capital deposit
2026-01-05,BUY,SYS,1000,420.00,420.00,Brokerage trade confirmation #1024
2026-01-10,FEE,,0,300.00,0,[UIN FEES] Account maintenance
2026-02-01,SELL,SYS,300,460.00,150.00,Partial profit taking
```

### 3. Validation & Accounting Safety Rules

- **Chronological Sorting**: Rows in the file are sorted chronologically by `Date` before processing.
- **FIFO Inventory Validation**: A sequential simulation verifies that no `SELL` transaction sells more shares than were available in the account at that date.
- **Atomic Execution**: Imports are strictly atomic. If any row fails validation, the entire batch is rejected with line numbers and reasons, preventing corrupt or partial state.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

