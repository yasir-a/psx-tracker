# FIFO Lot Accounting Methodology

This document specifies the exact accounting rules, formulas, and edge cases for the **First-In, First-Out (FIFO)** lot-matching engine in the PSX Portfolio Tracker.

---

## 1. Core Principles

1. **Deterministic Reconstruction**: A portfolio's holdings, cost basis, and realized profit/loss are deterministically reconstructed by replaying the append-only ledger of transactions and corporate actions in chronological order.
2. **First-In, First-Out (FIFO) Matching**: When shares of a security are sold, the oldest available open tax lot (earliest acquisition timestamp) is depleted first.
3. **High-Precision Decimal Arithmetic**: Floating-point numbers are prohibited. All quantities, prices, fees, and currency values must be processed using Python's `Decimal` type with fixed rounding conventions (Half-Up).

---

## 2. Transaction Types & Accounting Rules

### 2.1 BUY Transaction
* **Action**: Creates a new open tax lot.
* **Fields**:
  * `lot_id`: Unique identifier
  * `security_id`: PSX symbol
  * `timestamp`: Date and time of execution
  * `original_quantity`: Number of shares bought
  * `remaining_quantity`: Initialized to `original_quantity`
  * `unit_price`: Execution price per share
  * `brokerage_fee`: Transaction fee charged
  * `other_charges`: CDC, NCCPL, or regulatory charges
  * `total_cost_basis`: $(\text{original\_quantity} \times \text{unit\_price}) + \text{brokerage\_fee} + \text{other\_charges}$
  * `cost_basis_per_share`: $\frac{\text{total\_cost\_basis}}{\text{original\_quantity}}$

---

### 2.2 SELL Transaction
* **Action**: Depletes existing open lots for the security in FIFO order (ascending timestamp).
* **Validation**: Total available `remaining_quantity` across open lots must be $\ge \text{sell\_quantity}$. If not, reject transaction (short selling / negative holdings are prohibited).
* **Depletion Process**:
  * Iterate through open lots from oldest to newest.
  * For each lot, determine $\text{shares\_to\_deplete} = \min(\text{lot.remaining\_quantity}, \text{unmatched\_sell\_quantity})$.
  * Calculate proportion of lot cost basis:
    $$\text{cost\_basis\_depleted} = \text{lot.cost\_basis\_per\_share} \times \text{shares\_to\_deplete}$$
  * Calculate gross proceeds from this portion:
    $$\text{gross\_proceeds} = \text{sell\_unit\_price} \times \text{shares\_to\_deplete}$$
  * Deduct prorated sell fees:
    $$\text{allocated\_sell\_fees} = \text{total\_sell\_fees} \times \left(\frac{\text{shares\_to\_deplete}}{\text{sell\_quantity}}\right)$$
  * **Realized P&L for Depleted Chunk**:
    $$\text{Realized P\&L} = \text{gross\_proceeds} - \text{cost\_basis\_depleted} - \text{allocated\_sell\_fees}$$
  * Update `lot.remaining_quantity = lot.remaining_quantity - shares_to_deplete`.
  * If `lot.remaining_quantity == 0`, mark lot as `CLOSED`.

---

### 2.3 BONUS SHARES (Stock Dividends)
* **Description**: Company issues additional shares to existing shareholders at zero cost.
* **PSX Behavior**: Bonus percentage is announced based on existing holdings at book closure date.
* **Accounting Treatment**:
  * Bonus shares create an additional tax lot with **zero acquisition cost** ($\text{cost\_basis} = 0$, $\text{fee} = 0$) OR dilute the existing lots proportionally.
  * **Selected Model**: In our FIFO lot ledger, bonus shares are recorded as a distinct lot linked to the corporate action event with $\text{cost\_basis} = 0$. When sold under FIFO, these shares will yield realized gain equal to net proceeds minus sell fees.

---

### 2.4 RIGHT SHARES (Rights Offering)
* **Description**: Opportunity for existing shareholders to purchase new shares at a specified subscription price.
* **Accounting Treatment**:
  * Exercising rights creates a new standard tax lot with $\text{unit\_price} = \text{subscription\_price}$ and $\text{acquisition\_date} = \text{subscription\_settlement\_date}$.

---

### 2.5 STOCK SPLITS & REVERSE SPLITS
* **Description**: Company splits existing shares by a ratio $R$ (e.g., 2:1 split where $R = 2$, or 1:5 reverse split where $R = 0.2$).
* **Accounting Treatment**:
  * Every existing open lot for the symbol is adjusted:
    $$\text{new\_remaining\_quantity} = \text{old\_remaining\_quantity} \times R$$
    $$\text{new\_cost\_basis\_per\_share} = \frac{\text{old\_cost\_basis\_per\_share}}{R}$$
  * Total lot cost basis remains identical before and after the split.

---

### 2.6 CASH DIVIDENDS
* **Description**: Cash distributions paid per share.
* **Accounting Treatment**:
  * Does not alter share quantities or lot cost bases.
  * Recorded in the cash ledger as an increase in cash balance and credited to total portfolio dividend income.
  * Withholding tax (e.g., PSX Filer 15% vs Non-Filer 30%) is recorded as a tax deduction event.

---

## 3. Holding & Portfolio Valuation Metrics

At any timestamp $T$ with market price $P_{market}$:

* **Total Quantity**: $\sum \text{open\_lot.remaining\_quantity}$
* **Total Cost Basis**: $\sum \text{open\_lot.remaining\_cost\_basis}$
* **Average Cost Per Share**: $\frac{\text{Total Cost Basis}}{\text{Total Quantity}}$
* **Current Market Value**: $\text{Total Quantity} \times P_{market}$
* **Unrealized Gain / Loss**: $\text{Current Market Value} - \text{Total Cost Basis}$
* **Unrealized Return %**: $\left(\frac{\text{Current Market Value} - \text{Total Cost Basis}}{\text{Total Cost Basis}}\right) \times 100$
* **Day Gain / Loss**: $\text{Total Quantity} \times (P_{market} - P_{previous\_close})$

