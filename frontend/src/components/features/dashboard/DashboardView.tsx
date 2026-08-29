import React from 'react';
import { PortfolioValuationResponse } from '../../../types/portfolio';
import { StatCard } from './StatCard';
import { Card } from '../../ui/Card';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';
import { PlusCircle } from 'lucide-react';

interface DashboardViewProps {
  data: PortfolioValuationResponse;
  onOpenTrade: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  data,
  onOpenTrade,
}) => {
  const { summary, holdings } = data;

  return (
    <div className="space-y-6">
      {/* Top Banner Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Portfolio Dashboard</h2>
          <p className="text-xs text-gray-500 mt-0.5">Real-time valuation with FIFO lot accounting</p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button variant="primary" size="sm" onClick={onOpenTrade}>
            <PlusCircle className="w-4 h-4 mr-1.5" />
            New Transaction
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid - 5 Distinct Columns */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          label="Total Portfolio Value"
          value={`PKR ${summary.total_portfolio_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subValue={`${summary.unrealized_return_pct >= 0 ? '+' : ''}${summary.unrealized_return_pct}% Return`}
          isPositive={summary.unrealized_return_pct >= 0}
        />
        <StatCard
          label="Unrealized P&L"
          value={`PKR ${summary.unrealized_gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subValue={`${summary.unrealized_return_pct >= 0 ? '+' : ''}${summary.unrealized_return_pct}% on active lots`}
          isPositive={summary.unrealized_gain >= 0}
        />
        <StatCard
          label="Realized Profit"
          value={`PKR ${summary.realized_gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subValue={`Fees: PKR ${summary.total_fees_paid.toLocaleString()}`}
          isPositive={summary.realized_gain >= 0}
        />
        <StatCard
          label="Trading Cash"
          value={`PKR ${summary.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subValue="Available for trades"
          isNeutral={true}
        />
        <StatCard
          label="Dividend Income"
          value={`PKR ${summary.total_dividends_earned.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subValue="Net payouts received"
          isPositive={summary.total_dividends_earned > 0}
        />
      </div>

      {/* Holdings Overview Table */}
      <Card title="Current Holdings" subtitle={`${holdings.length} active positions in Pakistan Stock Exchange`}>
        {holdings.length === 0 ? (
          <div className="text-center py-10 text-gray-500">
            <p className="text-sm">No active holdings recorded yet.</p>
            <Button variant="primary" size="sm" className="mt-3" onClick={onOpenTrade}>
              Execute Your First Trade
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs font-semibold uppercase">
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
                    <tr key={h.symbol} className="hover:bg-gray-50/80 transition-colors">
                      <td className="px-4 py-3.5 font-bold text-gray-900">{h.symbol}</td>
                      <td className="px-4 py-3.5 text-gray-700">{h.quantity.toLocaleString()}</td>
                      <td className="px-4 py-3.5 text-gray-700">PKR {h.cost_per_share.toFixed(2)}</td>
                      <td className="px-4 py-3.5 text-gray-900 font-medium">PKR {h.current_price.toFixed(2)}</td>
                      <td className="px-4 py-3.5 font-semibold text-gray-900">PKR {h.market_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                      <td className="px-4 py-3.5">
                        <Badge variant={isUp ? 'green' : 'red'}>
                          {isUp ? '+' : ''}{h.unrealized_return_pct}% (PKR {h.unrealized_gain.toLocaleString()})
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