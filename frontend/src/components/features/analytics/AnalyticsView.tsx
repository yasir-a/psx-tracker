import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { StatCard } from '../dashboard/StatCard';
import { analyticsService } from '../../../services/analyticsService';
import { AnalyticsResponse } from '../../../types/analytics';

interface AnalyticsViewProps {
  portfolioId: string;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ portfolioId }) => {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        const res = await analyticsService.getAnalyticsSummary(portfolioId);
        setData(res);
      } catch {
        // Handle error
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, [portfolioId]);

  if (isLoading || !data) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  const isAlphaPositive = data.benchmark.alpha_pct >= 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics & KSE-100 Benchmark</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Benchmark alpha/beta, sector concentration risk, and NCCPL Capital Gains Tax schedules
        </p>
      </div>

      {/* Benchmark KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Portfolio Total Return"
          value={`${data.benchmark.portfolio_return_pct >= 0 ? '+' : ''}${data.benchmark.portfolio_return_pct}%`}
          subValue="Active positions"
          isPositive={data.benchmark.portfolio_return_pct >= 0}
        />
        <StatCard
          label="KSE-100 Benchmark Return"
          value={`${data.benchmark.kse100_return_pct >= 0 ? '+' : ''}${data.benchmark.kse100_return_pct}%`}
          subValue="PSX Market Baseline"
          isNeutral={true}
        />
        <StatCard
          label="Portfolio Alpha (α)"
          value={`${isAlphaPositive ? '+' : ''}${data.benchmark.alpha_pct}%`}
          subValue={isAlphaPositive ? 'Outperforming KSE-100' : 'Underperforming KSE-100'}
          isPositive={isAlphaPositive}
        />
        <StatCard
          label="Portfolio Beta (β)"
          value={`${data.benchmark.beta}`}
          subValue="Market Volatility Sensitivity"
          isNeutral={true}
        />
      </div>

      {/* Sector Concentration Visualizer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Sector Concentration & Weighting" subtitle="Diversification exposure across PSX sectors">
          {data.sectors.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-xs">No active stock positions.</div>
          ) : (
            <div className="space-y-4">
              {data.sectors.map((sec) => (
                <div key={sec.sector} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-gray-900 flex items-center gap-1.5">
                      {sec.sector}
                      {sec.is_concentrated && (
                        <span className="text-[10px] text-amber-600 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                          High Concentration (&gt;35%)
                        </span>
                      )}
                    </span>
                    <span className="text-gray-600 font-medium">
                      {sec.weight_pct}% (PKR {sec.market_value.toLocaleString()})
                    </span>
                  </div>
                  {/* Progress Bar */}
                  <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full ${sec.is_concentrated ? 'bg-amber-500' : 'bg-emerald-600'}`}
                      style={{ width: `${Math.min(sec.weight_pct, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* NCCPL Section 37A Capital Gains Tax Schedule */}
        <Card title="NCCPL Capital Gains Tax (CGT) Schedule" subtitle="Section 37A holding period tax estimates">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                <tr>
                  <th className="p-2">Holding Period</th>
                  <th className="p-2">Realized Gain</th>
                  <th className="p-2">Filer Tax (15%)</th>
                  <th className="p-2">Non-Filer (30%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.cgt_schedule.map((item) => (
                  <tr key={item.holding_period} className="hover:bg-gray-50/50">
                    <td className="p-2 font-medium text-gray-900">{item.holding_period}</td>
                    <td className="p-2 font-semibold text-gray-900">PKR {item.realized_gain.toLocaleString()}</td>
                    <td className="p-2 text-emerald-700 font-medium">PKR {item.estimated_tax_filer.toLocaleString()}</td>
                    <td className="p-2 text-rose-700 font-medium">PKR {item.estimated_tax_non_filer.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 p-2.5 bg-gray-50 rounded-lg text-[11px] text-gray-500">
            * Capital Gains Tax is computed on net realized capital gains under NCCPL regulations.
          </div>
        </Card>
      </div>
    </div>
  );
};