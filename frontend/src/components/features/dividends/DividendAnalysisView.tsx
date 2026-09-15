import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { StatCard } from '../dashboard/StatCard';
import { dividendService } from '../../../services/dividendService';
import { DividendAnalyticsData } from '../../../types/dividend';
import { 
  Coins, 
  TrendingUp, 
  Receipt, 
  Calendar, 
  Filter,
  Loader2,
} from 'lucide-react';

interface DividendAnalysisViewProps {
  portfolioId: string;
  onOpenRecordDividend?: () => void;
}

export const DividendAnalysisView: React.FC<DividendAnalysisViewProps> = ({
  portfolioId,
  onOpenRecordDividend,
}) => {
  const [data, setData] = useState<DividendAnalyticsData | null>(null);
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'total_net' | 'yield_on_cost_pct' | 'portfolio_share_pct'>('total_net');

  const fetchDividends = async () => {
    setIsLoading(true);
    try {
      const res = await dividendService.getDividendAnalytics(portfolioId, selectedYear);
      setData(res);
    } catch {
      // Handled by interceptor
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDividends();
  }, [portfolioId, selectedYear]);

  if (isLoading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <Loader2 className="w-9 h-9 text-emerald-600 animate-spin" />
        <div className="text-center">
          <p className="text-sm font-semibold text-gray-800">Computing Dividend Intelligence</p>
          <p className="text-xs text-gray-500 mt-0.5">Calculating Yield on Cost, cash flows, and FBR tax deductions...</p>
        </div>
      </div>
    );
  }

  const summary = data?.summary;
  const sortedStocks = [...(data?.by_stock || [])].sort((a, b) => b[sortBy] - a[sortBy]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Year Filter */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
              <Coins className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Dividend Analysis & Passive Income</h1>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Track declared payouts, FBR Section 150 tax deductions, Yield on Cost (YoC), and cash flow patterns.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 shadow-xs">
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 text-emerald-600 animate-spin" />
            ) : (
              <Filter className="w-3.5 h-3.5 text-gray-400" />
            )}
            <span className="text-xs font-medium text-gray-600">Tax Year:</span>
            <select
              value={selectedYear}
              disabled={isLoading}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="text-xs font-bold text-gray-900 bg-transparent border-none outline-none cursor-pointer focus:ring-0"
            >
              <option value="all">All-Time</option>
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2024">2023</option>
            </select>
          </div>

          {onOpenRecordDividend && (
            <button
              onClick={onOpenRecordDividend}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors"
            >
              <Receipt className="w-3.5 h-3.5" />
              <span>Record Dividend</span>
            </button>
          )}
        </div>
      </div>

      {/* 5-Card Dividend KPI Bar */}
      {summary && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard
            label="Net Dividends Received"
            value={`Rs. ${summary.total_net_dividends.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`${summary.distribution_count} cash distributions`}
            isPositive={true}
          />
          <StatCard
            label="Gross Declared Dividends"
            value={`Rs. ${summary.total_gross_dividends.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue="Pre-tax declared income"
            isNeutral={true}
          />
          <StatCard
            label="Advance WHT Deducted"
            value={`Rs. ${summary.total_wht_deducted.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`Zakat: Rs. ${summary.total_zakat_deducted.toLocaleString()}`}
            isPositive={false}
          />
          <StatCard
            label="Weighted Yield on Cost"
            value={`${summary.overall_yield_on_cost_pct.toFixed(2)}%`}
            subValue="Cash return on invested cost"
            isPositive={summary.overall_yield_on_cost_pct > 0}
          />
          <StatCard
            label="Projected Annual Income"
            value={`Rs. ${summary.projected_annual_dividend.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`~Rs. ${(summary.projected_annual_dividend / 12).toLocaleString(undefined, { maximumFractionDigits: 0 })} / mo`}
            isNeutral={true}
          />
        </div>
      )}

      {/* Main Grid: Stock Breakdown & Visual Seasonality */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        
        {/* Left 2 Cols: Dividend By Stock */}
        <div className="space-y-4 lg:col-span-2">
          <Card className="p-5">
            <div className="flex flex-col justify-between gap-2 pb-4 border-b border-gray-100 sm:flex-row sm:items-center">
              <div>
                <h2 className="text-sm font-bold text-gray-900">Dividend Income by Stock</h2>
                <p className="text-[11px] text-gray-500">Historical cash yield, acquisition cost basis, and portfolio share</p>
              </div>

              {/* Sorting Buttons */}
              <div className="flex items-center gap-1 p-1 border border-gray-200 rounded-lg bg-gray-50">
                <span className="text-[10px] font-bold text-gray-400 px-1.5 uppercase">Sort:</span>
                <button
                  onClick={() => setSortBy('total_net')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    sortBy === 'total_net' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Net Income
                </button>
                <button
                  onClick={() => setSortBy('yield_on_cost_pct')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    sortBy === 'yield_on_cost_pct' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Yield on Cost
                </button>
                <button
                  onClick={() => setSortBy('portfolio_share_pct')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    sortBy === 'portfolio_share_pct' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Contribution
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
                    <th className="py-2.5 px-3">Company</th>
                    <th className="py-2.5 px-3 text-right">Net Received</th>
                    <th className="py-2.5 px-3 text-right">Yield on Cost</th>
                    <th className="py-2.5 px-3 text-right">Gross (Tax)</th>
                    <th className="py-2.5 px-3 text-right">Income Share</th>
                  </tr>
                </thead>
                <tbody className="text-xs divide-y divide-gray-50">
                  {sortedStocks.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-gray-400">
                        No dividend distributions recorded for the selected period.
                      </td>
                    </tr>
                  ) : (
                    sortedStocks.map((stock) => (
                      <tr key={stock.symbol} className="transition-colors hover:bg-gray-50/70">
                        <td className="px-3 py-3">
                          <div className="font-bold text-gray-900">{stock.symbol}</div>
                          <div className="text-[11px] text-gray-500 truncate max-w-[160px]">{stock.company_name}</div>
                          <div className="text-[10px] text-gray-400 mt-0.5">
                            {stock.payout_count} payout{stock.payout_count > 1 ? 's' : ''} • {stock.current_shares.toLocaleString()} shares held
                          </div>
                        </td>
                        <td className="px-3 py-3 text-right">
                          <div className="font-bold text-emerald-600">
                            Rs. {stock.total_net.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </div>
                          {stock.current_market_value > 0 && (
                            <div className="text-[10px] text-gray-400">
                              Mkt Val: Rs. {stock.current_market_value.toLocaleString()}
                            </div>
                          )}
                        </td>
                        <td className="px-3 py-3 text-right">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700">
                            {stock.yield_on_cost_pct.toFixed(2)}%
                          </span>
                          {stock.current_yield_pct > 0 && (
                            <div className="text-[10px] text-gray-400 mt-0.5">
                              Curr: {stock.current_yield_pct.toFixed(2)}%
                            </div>
                          )}
                        </td>
                        <td className="px-3 py-3 text-right">
                          <div className="font-medium text-gray-700">
                            Rs. {stock.total_gross.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </div>
                          <div className="text-[10px] text-rose-500">
                            -Rs. {stock.total_wht.toLocaleString(undefined, { minimumFractionDigits: 2 })} WHT
                          </div>
                        </td>
                        <td className="px-3 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <span className="font-bold text-gray-800">{stock.portfolio_share_pct.toFixed(1)}%</span>
                          </div>
                          <div className="w-20 ml-auto bg-gray-100 h-1.5 rounded-full mt-1 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-emerald-500"
                              style={{ width: `${Math.min(100, stock.portfolio_share_pct)}%` }}
                            />
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        {/* Right Col: Monthly Cash Flow & Annual History */}
        <div className="space-y-4">
          {/* Monthly Seasonality Bar Chart */}
          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-emerald-600" />
                <h3 className="text-sm font-bold text-gray-900">Monthly Payout Distribution</h3>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              {data?.monthly_breakdown && data.monthly_breakdown.length > 0 ? (
                data.monthly_breakdown.map((m) => {
                  const maxNet = Math.max(...data.monthly_breakdown.map((i) => i.net_amount), 1);
                  const pct = Math.round((m.net_amount / maxNet) * 100);
                  return (
                    <div key={`${m.year}-${m.month}`} className="text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-gray-700">
                          {m.month_name} {m.year}
                        </span>
                        <span className="font-bold text-emerald-600">
                          Rs. {m.net_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="w-full h-2 overflow-hidden bg-gray-100 rounded-full">
                        <div
                          className="h-full transition-all duration-500 rounded-full bg-emerald-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="py-6 text-xs text-center text-gray-400">No monthly distribution data available.</p>
              )}
            </div>
          </Card>

          {/* Annual Passive Income Growth */}
          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                <h3 className="text-sm font-bold text-gray-900">Annual Dividend History</h3>
              </div>
            </div>

            <div className="mt-3 text-xs divide-y divide-gray-100">
              {data?.yearly_breakdown && data.yearly_breakdown.length > 0 ? (
                data.yearly_breakdown.map((y) => (
                  <div key={y.year} className="py-2.5 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-gray-900">Tax Year {y.year}</div>
                      <div className="text-[10px] text-gray-400">
                        Gross: Rs. {y.gross.toLocaleString()} • WHT: Rs. {y.wht.toLocaleString()}
                      </div>
                    </div>
                    <div className="font-bold text-right text-emerald-600">
                      Rs. {y.net.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                ))
              ) : (
                <p className="py-4 text-xs text-center text-gray-400">No annual data available.</p>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Card: Audit Trail of Recent Dividend Distributions */}
      <Card className="p-5">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100">
          <div>
            <h3 className="text-sm font-bold text-gray-900">Recent Dividend Distributions Ledger</h3>
            <p className="text-[11px] text-gray-500">Audited cash payments credited into broker trading cash</p>
          </div>
        </div>

        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Account</th>
                <th className="px-3 py-2">Symbol</th>
                <th className="px-3 py-2 text-right">Eligible Shares</th>
                <th className="px-3 py-2 text-right">DPS (Rs.)</th>
                <th className="px-3 py-2 text-right">Gross Amount</th>
                <th className="px-3 py-2 text-right">WHT Deducted</th>
                <th className="px-3 py-2 text-right">Net Credited</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-gray-50">
              {data?.recent_distributions && data.recent_distributions.length > 0 ? (
                data.recent_distributions.map((tx) => (
                  <tr key={tx.id} className="transition-colors hover:bg-gray-50/70">
                    <td className="py-2.5 px-3 text-gray-600">
                      {new Date(tx.executed_at).toLocaleDateString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className="py-2.5 px-3 text-gray-700 font-medium">{tx.portfolio_name}</td>
                    <td className="py-2.5 px-3">
                      <span className="font-bold text-gray-900 bg-gray-100 px-1.5 py-0.5 rounded text-[11px]">
                        {tx.symbol}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-gray-600">{tx.eligible_shares.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-right font-medium text-gray-800">Rs. {tx.dividend_per_share.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-right text-gray-600">
                      Rs. {tx.gross_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-3 text-right text-rose-500 font-medium">
                      -Rs. {tx.wht_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-emerald-600">
                      Rs. {tx.net_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-6 text-xs text-center text-gray-400">
                    No individual dividend distribution records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};