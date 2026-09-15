export interface DividendSummary {
  total_gross_dividends: number;
  total_wht_deducted: number;
  total_zakat_deducted: number;
  total_net_dividends: number;
  overall_yield_on_cost_pct: number;
  overall_current_yield_pct: number;
  distribution_count: number;
  projected_annual_dividend: number;
}

export interface StockDividendRecord {
  symbol: string;
  company_name: string;
  payout_count: number;
  total_gross: number;
  total_wht: number;
  total_zakat: number;
  total_net: number;
  current_shares: number;
  invested_cost: number;
  current_market_value: number;
  yield_on_cost_pct: number;
  current_yield_pct: number;
  portfolio_share_pct: number;
  last_payment_date: string;
}

export interface MonthlyDividendItem {
  year: number;
  month: number;
  month_name: string;
  net_amount: number;
}

export interface YearlyDividendItem {
  year: number;
  gross: number;
  wht: number;
  zakat: number;
  net: number;
}

export interface DividendDistributionLog {
  id: string;
  executed_at: string;
  portfolio_name: string;
  symbol: string;
  eligible_shares: number;
  dividend_per_share: number;
  gross_amount: number;
  wht_amount: number;
  zakat_amount: number;
  net_amount: number;
  notes: string;
}

export interface DividendAnalyticsData {
  summary: DividendSummary;
  by_stock: StockDividendRecord[];
  monthly_breakdown: MonthlyDividendItem[];
  yearly_breakdown: YearlyDividendItem[];
  recent_distributions: DividendDistributionLog[];
}