import React, { useState } from 'react';
import { TransactionRecord } from '../../../types/portfolio';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { Button } from '../../ui/Button';
import { PlusCircle } from 'lucide-react';

interface TransactionsViewProps {
  transactions: TransactionRecord[];
  onOpenTrade: () => void;
}

export const TransactionsView: React.FC<TransactionsViewProps> = ({ transactions, onOpenTrade }) => {
  const [filterType, setFilterType] = useState<string>('ALL');

  const filtered = transactions.filter((t) => {
    if (filterType === 'ALL') return true;
    return t.transaction_type === filterType;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Transaction Ledger</h2>
          <p className="text-xs text-gray-500 mt-0.5">Immutable audit trail of all portfolio events</p>
        </div>
        <Button variant="primary" size="sm" onClick={onOpenTrade}>
          <PlusCircle className="w-4 h-4 mr-1.5" />
          Add Transaction
        </Button>
      </div>

      <Card>
        {/* Filter Pills */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
          {['ALL', 'BUY', 'SELL', 'DIVIDEND_CASH', 'BONUS_SHARES', 'CASH_DEPOSIT'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                filterType === t
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t.replace('_', ' ')}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-10 text-gray-500 text-sm">No transactions found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs font-semibold uppercase">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Quantity</th>
                  <th className="px-4 py-3">Price/Share</th>
                  <th className="px-4 py-3">Fees</th>
                  <th className="px-4 py-3">Net Amount</th>
                  <th className="px-4 py-3">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((t) => {
                  const isBuy = t.transaction_type === 'BUY' || t.transaction_type === 'CASH_DEPOSIT';
                  return (
                    <tr key={t.id} className="hover:bg-gray-50/60 transition-colors">
                      <td className="px-4 py-3 text-xs text-gray-500">{new Date(t.executed_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3">
                        <Badge variant={isBuy ? 'green' : 'blue'}>
                          {t.transaction_type.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 font-bold text-gray-900">{t.symbol || '—'}</td>
                      <td className="px-4 py-3 text-gray-700">{t.quantity > 0 ? t.quantity.toLocaleString() : '—'}</td>
                      <td className="px-4 py-3 text-gray-700">PKR {t.price_per_share.toFixed(2)}</td>
                      <td className="px-4 py-3 text-gray-500">PKR {(t.brokerage_fee + t.regulatory_fee).toFixed(2)}</td>
                      <td className="px-4 py-3 font-semibold text-gray-900">PKR {Math.abs(t.net_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                      <td className="px-4 py-3 text-xs text-gray-400">{t.notes || '—'}</td>
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