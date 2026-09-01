export interface Security {
  symbol: string;
  name: string;
  sector: string;
  security_type: string;
  is_active: boolean;
}

export interface MarketQuote {
  symbol: string;
  name?: string;
  sector?: string;
  current_price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

export interface SecurityFundamentals {
  eps_annual: number;
  eps_quarter: number;
  eps_ytd: number;
  eps_expected: number;
  pe_annual: number;
  pe_expected: number;
  expected_growth_pct: number;
  peg_ratio: number;
  forward_peg: number;
  gross_profit_pct: number;
  operating_profit_pct: number;
  net_profit_pct: number;
  ebitda_pct: number;
  roe_pct: number;
  roa_pct: number;
  roce_pct: number;
  dps_annual: number;
  dps_quarter: number;
  dps_interim: number;
  dividend_yield_pct: number;
  dividend_cover: number;
  payout_ratio_pct: number;
}

export interface TechnicalIndicator {
  name: string;
  params: string;
  value: number;
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
}

export interface MovingAverage {
  name: string;
  label: string;
  value: number;
  signal: 'BUY' | 'SELL';
}

export interface SecurityTechnicals {
  indicators: TechnicalIndicator[];
  pivot_points: Record<string, number>;
  moving_averages: MovingAverage[];
}

export interface AnnouncementItem {
  date: string;
  time: string;
  title: string;
  category: string;
  pdf_url: string;
}

export interface CompanyExecutive {
  title: string;
  name: string;
}

export interface CompanyProfile {
  background: string;
  market_cap: number;
  total_shares: number;
  free_float: number;
  free_float_pct: number;
  executives: CompanyExecutive[];
  address: string;
  website: string;
  registrar: string;
  auditor: string;
}

export interface CompetitorItem {
  symbol: string;
  name: string;
  price: number;
  pe: number;
  market_cap: number;
  dividend_yield: number;
  change: number;
}

export interface SecurityDetails {
  symbol: string;
  name: string;
  sector: string;
  current_price: number;
  change: number;
  change_percent: number;
  open_price: number;
  previous_close: number;
  day_low: number;
  day_high: number;
  week_52_low: number;
  week_52_high: number;
  volume: number;
  bid_price: number;
  bid_volume: number;
  ask_price: number;
  ask_volume: number;
  circuit_lower: number;
  circuit_upper: number;
  is_shariah_compliant: boolean;
  market_status: string;
  fundamentals: SecurityFundamentals;
  technicals: SecurityTechnicals;
  announcements: AnnouncementItem[];
  profile: CompanyProfile;
  competitors: CompetitorItem[];
}