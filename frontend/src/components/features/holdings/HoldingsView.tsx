import React, { useState } from 'react';
import { Holding } from '../../../types/portfolio';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { ChevronDown, ChevronRight, Layers } from 'lucide-react';
import { PortfolioBreakdown } from './PortfolioBreakdown';

interface HoldingsViewProps {
  holdings: Holding[];
  portfolioName?: string;
}

export const HoldingsView: React.FC<HoldingsViewProps> = ({
  holdings,
  portfolioName = 'Portfolio',
}) => {
  const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null);

  const toggleExpand = (sym: string) => {
    setExpandedSymbol((prev) => (prev === sym ? null : sym));
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Portfolio Holdings</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Detailed cost basis, FIFO open tax lots, and allocation breakdown
        </p>
      </div>

      {/* Breakdown Visualization Section */}
      <PortfolioBreakdown holdings={holdings} portfolioName={portfolioName} />

      {/* Holdings Detailed Table */}
      <Card title="Holdings Detail" subtitle={`${holdings.length} active positions with FIFO tax lots`}>
        {holdings.length === 0 ? (
          <div className="py-10 text-sm text-center text-gray-500">
            No active holdings found in this portfolio.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs font-semibold text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">Security</th>
                  <th className="px-4 py-3">Sector</th>
                  <th className="px-4 py-3">Quantity</th>
                  <th className="px-4 py-3">Avg Cost/Sh</th>
                  <th className="px-4 py-3">Market Price</th>
                  <th className="px-4 py-3">Total Cost</th>
                  <th className="px-4 py-3">Market Value</th>
                  <th className="px-4 py-3">Unrealized P&L</th>
                  <th className="px-4 py-3 text-right">Tax Lots</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {holdings.map((h) => {
                  const isExpanded = expandedSymbol === h.symbol;
                  const isUp = h.unrealized_gain >= 0;
                  return (
                    <React.Fragment key={h.symbol}>
                      <tr
                        onClick={() => toggleExpand(h.symbol)}
                        className="transition-colors cursor-pointer hover:bg-gray-50/80"
                      >
                        <td className="px-4 py-3.5 font-bold text-gray-900 flex items-center gap-2">
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-emerald-600" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                          <div>
                            <div>{h.symbol}</div>
                            {h.name && <div className="text-[10px] text-gray-400 font-normal">{h.name}</div>}
                          </div>
                        </td>
                        <td className="px-4 py-3.5 text-xs text-gray-600">
                          {h.sector || 'Miscellaneous'}
                        </td>
                        <td className="px-4 py-3.5 text-gray-700">{h.quantity.toLocaleString()}</td>
                        <td className="px-4 py-3.5 text-gray-700">PKR {h.cost_per_share.toFixed(2)}</td>
                        <td className="px-4 py-3.5 font-medium text-gray-900">PKR {h.current_price.toFixed(2)}</td>
                        <td className="px-4 py-3.5 text-gray-700">PKR {h.total_cost_basis.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                        <td className="px-4 py-3.5 font-semibold text-gray-900">PKR {h.market_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                        <td className="px-4 py-3.5">
                          <Badge variant={isUp ? 'green' : 'red'}>
                            {isUp ? '+' : ''}{h.unrealized_return_pct.toFixed(2)}% (PKR {h.unrealized_gain.toLocaleString(undefined,{ minimumFractionDigits: 2, maximumFractionDigits: 2 })})
                          </Badge>
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          <span className="px-2 py-1 text-xs font-semibold rounded text-emerald-600 bg-emerald-50">
                            {h.open_lots.length} lot{h.open_lots.length > 1 ? 's' : ''}
                          </span>
                        </td>
                      </tr>

                      {/* Expandable FIFO Lots Table */}
                      {isExpanded && (
                        <tr className="bg-emerald-50/30">
                          <td colSpan={9} className="p-4">
                            <div className="p-4 bg-white border rounded-lg border-emerald-100 shadow-2xs">
                              <div className="flex items-center gap-2 mb-3">
                                <Layers className="w-4 h-4 text-emerald-600" />
                                <h4 className="text-xs font-bold tracking-wider text-gray-900 uppercase">
                                  FIFO Acquisition Lots for {h.symbol}
                                </h4>
                              </div>
                              <table className="w-full text-xs text-left">
                                <thead className="font-medium text-gray-500 bg-gray-50">
                                  <tr>
                                    <th className="p-2">Acquisition Date</th>
                                    <th className="p-2">Original Qty</th>
                                    <th className="p-2">Remaining Qty</th>
                                    <th className="p-2">Buy Price</th>
                                    <th className="p-2">Effective Cost Basis/Sh</th>
                                    <th className="p-2">Remaining Cost Basis</th>
                                    <th className="p-2">Status</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                  {h.open_lots.map((lot, idx) => (
                                    <tr key={lot.lot_id || idx} className="hover:bg-gray-50/50">
                                      <td className="p-2 text-gray-600">{new Date(lot.executed_at).toLocaleDateString()}</td>
                                      <td className="p-2">{lot.original_quantity.toLocaleString()}</td>
                                      <td className="p-2 font-semibold text-gray-900">{lot.remaining_quantity.toLocaleString()}</td>
                                      <td className="p-2 text-gray-700">PKR {lot.unit_price.toFixed(2)}</td>
                                      <td className="p-2 font-medium text-emerald-700">PKR {lot.cost_basis_per_share.toFixed(4)}</td>
                                      <td className="p-2">PKR {lot.remaining_cost_basis.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                                      <td className="p-2">
                                        <Badge variant={lot.status === 'OPEN' ? 'green' : 'gray'}>
                                          {lot.status}
                                        </Badge>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
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