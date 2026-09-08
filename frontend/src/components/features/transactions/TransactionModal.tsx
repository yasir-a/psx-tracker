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
  
  const [type, setType] = useState<'BUY' | 'SELL' | 'CASH_DEPOSIT' | 'CASH_WITHDRAWAL' | 'DIVIDEND_CASH' | 'FEE'>('BUY');
  const [deductionReason, setDeductionReason] = useState<string>('UIN FEES');
  const [depositType, setDepositType] = useState<string>('REGULAR');
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [fee, setFee] = useState('0');
  const [executedAt, setExecutedAt] = useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const DEDUCTION_CATEGORIES = [
    'UIN FEES',
    'CGT DEBIT',
    'Custody Charges',
    'SST FEES',
    'CDC Transaction Fee',
    'Stamp Paper Fee',
    'KYC FEES',
    'SMS Charges',
    'Other Fee / Charge',
  ];

  const isCash = type === 'CASH_DEPOSIT' || type === 'CASH_WITHDRAWAL';
  const isDividend = type === 'DIVIDEND_CASH';
  const isFee = type === 'FEE';

  const availablePortfolios = (isCash || isFee)
    ? portfolios
    : portfolios.filter((p) => !p.name.toLowerCase().includes('cdc'));
    
  useEffect(() => {
    if (editingTransaction) {
      setSelectedPortfolioId(editingTransaction.portfolio_id);
      setType(editingTransaction.transaction_type as any);
      setSymbol(editingTransaction.symbol || '');
      setQuantity(editingTransaction.quantity ? String(editingTransaction.quantity) : '');
      setPrice(String(editingTransaction.price_per_share));
      setFee(String((editingTransaction.brokerage_fee || 0) + (editingTransaction.regulatory_fee || 0)));
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
      execDate.setHours(10, 0, 0, 0);
      let finalNotes = notes || undefined;
      if (isFee) {
        finalNotes = notes ? `[${deductionReason}] ${notes}` : `[${deductionReason}] Account deduction`;
      } else if (type === 'CASH_DEPOSIT' && depositType === 'CGT_CREDIT') {
        finalNotes = notes ? `[CGT Credit] ${notes}` : `[CGT Credit] NCCPL tax credit/refund`;
      }

      if (editingTransaction) {
        const feeVal = parseFloat(fee || '0');
        await portfolioService.updateTransaction(selectedPortfolioId, editingTransaction.id, {
          symbol: (isCash || isFee) ? undefined : symbol.toUpperCase().trim(),
          quantity: (isCash || isFee) ? undefined : parseFloat(quantity),
          price_per_share: parseFloat(price),
          brokerage_fee: (isCash || isFee) ? 0 : feeVal,
          regulatory_fee: isFee ? parseFloat(price) : 0,
          executed_at: execDate.toISOString(),
          notes: finalNotes,
        });
      } else {
        await portfolioService.createTransaction(selectedPortfolioId, {
          transaction_type: type,
          symbol: (isCash || isFee) ? undefined : symbol.toUpperCase().trim(),
          quantity: (isCash || isFee) ? undefined : parseFloat(quantity),
          price_per_share: parseFloat(price),
          brokerage_fee: 0,
          regulatory_fee: isFee ? parseFloat(price) : 0,
          executed_at: execDate.toISOString(),
          notes: finalNotes,
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
      title={editingTransaction ? `Edit ${editingTransaction.transaction_type.replace('_', ' ')}` : 'Record New Transaction'}
    >
      {error && (
        <div className="p-3 mb-4 text-xs border rounded-lg bg-rose-50 border-rose-200 text-rose-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
            Account
          </label>
          <select
            value={selectedPortfolioId}
            disabled={!!editingTransaction}
            onChange={(e) => setSelectedPortfolioId(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold bg-white border border-gray-300 rounded-lg cursor-pointer focus:ring-2 focus:ring-emerald-500 disabled:bg-gray-100"
          >
            {(isDividend ? portfolios : availablePortfolios).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} (Cash: PKR {p.cash_balance.toLocaleString()})
              </option>
            ))}
          </select>
        </div>

        {!editingTransaction && (
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">Type</label>
              <div className="grid grid-cols-5 gap-1.5 bg-gray-100 p-1 rounded-lg">
              {(['BUY', 'SELL', 'CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'FEE'] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setType(t)}
                  className={`py-1.5 text-xs font-medium rounded-md transition-colors ${
                    type === t
                      ? t === 'BUY' || t === 'CASH_DEPOSIT'
                        ? 'bg-emerald-600 text-white shadow-xs'
                        : t === 'FEE'
                        ? 'bg-amber-600 text-white shadow-xs'
                        : 'bg-rose-600 text-white shadow-xs'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {t === 'FEE' ? 'DEDUCTION' : t.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        )}

        <Input
          label="Transaction Date"
          type="date"
          value={executedAt}
          onChange={(e) => setExecutedAt(e.target.value)}
          required
        />
        {type === 'CASH_DEPOSIT' && (
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
              Deposit Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setDepositType('REGULAR')}
                className={`py-1.5 text-xs font-medium rounded-md border transition-colors ${
                  depositType === 'REGULAR'
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold'
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                }`}
              >
                Regular Deposit
              </button>
              <button
                type="button"
                onClick={() => setDepositType('CGT_CREDIT')}
                className={`py-1.5 text-xs font-medium rounded-md border transition-colors ${
                  depositType === 'CGT_CREDIT'
                    ? 'bg-teal-50 text-teal-800 border-teal-300 font-semibold'
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                }`}
              >
                CGT Credit (NCCPL)
              </button>
            </div>
          </div>
        )}
        {/* Deduction Type (Only shown when Deduction/FEE is selected) */}
        {isFee && (
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
              Deduction Type
            </label>
            <select
              value={deductionReason}
              onChange={(e) => setDeductionReason(e.target.value)}
              className="w-full px-3 py-2 text-xs font-semibold bg-white border border-gray-300 rounded-lg cursor-pointer focus:ring-2 focus:ring-amber-500"
            >
              {DEDUCTION_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Symbol & Quantity (Hidden for Cash and Deductions) */}
        {!isCash && !isFee && (
          <>
            <Input
              label="PSX Symbol"
              placeholder="e.g. ENGRO, SYS, FFC, OGDC, DCR"
              value={symbol}
              disabled={!!editingTransaction && isDividend}
              onChange={(e) => setSymbol(e.target.value)}
              required
            />
            <Input
              label={isDividend ? "Eligible Shares" : "Quantity (Shares)"}
              type="number"
              min="1"
              step="1"
              placeholder="e.g. 500"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </>
        )}

        {/* Amount Input */}
        <Input
          label={
            isFee
              ? 'Deduction Amount (PKR)'
              : isCash
              ? 'Amount (PKR)'
              : isDividend
              ? 'Dividend Per Share (DPS in PKR)'
              : 'Price per Share (PKR)'
          }
          type="number"
          step="0.01"
          placeholder="e.g. 300.00"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          required
        />

        {/* Brokerage / Taxes (Hidden for Cash and Deductions) */}
        {!isCash && !isFee && (
          <Input
            label={isDividend ? "Tax & Zakat Deductions (PKR)" : "Brokerage & Regulatory Fees (PKR)"}
            type="number"
            step="0.01"
            placeholder="e.g. 15.00"
            value={fee}
            onChange={(e) => setFee(e.target.value)}
          />
        )}

        <Input
          label="Notes (Optional)"
          placeholder={isFee ? "e.g. Account maintenance or reference" : "e.g. Order reference or execution note"}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <div className="pt-2">
          <Button type="submit" className="w-full" isLoading={isLoading}>
            {editingTransaction ? 'Save Changes' : isFee ? 'Confirm Deduction' : `Confirm ${type.replace('_', ' ')}`}
          </Button>
        </div>
      </form>
    </Modal>
  );
};