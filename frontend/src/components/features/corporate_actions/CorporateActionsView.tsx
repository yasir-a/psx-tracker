import React, { useState, useEffect } from 'react';
import { Card } from '../../ui/Card';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { portfolioService, PortfolioListItem } from '../../../services/portfolioService';

interface CorporateActionsViewProps {
  portfolioId: string;
  portfolios: PortfolioListItem[];
  onSuccess: () => void;
}

export const CorporateActionsView: React.FC<CorporateActionsViewProps> = ({
  portfolioId,
  portfolios,
  onSuccess,
}) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>(
    portfolioId === 'consolidated' ? (portfolios[0]?.id || '') : portfolioId
  );
  const [symbol, setSymbol] = useState('');
  const [dps, setDps] = useState('');
  const [taxStatus, setTaxStatus] = useState<'FILER' | 'NON_FILER' | 'CUSTOM'>('FILER');
  const [customTax, setCustomTax] = useState('');
  const [zakat, setZakat] = useState('0');
  const [executedAt, setExecutedAt] = useState(new Date().toISOString().split('T')[0]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (portfolioId !== 'consolidated') {
      setSelectedPortfolioId(portfolioId);
    } else if (portfolios.length > 0) {
      setSelectedPortfolioId(portfolios[0].id);
    }
  }, [portfolioId, portfolios]);

  const handleDividendSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPortfolioId) {
      setError('Please select an account');
      return;
    }
    setError(null);
    setMessage(null);
    setIsLoading(true);

    try {
      const execDate = new Date(executedAt);
      execDate.setHours(10, 0, 0, 0);

      await portfolioService.recordDividend({
        portfolio_id: selectedPortfolioId,
        symbol: symbol.toUpperCase().trim(),
        dividend_per_share: parseFloat(dps),
        tax_status: taxStatus,
        custom_tax_rate: taxStatus === 'CUSTOM' ? parseFloat(customTax) : undefined,
        zakat_deducted: parseFloat(zakat || '0'),
        executed_at: execDate.toISOString(),
      });
      setMessage(`Successfully credited dividend for ${symbol.toUpperCase()} on ${executedAt}!`);
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
        <Card title="Record Cash Dividend" subtitle="Credits dividend earnings net of withholding tax and Zakat">
          {message && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
              {message}
            </div>
          )}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
              {error}
            </div>
          )}

          <form onSubmit={handleDividendSubmit} className="space-y-4">
            {/* Account Selector */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
                Account Holding the Shares
              </label>
              <select
                value={selectedPortfolioId}
                onChange={(e) => setSelectedPortfolioId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs font-semibold bg-white focus:ring-2 focus:ring-emerald-500 cursor-pointer"
              >
                {portfolios.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Dividend Execution Date"
              type="date"
              value={executedAt}
              onChange={(e) => setExecutedAt(e.target.value)}
              required
            />

            <Input
              label="PSX Security Symbol"
              placeholder="e.g. ENGRO, SYS, FFC, OGDC, DCR"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              required
            />

            <Input
              label="Dividend Per Share (DPS in PKR)"
              type="number"
              step="0.01"
              placeholder="e.g. 0.66"
              value={dps}
              onChange={(e) => setDps(e.target.value)}
              required
            />

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
                Tax Filer Status (Withholding Tax)
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { key: 'FILER', label: 'Filer (15% WHT)' },
                  { key: 'NON_FILER', label: 'Non-Filer (30% WHT)' },
                  { key: 'CUSTOM', label: 'Custom Tax Rate' },
                ].map((item) => (
                  <button
                    key={item.key}
                    type="button"
                    onClick={() => setTaxStatus(item.key as any)}
                    className={`py-2 px-3 text-xs font-medium rounded-lg border transition-colors ${
                      taxStatus === item.key
                        ? 'bg-emerald-600 text-white border-emerald-600'
                        : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {taxStatus === 'CUSTOM' && (
              <Input
                label="Custom Withholding Tax Rate (%)"
                type="number"
                step="0.1"
                placeholder="e.g. 7.5"
                value={customTax}
                onChange={(e) => setCustomTax(e.target.value)}
                required
              />
            )}

            <Input
              label="Zakat Deducted at Source (PKR, Optional)"
              type="number"
              step="0.01"
              placeholder="e.g. 0.00"
              value={zakat}
              onChange={(e) => setZakat(e.target.value)}
            />

            <Button type="submit" variant="primary" className="w-full" isLoading={isLoading}>
              Apply Cash Dividend
            </Button>
          </form>
        </Card>

        {/* Corporate Actions Overview Guide */}
        <Card title="Corporate Actions Guide" subtitle="Taxation & accounting methodology">
          <div className="space-y-4 text-xs text-gray-600 leading-relaxed">
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-800">
              <span className="font-bold">FBR Section 150 Dividend Rules:</span>
              <p className="mt-1">
                Dividends are subject to 15% WHT for active tax filers and 30% WHT for non-filers. Net dividend income is credited and tracked separately for annual tax returns.
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 text-blue-800">
              <span className="font-bold">Bonus Shares & Stock Splits:</span>
              <p className="mt-1">
                Bonus shares and splits increase share quantity while adjusting lot cost basis per share proportionally without taxable capital events.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};