import React, { useState } from 'react';
import { Card } from '../../ui/Card';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { portfolioService } from '../../../services/portfolioService';

interface CorporateActionsViewProps {
  portfolioId: string;
  onSuccess: () => void;
}

export const CorporateActionsView: React.FC<CorporateActionsViewProps> = ({
  portfolioId,
  onSuccess,
}) => {
  const [symbol, setSymbol] = useState('');
  const [dps, setDps] = useState('');
  const [taxStatus, setTaxStatus] = useState<'FILER' | 'NON_FILER' | 'CUSTOM'>('FILER');
  const [customTax, setCustomTax] = useState('');
  const [zakat, setZakat] = useState('0');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDividendSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setIsLoading(true);

    try {
      await portfolioService.recordDividend({
        portfolio_id: portfolioId,
        symbol: symbol.toUpperCase().trim(),
        dividend_per_share: parseFloat(dps),
        tax_status: taxStatus,
        custom_tax_rate: taxStatus === 'CUSTOM' ? parseFloat(customTax) : undefined,
        zakat_deducted: parseFloat(zakat || '0'),
      });
      setMessage(`Successfully credited dividend for ${symbol.toUpperCase()}!`);
      setSymbol('');
      setDps('');
      onSuccess();
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to record dividend');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Corporate Actions</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Record Cash Dividends with Withholding Tax (15% Filer / 30% Non-Filer), Bonus & Rights
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Dividend Form */}
        <Card title="Record Cash Dividend" subtitle="Automatically applies FBR Section 150 Withholding Tax">
          {message && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs">
              {message}
            </div>
          )}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleDividendSubmit} className="space-y-4">
            <Input
              label="Symbol"
              placeholder="e.g. ENGRO, SYS"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              required
            />

            <Input
              label="Dividend Per Share (PKR)"
              type="number"
              step="0.01"
              placeholder="e.g. 5.50"
              value={dps}
              onChange={(e) => setDps(e.target.value)}
              required
            />

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
                Withholding Tax Status (FBR)
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { key: 'FILER', label: 'Filer (15%)' },
                  { key: 'NON_FILER', label: 'Non-Filer (30%)' },
                  { key: 'CUSTOM', label: 'Custom %' },
                ].map((t) => (
                  <button
                    key={t.key}
                    type="button"
                    onClick={() => setTaxStatus(t.key as any)}
                    className={`py-2 text-xs font-medium rounded-lg border transition-colors ${
                      taxStatus === t.key
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-700 font-bold'
                        : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {taxStatus === 'CUSTOM' && (
              <Input
                label="Custom Withholding Tax Rate (%)"
                type="number"
                step="0.1"
                placeholder="e.g. 12.5"
                value={customTax}
                onChange={(e) => setCustomTax(e.target.value)}
                required
              />
            )}

            <Input
              label="Zakat Deducted at Source (Optional PKR)"
              type="number"
              step="0.01"
              placeholder="0.00"
              value={zakat}
              onChange={(e) => setZakat(e.target.value)}
            />

            <Button type="submit" className="w-full mt-2" isLoading={isLoading}>
              Apply Cash Dividend & Credit Cash
            </Button>
          </form>
        </Card>

        {/* Corporate Actions Overview Guide */}
        <Card title="PSX Corporate Actions Guide" subtitle="Automated ledger treatment">
          <div className="space-y-3 text-xs text-gray-600 leading-relaxed">
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <h5 className="font-bold text-gray-900 mb-1">💵 Cash Dividends</h5>
              <p>Credited directly to portfolio cash balance after deducting Withholding Tax (15% for Filers, 30% for Non-Filers) and Zakat.</p>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <h5 className="font-bold text-gray-900 mb-1">🎁 Bonus Shares</h5>
              <p>Injected as new tax lots with PKR 0.00 acquisition cost, diluting your overall average cost basis under FIFO.</p>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <h5 className="font-bold text-gray-900 mb-1">📑 Tax Reports</h5>
              <p>Every dividend event records gross receipts and advance tax for effortless annual FBR tax return filing under Section 150.</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};