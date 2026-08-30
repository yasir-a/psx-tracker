export interface TaxLot {
  lot_id: string;
  original_quantity: number;
  remaining_quantity: number;
  unit_price: number;
  cost_basis_per_share: number;
  remaining_cost_basis: number;
  status: 'OPEN' | 'CLOSED';
  executed_at: string;
}

export interface Holding {
  symbol: string;
  quantity: number;
  cost_per_share: number;
  total_cost_basis: number;
  current_price: number;
  market_value: number;
  unrealized_gain: number;
  unrealized_return_pct: number;
  day_change: number;
  day_change_pct: number;
  open_lots: TaxLot[];
}

export interface PortfolioSummary {
  total_portfolio_value: number;
  total_stock_value: number;
  total_cost_basis: number;
  cash_balance: number;
  unrealized_gain: number;
  unrealized_return_pct: number;
  realized_gain: number;
  total_fees_paid: number;
  total_dividends_earned: number;
}

export interface PortfolioHeader {
  id: string;
  name: string;
  currency: string;
  is_consolidated?: boolean;
  account_count?: number;
}

export interface PortfolioValuationResponse {
  portfolio: PortfolioHeader;
  summary: PortfolioSummary;
  holdings: Holding[];
}

export type TransactionTypeUnion =
  | 'BUY'
  | 'SELL'
  | 'CASH_DEPOSIT'
  | 'CASH_WITHDRAWAL'
  | 'DIVIDEND_CASH'
  | 'BONUS_SHARES'
  | 'RIGHT_SHARES'
  | 'STOCK_SPLIT'
  | 'FEE'
  | 'TRANSFER_OUT'
  | 'TRANSFER_IN';

export interface TransactionRecord {
  id: string;
  portfolio_id: string;
  portfolio_name?: string;
  transaction_type: TransactionTypeUnion;
  symbol: string | null;
  quantity: number;
  price_per_share: number;
  brokerage_fee: number;
  regulatory_fee: number;
  gross_amount: number;
  net_amount: number;
  executed_at: string;
  notes: string | null;
}