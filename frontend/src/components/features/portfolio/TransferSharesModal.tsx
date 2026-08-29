import React, { useState } from 'react';
import { Modal } from '../../ui/Modal';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { portfolioService, PortfolioListItem } from '../../../services/portfolioService';

interface TransferSharesModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolios: PortfolioListItem[];
  onSuccess: () => void;
}

export const TransferSharesModal: React.FC<TransferSharesModalProps> = ({
  isOpen,
  onClose,
  portfolios,
  onSuccess,
}) => {
  const [fromPid, setFromPid] = useState(portfolios[0]?.id || '');
  const [toPid, setToPid] = useState(portfolios[1]?.id || '');
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [cdcFee, setCdcFee] = useState('0');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (fromPid === toPid) {
      setError('Source and Destination accounts must be different');
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      await portfolioService.transferShares({
        from_portfolio_id: fromPid,
        to_portfolio_id: toPid,
        symbol: symbol.toUpperCase().trim(),
        quantity: parseFloat(quantity),
        cdc_transfer_fee: parseFloat(cdcFee || '0'),
        notes: notes || undefined,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Share transfer failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Transfer Shares (Broker ⇄ CDC)">
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">From Account</label>
            <select
              value={fromPid}
              onChange={(e) => setFromPid(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs font-medium bg-white focus:ring-2 focus:ring-emerald-500"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">To Account</label>
            <select
              value={toPid}
              onChange={(e) => setToPid(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs font-medium bg-white focus:ring-2 focus:ring-emerald-500"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <Input
          label="Security Symbol"
          placeholder="e.g. SYS, ENGRO, FFC"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          required
        />

        <Input
          label="Quantity (Shares to Move)"
          type="number"
          min="1"
          placeholder="e.g. 500"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />

        <Input
          label="CDC Transfer Fee / Broker Charges (PKR)"
          type="number"
          step="0.01"
          placeholder="0.00"
          value={cdcFee}
          onChange={(e) => setCdcFee(e.target.value)}
        />

        <Input
          label="Notes / CDC Transaction ID"
          placeholder="e.g. Transferred for long-term safe custody"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <div className="pt-2">
          <Button type="submit" className="w-full" isLoading={isLoading}>
            Confirm Inter-Account Transfer
          </Button>
        </div>
      </form>
    </Modal>
  );
};