import React, { useEffect, useState } from 'react';
import { Modal } from '../../ui/Modal';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { portfolioService, PortfolioListItem } from '../../../services/portfolioService';
import { TransactionRecord } from '../../../types/portfolio';

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolios: PortfolioListItem[];
  activePortfolioId: string;
  onSuccess: () => void;
  editingTransaction?: TransactionRecord | null;
}

export const TransactionModal: React.FC<TransactionModalProps> = ({
  isOpen,
  onClose,
  portfolios,
  activePortfolioId,
  onSuccess,
  editingTransaction,
}) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>(
    activePortfolioId === 'consolidated' ? (portfolios[0]?.id || '') : activePortfolioId
  );
  const [type, setType] = useState<'BUY' | 'SELL' | 'CASH_DEPOSIT' | 'CASH_WITHDRAWAL'>('BUY');
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [fee, setFee] = useState('0');
  const [executedAt, setExecutedAt] = useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const isCash = type === 'CASH_DEPOSIT' || type === 'CASH_WITHDRAWAL';

  // Available accounts based on transaction type
  // Cash deposit/withdrawal is allowed on all accounts including CDC.
  // Buy/Sell is restricted to broker accounts.
  const availablePortfolios = isCash
    ? portfolios
    : portfolios.filter((p) => !p.name.toLowerCase().includes('cdc'));

  useEffect(() => {
    if (editingTransaction) {
      setSelectedPortfolioId(editingTransaction.portfolio_id);
      setType(editingTransaction.transaction_type as any);
      setSymbol(editingTransaction.symbol || '');
      setQuantity(editingTransaction.quantity ? String(editingTransaction.quantity) : '');
      setPrice(String(editingTransaction.price_per_share));
      setFee(String(editingTransaction.brokerage_fee || 0));
      setExecutedAt(editingTransaction.executed_at.split('T')[0]);
      setNotes(editingTransaction.notes || '');
    } else {
      if (activePortfolioId !== 'consolidated') {
        setSelectedPortfolioId(activePortfolioId);
      } else if (availablePortfolios.length > 0) {
        setSelectedPortfolioId(availablePortfolios[0].id);
      }
      setSymbol('');
      setQuantity('');
      setPrice('');
      setFee('0');
      setExecutedAt(new Date().toISOString().split('T')[0]);
      setNotes('');
    }
  }, [editingTransaction, activePortfolioId, portfolios, isOpen, type]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPortfolioId) {
      setError('Please select a valid account');
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      const execDate = new Date(executedAt);
      execDate.setHours(10, 0, 0, 0); // Default market trading hour

      if (editingTransaction) {
        await portfolioService.updateTransaction(selectedPortfolioId, editingTransaction.id, {
          symbol: isCash ? undefined : symbol.toUpperCase().trim(),
          quantity: isCash ? undefined : parseFloat(quantity),
          price_per_share: parseFloat(price),
          brokerage_fee: isCash ? 0 : parseFloat(fee || '0'),
          notes: notes || undefined,
        });
      } else {
        await portfolioService.createTransaction(selectedPortfolioId, {
          transaction_type: type,
          symbol: isCash ? undefined : symbol.toUpperCase().trim(),
          quantity: isCash ? undefined : parseFloat(quantity),
          price_per_share: parseFloat(price),
          brokerage_fee: isCash ? 0 : parseFloat(fee || '0'),
          executed_at: execDate.toISOString(),
          notes: notes || undefined,
        });
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Transaction failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editingTransaction ? 'Edit Transaction' : 'Record New Transaction'}
    >
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Account Selector */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
            Account
          </label>
          <select
            value={selectedPortfolioId}
            disabled={!!editingTransaction}
            onChange={(e) => setSelectedPortfolioId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs font-semibold bg-white focus:ring-2 focus:ring-emerald-500 disabled:bg-gray-100 cursor-pointer"
          >
            {availablePortfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} (Cash: PKR {p.cash_balance.toLocaleString()})
              </option>
            ))}
          </select>
        </div>

        {/* Transaction Type Buttons */}
        {!editingTransaction && (
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">Type</label>
            <div className="grid grid-cols-4 gap-1.5 bg-gray-100 p-1 rounded-lg">
              {(['BUY', 'SELL', 'CASH_DEPOSIT', 'CASH_WITHDRAWAL'] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setType(t)}
                  className={`py-1.5 text-xs font-medium rounded-md transition-colors ${
                    type === t
                      ? t === 'BUY' || t === 'CASH_DEPOSIT'
                        ? 'bg-emerald-600 text-white shadow-xs'
                        : 'bg-rose-600 text-white shadow-xs'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {t.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Execution Date Picker */}
        <Input
          label="Transaction Date"
          type="date"
          value={executedAt}
          onChange={(e) => setExecutedAt(e.target.value)}
          required
        />

        {!isCash && (
          <Input
            label="PSX Symbol"
            placeholder="e.g. ENGRO, SYS, FFC, OGDC"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            required
          />
        )}

        {!isCash && (
          <Input
            label="Quantity (Shares)"
            type="number"
            min="1"
            step="1"
            placeholder="e.g. 500"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
          />
        )}

        <Input
          label={isCash ? 'Amount (PKR)' : 'Price per Share (PKR)'}
          type="number"
          step="0.01"
          placeholder="e.g. 550.00"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          required
        />

        {!isCash && (
          <Input
            label="Brokerage & Regulatory Fees (PKR)"
            type="number"
            step="0.01"
            placeholder="e.g. 15.00"
            value={fee}
            onChange={(e) => setFee(e.target.value)}
          />
        )}

        <Input
          label="Notes (Optional)"
          placeholder="e.g. Order reference or execution note"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <div className="pt-2">
          <Button type="submit" className="w-full" isLoading={isLoading}>
            {editingTransaction ? 'Save Changes' : `Confirm ${type.replace('_', ' ')}`}
          </Button>
        </div>
      </form>
    </Modal>
  );
};