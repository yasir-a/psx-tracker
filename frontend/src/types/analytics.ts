export interface BenchmarkData {
  benchmark_name: string;
  portfolio_return_pct: number;
  kse100_return_pct: number;
  alpha_pct: number;
  beta: number;
}

export interface SectorExposureData {
  sector: string;
  market_value: number;
  weight_pct: number;
  stock_count: number;
  is_concentrated: boolean;
}

export interface CGTScheduleData {
  holding_period: string;
  tax_rate_filer_pct: number;
  tax_rate_non_filer_pct: number;
  realized_gain: number;
  estimated_tax_filer: number;
  estimated_tax_non_filer: number;
}

export interface AnalyticsResponse {
  benchmark: BenchmarkData;
  sectors: SectorExposureData[];
  cgt_schedule: CGTScheduleData[];
}