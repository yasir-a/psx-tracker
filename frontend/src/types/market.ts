export interface Security {
  symbol: string;
  name: string;
  sector: string;
  security_type: string;
  is_active: boolean;
}

export interface MarketQuote {
  symbol: string;
  current_price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  volume: number;
  updated_at: string;
}