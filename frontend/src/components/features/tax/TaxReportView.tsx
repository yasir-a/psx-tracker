import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { StatCard } from '../dashboard/StatCard';
import { portfolioService } from '../../../services/portfolioService';

interface TaxReportViewProps {
  portfolioId: string;
}

export const TaxReportView: React.FC<TaxReportViewProps> = ({ portfolioId }) => {
  const [report, setReport] = useState<any>(null);
  const [taxYear, setTaxYear] = useState<number>(2026);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await portfolioService.getTaxReport(portfolioId, taxYear);
        setReport(data);
      } catch {
        // Handle error
      }
    };
    fetchReport();
  }, [portfolioId, taxYear]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">FBR Section 150 Tax Report</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Annual summary of dividend income and advance withholding tax paid
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={taxYear}
            onChange={(e) => setTaxYear(parseInt(e.target.value))}
            className="px-3 py-1.5 text-xs font-semibold border border-gray-300 rounded-lg bg-white shadow-xs focus:ring-2 focus:ring-emerald-500"
          >
            {[2026, 2025, 2024].map((y) => (
              <option key={y} value={y}>Tax Year {y}</option>
            ))}
          </select>
        </div>
      </div>

      {report && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            label="Total Gross Dividends"
            value={`PKR ${report.total_gross_dividend.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`${report.dividend_count} distributions recorded`}
            isNeutral={true}
          />
          <StatCard
            label="Advance WHT Paid"
            value={`PKR ${report.total_withholding_tax_paid.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue="Claimable on FBR Return"
            isPositive={true}
          />
          <StatCard
            label="Net Dividend Income"
            value={`PKR ${report.net_dividend_income.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            subValue={`Zakat Deducted: PKR ${report.total_zakat_deducted.toLocaleString()}`}
            isNeutral={true}
          />
        </div>
      )}

      <Card title={`FBR Tax Summary — Tax Year ${taxYear}`}>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 text-xs space-y-2">
          <p className="font-semibold text-gray-900">FBR Tax Return Filing Reference:</p>
          <p className="text-gray-600 leading-relaxed">
            Under <strong>Section 150 of the Income Tax Ordinance 2001</strong>, tax deducted at source from dividends
            is an adjustable advance tax for Filers (15%) or full and final tax for Non-Filers (30%).
            Use the figures above when submitting your annual wealth and income return in Iris.
          </p>
        </div>
      </Card>
    </div>
  );
};