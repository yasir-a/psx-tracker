import React, { useMemo } from 'react';
import { PortfolioValuationResponse } from '../../../types/portfolio';
import { StatCard } from './StatCard';
import { Card } from '../../ui/Card';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';
import { PlusCircle, TrendingUp, TrendingDown, PieChart, Layers, Building2  } from 'lucide-react';
import { PortfolioListItem } from '../../../services/portfolioService';

interface DashboardViewProps {
  data: PortfolioValuationResponse;
  portfolios?: PortfolioListItem[];
  activePortfolioId?: string;
  onOpenTrade: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  data,
  portfolios = [],
  activePortfolioId = 'consolidated',
  onOpenTrade,
}) => {
  const { summary, holdings } = data;

  // 1. Calculate Today's Total Movement across all active positions
  const { todayRupeeGain, todayReturnPct } = useMemo(() => {
    let rupeeGain = 0;
    for (const h of holdings) {
      if (h.quantity > 0 && h.day_change) {
        rupeeGain += h.day_change * h.quantity;
      }
    }
    const prevStockVal = summary.total_stock_value - rupeeGain;
    const returnPct = prevStockVal > 0 ? (rupeeGain / prevStockVal) * 100 : 0;
    return {
      todayRupeeGain: Math.round(rupeeGain * 100) / 100,
      todayReturnPct: Math.round(returnPct * 100) / 100,
    };
  }, [holdings, summary.total_stock_value]);

  // 2. Identify Today's Top Gainer and Top Drag (Loser)
  const { topGainer, topLoser } = useMemo(() => {
    const activeWithMovers = holdings.filter((h) => h.quantity > 0 && h.day_change_pct !== undefined);
    if (activeWithMovers.length === 0) return { topGainer: null, topLoser: null };

    const sortedByDayChange = [...activeWithMovers].sort((a, b) => b.day_change_pct - a.day_change_pct);
    const best = sortedByDayChange[0]?.day_change_pct > 0 ? sortedByDayChange[0] : null;
    const worst = sortedByDayChange[sortedByDayChange.length - 1]?.day_change_pct < 0 ? sortedByDayChange[sortedByDayChange.length - 1] : null;

    return { topGainer: best, topLoser: worst };
  }, [holdings]);

  // 3. Asset Allocation Percentages
  const totalVal = summary.total_portfolio_value;
  const equityPct = totalVal > 0 ? Math.round((summary.total_stock_value / totalVal) * 100) : 0;
  const cashPct = totalVal > 0 ? Math.max(0, 100 - equityPct) : 0;

  // 4. Financial Calculations
  const totalDeposited = summary.total_cash_deposited || 0;
  const totalWithdrawn = summary.total_cash_withdrawn || 0;
  const netInjected = summary.net_injected_capital !== undefined ? summary.net_injected_capital : Math.max(0, totalDeposited - totalWithdrawn);
  const allTimeNet = summary.all_time_net_profit !== undefined ? summary.all_time_net_profit : Math.round((summary.realized_gain + summary.unrealized_gain + summary.total_dividends_earned - summary.total_fees_paid) * 100) / 100;
  const allTimeRoiPct = netInjected > 0 ? Math.round((allTimeNet / netInjected) * 10000) / 100 : 0;
  const dividendYieldPct = summary.total_stock_value > 0 ? Math.round((summary.total_dividends_earned / summary.total_stock_value) * 10000) / 100 : 0;

  return (
    <div className="space-y-6">
      {/* Top Banner Actions */}
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Portfolio Dashboard</h2>
          <p className="text-xs text-gray-500 mt-0.5">Executive financial overview with FIFO lot accounting</p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button variant="primary" size="sm" onClick={onOpenTrade}>
            <PlusCircle className="w-4 h-4 mr-1.5" />
            New Transaction
          </Button>
        </div>
      </div>

      {/* Tier 1: Core Wealth & Performance (5 Columns) */}
      <div>
        <h3 className="mb-3 text-xs font-bold tracking-wider text-gray-400 uppercase">Portfolio Performance & Value</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard
            label="Total Portfolio Value"
            value={`Rs. ${summary.total_portfolio_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`${todayRupeeGain >= 0 ? '+' : ''}Rs. ${Math.abs(todayRupeeGain).toLocaleString()} (${todayReturnPct >= 0 ? '+' : ''}${todayReturnPct.toFixed(2)}%) Today`}
            isPositive={todayRupeeGain >= 0}
          />
          <StatCard
            label="Equities Market Value"
            value={`Rs. ${summary.total_stock_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`${equityPct}% of Portfolio • ${holdings.length} Position${holdings.length !== 1 ? 's' : ''}`}
            isNeutral={true}
          />
          <StatCard
            label="Unrealized P&L"
            value={`Rs. ${summary.unrealized_gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`${summary.unrealized_return_pct >= 0 ? '+' : ''}${summary.unrealized_return_pct.toFixed(2)}% on active lots`}
            isPositive={summary.unrealized_gain >= 0}
          />
          <StatCard
            label="All-Time Net Profit"
            value={`Rs. ${allTimeNet.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`${allTimeRoiPct >= 0 ? '+' : ''}${allTimeRoiPct.toFixed(2)}% Total ROI`}
            isPositive={allTimeNet >= 0}
          />
          <StatCard
            label="Realized Profit"
            value={`Rs. ${summary.realized_gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`From closed trade lots`}
            isPositive={summary.realized_gain >= 0}
          />
        </div>
      </div>

      {/* Tier 2: Capital Flows & Income (5 Columns) */}
      <div>
        <h3 className="mb-3 text-xs font-bold tracking-wider text-gray-400 uppercase">Capital Flows & Cash Liquidity</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard
            label="Trading Cash"
            value={`Rs. ${summary.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`${cashPct}% available for trades`}
            isNeutral={true}
          />
          <StatCard
            label="Total Cash Deposited"
            value={`Rs. ${totalDeposited.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue="Gross capital injected"
            isNeutral={true}
          />
          <StatCard
            label="Total Cash Withdrawn"
            value={`Rs. ${totalWithdrawn.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue="Capital returned to bank"
            isNeutral={true}
          />
          <StatCard
            label="Net Injected Capital"
            value={`Rs. ${netInjected.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue="Deposits less withdrawals"
            isNeutral={true}
          />
          <StatCard
            label="Dividend Income"
            value={`Rs. ${summary.total_dividends_earned.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            subValue={`Yield: ${dividendYieldPct.toFixed(2)}% on stocks`}
            isPositive={summary.total_dividends_earned > 0}
          />
        </div>
      </div>

      {/* Supporting Row: Asset Allocation Strip & Top Movers */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Asset Allocation & Purchasing Power */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <PieChart className="w-4 h-4 text-emerald-600" />
              <h4 className="text-xs font-bold tracking-wider text-gray-900 uppercase">
                Asset Allocation & Broker Distribution
              </h4>
            </div>
            <span className="text-xs font-medium text-gray-500">
              {activePortfolioId === 'consolidated'
                ? `Consolidated (${portfolios.length} Accounts)`
                : portfolios.find((p) => p.id === activePortfolioId)?.name || 'Account'}
            </span>
          </div>

          {/* Allocation Progress Bar: Equities vs Cash */}
          <div className="flex w-full h-3 overflow-hidden bg-gray-100 rounded-full shadow-inner">
            <div
              style={{ width: `${equityPct}%` }}
              className="h-full transition-all duration-500 bg-emerald-600"
              title={`Equities: ${equityPct}%`}
            />
            <div
              style={{ width: `${cashPct}%` }}
              className="h-full transition-all duration-500 bg-blue-500"
              title={`Cash: ${cashPct}%`}
            />
          </div>

          <div className="flex items-center justify-between pt-2 mt-3 text-xs border-t border-gray-100">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 inline-block" />
              <span className="text-gray-600">Equities:</span>
              <span className="font-semibold text-gray-900">
                Rs. {summary.total_stock_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({equityPct}%)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" />
              <span className="text-gray-600">Trading Cash:</span>
              <span className="font-semibold text-gray-900">
                Rs. {summary.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({cashPct}%)
              </span>
            </div>
          </div>

          {/* Individual Broker Breakdown when in Consolidated view or listing active accounts */}
          {portfolios.length > 0 && (
            <div className="pt-3 mt-3 border-t border-gray-100">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">
                <Building2 className="w-3.5 h-3.5 text-gray-400" />
                <span>Broker Accounts Liquidity</span>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                {portfolios.map((p) => {
                  const isSelected = activePortfolioId === p.id;
                  return (
                    <div
                      key={p.id}
                      className={`p-2 rounded-lg border text-xs flex items-center justify-between ${
                        isSelected
                          ? 'bg-emerald-50/70 border-emerald-300 font-semibold text-emerald-900'
                          : 'bg-gray-50/60 border-gray-200/80 text-gray-700'
                      }`}
                    >
                      <div className="mr-2 truncate">
                        <span className="block font-medium truncate">{p.name}</span>
                        <span className="text-[10px] text-gray-400">
                          {p.name.toLowerCase().includes('cdc') ? 'Depository (CDC)' : 'Broker Account'}
                        </span>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="block font-bold text-gray-900">
                          Rs. {p.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                        <span className="text-[9px] text-gray-400">Cash Available</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </Card>

        {/* Top Movers Today */}
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-emerald-600" />
            <h4 className="text-xs font-bold tracking-wider text-gray-900 uppercase">Today's Key Movers</h4>
          </div>

          <div className="space-y-2.5 text-xs">
            {/* Top Gainer */}
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600 shrink-0" />
                <div>
                  <span className="font-bold text-gray-900">{topGainer ? topGainer.symbol : 'None'}</span>
                  <span className="text-[10px] text-gray-500 block">Top Gainer Today</span>
                </div>
              </div>
              <div className="font-semibold text-right text-emerald-700">
                {topGainer ? `+${topGainer.day_change_pct.toFixed(2)}%` : '—'}
              </div>
            </div>

            {/* Top Drag / Loser */}
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-rose-50/50 border border-rose-100">
              <div className="flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-rose-600 shrink-0" />
                <div>
                  <span className="font-bold text-gray-900">{topLoser ? topLoser.symbol : 'None'}</span>
                  <span className="text-[10px] text-gray-500 block">Top Pullback Today</span>
                </div>
              </div>
              <div className="font-semibold text-right text-rose-700">
                {topLoser ? `${topLoser.day_change_pct.toFixed(2)}%` : '—'}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Current Holdings Table */}
      <Card title="Current Holdings" subtitle={`${holdings.length} active positions in Pakistan Stock Exchange`}>
        {holdings.length === 0 ? (
          <div className="py-10 text-center text-gray-500">
            <p className="text-sm">No active holdings recorded yet.</p>
            <Button variant="primary" size="sm" className="mt-3" onClick={onOpenTrade}>
              Execute Your First Trade
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs font-semibold text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Shares</th>
                  <th className="px-4 py-3">Avg Cost</th>
                  <th className="px-4 py-3">Market Price</th>
                  <th className="px-4 py-3">Market Value</th>
                  <th className="px-4 py-3">Unrealized Gain</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {holdings.map((h) => {
                  const isUp = h.unrealized_gain >= 0;
                  return (
                    <tr key={h.symbol} className="transition-colors hover:bg-gray-50/80">
                      <td className="px-4 py-3.5 font-bold text-gray-900">{h.symbol}</td>
                      <td className="px-4 py-3.5 text-gray-700">{h.quantity.toLocaleString()}</td>
                      <td className="px-4 py-3.5 text-gray-700">Rs. {h.cost_per_share.toFixed(2)}</td>
                      <td className="px-4 py-3.5 text-gray-900 font-medium">Rs. {h.current_price.toFixed(2)}</td>
                      <td className="px-4 py-3.5 font-semibold text-gray-900">
                        Rs. {h.market_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3.5">
                        <Badge variant={isUp ? 'green' : 'red'}>
                          {isUp ? '+' : ''}{h.unrealized_return_pct.toFixed(2)}% (Rs. {h.unrealized_gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};