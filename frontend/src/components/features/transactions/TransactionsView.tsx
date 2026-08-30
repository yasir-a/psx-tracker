import React, { useState } from 'react';
import { TransactionRecord } from '../../../types/portfolio';
import { Card } from '../../ui/Card';
import { Button } from '../../ui/Button';
import { PlusCircle, Trash2, Edit2 } from 'lucide-react';

interface TransactionsViewProps {
  transactions: TransactionRecord[];
  onOpenTrade: () => void;
  onEditTransaction?: (tx: TransactionRecord) => void;
  onDeleteTransaction?: (portfolioId: string, transactionId: string) => void;
}

// Color badges for each Account / Broker
const getAccountBadgeClass = (name?: string) => {
  const lower = (name || '').toLowerCase();
  if (lower.includes('darson')) {
    return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  }
  if (lower.includes('bma')) {
    return 'bg-rose-50 text-rose-700 border-rose-200';
  }
  if (lower.includes('cdc')) {
    return 'bg-blue-50 text-blue-700 border-blue-200';
  }
  return 'bg-slate-100 text-slate-700 border-slate-200';
};

// Symmetrical single-line badges for Transaction Types
const getTypeBadgeClass = (type: string) => {
  switch (type) {
    case 'BUY':
    case 'CASH_DEPOSIT':
    case 'BONUS_SHARES':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'SELL':
    case 'CASH_WITHDRAWAL':
      return 'bg-rose-50 text-rose-700 border-rose-200';
    case 'DIVIDEND_CASH':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'TRANSFER_IN':
      return 'bg-teal-50 text-teal-700 border-teal-200';
    case 'TRANSFER_OUT':
      return 'bg-indigo-50 text-indigo-700 border-indigo-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
};

export const TransactionsView: React.FC<TransactionsViewProps> = ({
  transactions,
  onOpenTrade,
  onEditTransaction,
  onDeleteTransaction,
}) => {
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
          <p className="text-xs text-gray-500 mt-0.5">Audit trail of all portfolio and transfer events</p>
        </div>
        <Button variant="primary" size="sm" onClick={onOpenTrade}>
          <PlusCircle className="w-4 h-4 mr-1.5" />
          Add Transaction
        </Button>
      </div>

      <Card>
        {/* Filter Pills */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
          {['ALL', 'BUY', 'SELL', 'DIVIDEND_CASH', 'TRANSFER_OUT', 'TRANSFER_IN', 'CASH_DEPOSIT'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
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
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 text-gray-500 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Account</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Quantity</th>
                  <th className="px-4 py-3">Price/Share</th>
                  <th className="px-4 py-3">Fees</th>
                  <th className="px-4 py-3">Net Amount</th>
                  <th className="px-4 py-3">Notes</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50/60 transition-colors">
                    <td className="px-4 py-3.5 text-xs text-gray-500">
                      {new Date(t.executed_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-semibold border whitespace-nowrap ${getAccountBadgeClass(
                          t.portfolio_name
                        )}`}
                      >
                        {t.portfolio_name || 'Account'}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-flex items-center justify-center px-2.5 py-1 rounded-md text-[11px] font-semibold border whitespace-nowrap uppercase tracking-wider ${getTypeBadgeClass(
                          t.transaction_type
                        )}`}
                      >
                        {t.transaction_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 font-bold text-gray-900">
                      {t.transaction_type === 'CASH_DEPOSIT' || t.transaction_type === 'CASH_WITHDRAWAL'
                        ? 'CASH'
                        : t.symbol || '—'}
                    </td>
                    <td className="px-4 py-3.5 text-gray-700">
                      {t.quantity > 0 ? t.quantity.toLocaleString() : '—'}
                    </td>
                    <td className="px-4 py-3.5 text-gray-700">PKR {t.price_per_share.toFixed(2)}</td>
                    <td className="px-4 py-3.5 text-gray-500">
                      PKR {(t.brokerage_fee + t.regulatory_fee).toFixed(2)}
                    </td>
                    <td className="px-4 py-3.5 font-semibold text-gray-900">
                      PKR {Math.abs(t.net_amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-gray-400 max-w-[200px] truncate">{t.notes || '—'}</td>
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {onEditTransaction && (
                          <button
                            onClick={() => onEditTransaction(t)}
                            className="p-1.5 rounded-md text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                            title="Edit transaction"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                        {onDeleteTransaction && (
                          <button
                            onClick={() => {
                              if (confirm('Are you sure you want to delete this transaction?')) {
                                onDeleteTransaction(t.portfolio_id, t.id);
                              }
                            }}
                            className="p-1.5 rounded-md text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                            title="Delete transaction"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};