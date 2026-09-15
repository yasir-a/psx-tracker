import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { StatCard } from '../dashboard/StatCard';
import { deductionService } from '../../../services/deductionService';
import { DeductionAnalyticsData } from '../../../types/deduction';
import { 
  ReceiptText, 
  Calendar, 
  Filter, 
  PlusCircle, 
  Loader2, 
  Building2, 
} from 'lucide-react';

interface DeductionAnalysisViewProps {
  portfolioId: string;
  onOpenRecordDeduction?: () => void;
}

export const DeductionAnalysisView: React.FC<DeductionAnalysisViewProps> = ({
  portfolioId,
  onOpenRecordDeduction,
}) => {
  const [data, setData] = useState<DeductionAnalyticsData | null>(null);
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedGroup, setSelectedGroup] = useState<string>('all');

  const fetchDeductions = async () => {
    setIsLoading(true);
    try {
      const res = await deductionService.getDeductionAnalytics(portfolioId, selectedYear);
      setData(res);
    } catch {
      // Handled by interceptor
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDeductions();
  }, [portfolioId, selectedYear]);

  if (isLoading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <Loader2 className="w-9 h-9 text-rose-600 animate-spin" />
        <div className="text-center">
          <p className="text-sm font-semibold text-gray-800">Auditing Portfolio Deductions & Friction</p>
          <p className="text-xs text-gray-500 mt-0.5">Aggregating broker commissions, SECP levies, CGT, and CDC custody fees...</p>
        </div>
      </div>
    );
  }

  const summary = data?.summary;
  const filteredCategories = (data?.by_category || []).filter(
    (c) => selectedGroup === 'all' || c.group === selectedGroup
  );

  const getGroupBadgeClass = (group: string) => {
    switch (group) {
      case 'Trading Friction':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'Taxes':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'Account & Custody':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Year Filter */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-rose-50 text-rose-600 rounded-lg">
              <ReceiptText className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Deduction & Fee Analysis</h1>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Audit trading commissions, SECP/PSX levies, advance taxes, and broker custody charges.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 shadow-xs">
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 text-rose-600 animate-spin" />
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
            </select>
          </div>

          {onOpenRecordDeduction && (
            <button
              onClick={onOpenRecordDeduction}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Record Deduction</span>
            </button>
          )}
        </div>
      </div>

      {/* 5-Card Deduction KPI Bar */}
      {summary && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard
            label="Total Friction & Deductions"
            value={`Rs. ${summary.total_deductions.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`${summary.total_event_count} fee events`}
            isPositive={false}
          />
          <StatCard
            label="Brokerage Commission"
            value={`Rs. ${summary.total_brokerage_commission.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue="Direct broker trading commission"
            isNeutral={true}
          />
          <StatCard
            label="Regulatory Levies"
            value={`Rs. ${summary.total_regulatory_fees.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue="SECP turnover & PSX charges"
            isNeutral={true}
          />
          <StatCard
            label="Taxes & FBR Deductions"
            value={`Rs. ${summary.total_taxes_paid.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue="Dividend WHT, CGT, SST"
            isPositive={false}
          />
          <StatCard
            label="Trading Fee Drag"
            value={`${summary.fee_drag_pct.toFixed(2)}%`}
            subValue="Cost per 100 Rs. traded"
            isNeutral={true}
          />
        </div>
      )}

      {/* Main Breakdown Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: Category Breakdown Table */}
        <div className="space-y-4 lg:col-span-2">
          <Card className="p-5">
            <div className="flex flex-col justify-between gap-2 pb-4 border-b border-gray-100 sm:flex-row sm:items-center">
              <div>
                <h2 className="text-sm font-bold text-gray-900">Deductions by Category</h2>
                <p className="text-[11px] text-gray-500">Distribution of fees across institutional groups</p>
              </div>

              {/* Group Filter Tabs */}
              <div className="flex items-center gap-1 p-1 border border-gray-200 rounded-lg bg-gray-50">
                <button
                  onClick={() => setSelectedGroup('all')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    selectedGroup === 'all' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setSelectedGroup('Trading Friction')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    selectedGroup === 'Trading Friction' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Trading
                </button>
                <button
                  onClick={() => setSelectedGroup('Taxes')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    selectedGroup === 'Taxes' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Taxes
                </button>
                <button
                  onClick={() => setSelectedGroup('Account & Custody')}
                  className={`text-[11px] px-2 py-0.5 rounded font-medium transition-colors ${
                    selectedGroup === 'Account & Custody' ? 'bg-white shadow-xs text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Custody
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
                    <th className="py-2.5 px-3">Deduction Type</th>
                    <th className="py-2.5 px-3">Group</th>
                    <th className="py-2.5 px-3">Recipient</th>
                    <th className="py-2.5 px-3 text-right">Events</th>
                    <th className="py-2.5 px-3 text-right">Total Amount</th>
                    <th className="py-2.5 px-3 text-right">Share</th>
                  </tr>
                </thead>
                <tbody className="text-xs divide-y divide-gray-50">
                  {filteredCategories.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-400">
                        No deductions recorded for the selected period.
                      </td>
                    </tr>
                  ) : (
                    filteredCategories.map((cat) => (
                      <tr key={cat.category} className="transition-colors hover:bg-gray-50/70">
                        <td className="px-3 py-3">
                          <span className="font-bold text-gray-900">{cat.category}</span>
                        </td>
                        <td className="px-3 py-3">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${getGroupBadgeClass(cat.group)}`}>
                            {cat.group}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-gray-500 text-[11px]">{cat.recipient}</td>
                        <td className="px-3 py-3 font-medium text-right text-gray-600">{cat.count}</td>
                        <td className="px-3 py-3 font-bold text-right text-rose-600">
                          Rs. {cat.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-3 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <span className="font-bold text-gray-700">{cat.share_pct.toFixed(1)}%</span>
                          </div>
                          <div className="w-16 ml-auto bg-gray-100 h-1.5 rounded-full mt-1 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-rose-500"
                              style={{ width: `${Math.min(100, cat.share_pct)}%` }}
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

        {/* Right Col: Broker Cost Breakdown & Monthly Timeline */}
        <div className="space-y-4">
          {/* Per-Broker Cost Distribution */}
          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-rose-600" />
                <h3 className="text-sm font-bold text-gray-900">Cost by Broker Account</h3>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              {data?.by_account && data.by_account.length > 0 ? (
                data.by_account.map((b) => (
                  <div key={b.portfolio_id} className="p-3 bg-gray-50/70 border border-gray-100 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-gray-900">{b.portfolio_name}</span>
                      <span className="text-xs font-bold text-rose-600">
                        Rs. {b.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-gray-500">
                      <span>Trading: Rs. {b.trading_fees.toLocaleString()}</span>
                      <span>Custody/Taxes: Rs. {(b.taxes + b.account_fees).toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-rose-500"
                        style={{ width: `${Math.min(100, b.share_pct)}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="py-4 text-xs text-center text-gray-400">No broker fee data available.</p>
              )}
            </div>
          </Card>

          {/* Monthly Cost Seasonality Bar Chart */}
          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-rose-600" />
                <h3 className="text-sm font-bold text-gray-900">Monthly Friction Trend</h3>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              {data?.monthly_breakdown && data.monthly_breakdown.length > 0 ? (
                data.monthly_breakdown.map((m) => {
                  const maxAmount = Math.max(...data.monthly_breakdown.map((i) => i.total_amount), 1);
                  const pct = Math.round((m.total_amount / maxAmount) * 100);
                  return (
                    <div key={`${m.year}-${m.month}`} className="text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-gray-700">
                          {m.month_name} {m.year}
                        </span>
                        <span className="font-bold text-rose-600">
                          Rs. {m.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="w-full h-2 overflow-hidden bg-gray-100 rounded-full">
                        <div
                          className="h-full transition-all duration-500 rounded-full bg-rose-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="py-6 text-xs text-center text-gray-400">No monthly fee data recorded.</p>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Card: Audit Trail of Recent Deductions */}
      <Card className="p-5">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100">
          <div>
            <h3 className="text-sm font-bold text-gray-900">Recent Deductions Ledger</h3>
            <p className="text-[11px] text-gray-500">Audited trail of individual fees, commissions, and tax charges</p>
          </div>
        </div>

        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Account</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">Symbol</th>
                <th className="px-3 py-2">Recipient</th>
                <th className="px-3 py-2">Notes / Reason</th>
                <th className="px-3 py-2 text-right">Amount (Rs.)</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-gray-50">
              {data?.recent_deductions && data.recent_deductions.length > 0 ? (
                data.recent_deductions.map((tx) => (
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
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${getGroupBadgeClass(tx.group)}`}>
                        {tx.category}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-bold text-gray-900 bg-gray-100 px-1.5 py-0.5 rounded text-[11px]">
                        {tx.symbol}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-gray-500">{tx.recipient}</td>
                    <td className="py-2.5 px-3 text-gray-600 max-w-xs truncate">{tx.notes || '—'}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-rose-600">
                      Rs. {tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-6 text-xs text-center text-gray-400">
                    No deduction records found for this period.
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