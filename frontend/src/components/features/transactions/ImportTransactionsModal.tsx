import React, { useState, useRef } from 'react';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { Upload, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import { portfolioService, PortfolioListItem } from '../../../services/portfolioService';

interface ImportTransactionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolios: PortfolioListItem[];
  activePortfolioId: string;
  onSuccess: () => void;
}

export const ImportTransactionsModal: React.FC<ImportTransactionsModalProps> = ({
  isOpen,
  onClose,
  portfolios,
  activePortfolioId,
  onSuccess,
}) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>(
    activePortfolioId === 'consolidated' ? (portfolios[0]?.id || '') : activePortfolioId
  );
  const [file, setFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<string[][]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<{ row: number; error: string }[]>([]);
  const [successCount, setSuccessCount] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setErrorDetails([]);
    setSuccessCount(null);
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!selected.name.endsWith('.csv') && !selected.name.endsWith('.txt')) {
      setError('Please upload a valid .csv file');
      return;
    }

    setFile(selected);

    // Read preview of first 5 rows
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split(/\r?\n/).filter((l) => l.trim() !== '');
      const parsed = lines.slice(0, 6).map((line) => line.split(','));
      setPreviewRows(parsed);
    };
    reader.readAsText(selected);
  };

  const downloadSampleTemplate = () => {
    const csvContent =
      'Date,Type,Symbol,Quantity,Price per Share (Rs.),Fees (Rs.),Notes\n' +
      '2026-01-01,CASH_DEPOSIT,,0,500000.00,0,Initial capital deposit\n' +
      '2026-01-05,BUY,SYS,1000,420.00,420.00,Brokerage trade confirmation #1024\n' +
      '2026-01-10,FEE,,0,300.00,0,[UIN FEES] Account maintenance\n' +
      '2026-02-01,SELL,SYS,300,460.00,150.00,Partial profit taking\n';

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'PSX_Transaction_Import_Template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleUpload = async () => {
    if (!file || !selectedPortfolioId) {
      setError('Please choose a file and select an account');
      return;
    }

    setIsLoading(true);
    setError(null);
    setErrorDetails([]);

    try {
      const res = await portfolioService.importTransactions(selectedPortfolioId, file);
      setSuccessCount(res.imported_count);
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1400);
    } catch (err: any) {
      const errRes = err?.response?.data?.error;
      setError(errRes?.message || 'Transaction import failed');
      if (errRes?.details?.errors) {
        setErrorDetails(errRes.details.errors);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Import Transaction Ledger (Excel / CSV)">
      <div className="space-y-4">
        {error && (
          <div className="p-3 text-xs border rounded-lg bg-rose-50 border-rose-200 text-rose-700">
            <div className="flex items-center gap-1.5 font-bold mb-1">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              <span>Import Rejected</span>
            </div>
            <p>{error}</p>
            {errorDetails.length > 0 && (
              <ul className="mt-2 space-y-1 max-h-32 overflow-y-auto pl-4 list-disc text-[11px] text-rose-800">
                {errorDetails.map((e, idx) => (
                  <li key={idx}>
                    Row {e.row}: {e.error}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {successCount !== null && (
          <div className="flex items-center gap-2 p-3 text-xs border rounded-lg bg-emerald-50 border-emerald-200 text-emerald-700">
            <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>Successfully imported {successCount} transactions! Synchronizing state...</span>
          </div>
        )}

        {/* Account Selection */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase">
            Target Broker / Account
          </label>
          <select
            value={selectedPortfolioId}
            onChange={(e) => setSelectedPortfolioId(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold bg-white border border-gray-300 rounded-lg cursor-pointer focus:ring-2 focus:ring-emerald-500"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} (Current Cash: Rs. {p.cash_balance.toLocaleString()})
              </option>
            ))}
          </select>
        </div>

        {/* Drag-and-drop / File input */}
        <div>
          <div
            onClick={() => fileInputRef.current?.click()}
            className="p-6 text-center transition-colors border-2 border-gray-300 border-dashed cursor-pointer hover:border-emerald-500 rounded-xl bg-gray-50/50 hover:bg-emerald-50/30"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv,.txt"
              className="hidden"
            />
            <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p className="text-xs font-semibold text-gray-700">
              {file ? file.name : 'Click to browse or drop CSV dump here'}
            </p>
            <p className="text-[11px] text-gray-400 mt-1">Accepts standard .csv transaction files</p>
          </div>
        </div>

        {/* CSV Preview */}
        {previewRows.length > 0 && (
          <div>
            <p className="text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-1.5">
              File Preview (First {previewRows.length - 1} rows)
            </p>
            <div className="overflow-x-auto border border-gray-200 rounded-lg max-h-36">
              <table className="min-w-full text-[11px] text-left">
                <thead className="sticky top-0 text-gray-600 bg-gray-100">
                  <tr>
                    {previewRows[0].map((h, i) => (
                      <th key={i} className="px-2.5 py-1.5 font-semibold whitespace-nowrap">
                        {h.trim()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-gray-700 divide-y divide-gray-100">
                  {previewRows.slice(1).map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="px-2.5 py-1 whitespace-nowrap">
                          {cell.trim()}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <button
            type="button"
            onClick={downloadSampleTemplate}
            className="inline-flex items-center text-xs font-medium text-emerald-600 hover:text-emerald-700"
          >
            <Download className="w-3.5 h-3.5 mr-1" />
            Download Sample CSV Template
          </button>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleUpload}
              disabled={!file || isLoading}
              isLoading={isLoading}
            >
              Import Ledger
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};