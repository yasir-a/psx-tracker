export interface DeductionSummary {
  total_deductions: number;
  total_brokerage_commission: number;
  total_regulatory_fees: number;
  total_taxes_paid: number;
  total_account_fees: number;
  total_traded_volume: number;
  fee_drag_pct: number;
  total_event_count: number;
}

export interface DeductionCategoryItem {
  category: string;
  group: 'Trading Friction' | 'Taxes' | 'Account & Custody';
  recipient: string;
  count: number;
  total_amount: number;
  share_pct: number;
}

export interface BrokerDeductionItem {
  portfolio_id: string;
  portfolio_name: string;
  total_amount: number;
  trading_fees: number;
  taxes: number;
  account_fees: number;
  share_pct: number;
}

export interface MonthlyDeductionItem {
  year: number;
  month: number;
  month_name: string;
  trading_fees: number;
  taxes: number;
  account_fees: number;
  total_amount: number;
}

export interface YearlyDeductionItem {
  year: number;
  trading_fees: number;
  taxes: number;
  account_fees: number;
  total_amount: number;
}

export interface DeductionLedgerRecord {
  id: string;
  executed_at: string;
  portfolio_name: string;
  category: string;
  group: string;
  recipient: string;
  symbol: string;
  amount: number;
  notes: string;
}

export interface DeductionAnalyticsData {
  summary: DeductionSummary;
  by_category: DeductionCategoryItem[];
  by_account: BrokerDeductionItem[];
  monthly_breakdown: MonthlyDeductionItem[];
  yearly_breakdown: YearlyDeductionItem[];
  recent_deductions: DeductionLedgerRecord[];
}