import React, { useState } from 'react';
import { LogOut, User as UserIcon, PlusCircle, ArrowLeftRight, Trash2, Database } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { PortfolioListItem, portfolioService } from '../../services/portfolioService';

interface HeaderProps {
  portfolios: PortfolioListItem[];
  activePortfolioId: string;
  onSelectPortfolio: (id: string) => void;
  onOpenCreatePortfolio: () => void;
  onOpenTransferModal: () => void;
  onDeletePortfolio?: (id: string, name: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  portfolios,
  activePortfolioId,
  onSelectPortfolio,
  onOpenCreatePortfolio,
  onOpenTransferModal,
  onDeletePortfolio,
}) => {
  const { user, logout } = useAuth();
  const [isBackingUp, setIsBackingUp] = useState(false);

  const totalConsolidatedCash = portfolios.reduce(
    (sum, p) => sum + (p.cash_balance || 0),
    0
  );

  const activePortfolio = portfolios.find((p) => p.id === activePortfolioId);

  const handleBackup = async () => {
    setIsBackingUp(true);
    try {
      const res = await portfolioService.backupDatabase();
      alert(`✅ ${res.message}`);
    } catch (err: any) {
      alert(`❌ ${err?.response?.data?.error?.message || 'Database backup failed'}`);
    } finally {
      setIsBackingUp(false);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-20">
      {/* Portfolio Selector & Actions */}
      <div className="flex items-center gap-3">
        <label htmlFor="portfolio-select" className="text-xs text-gray-500 font-medium">
          Account:
        </label>
        <select
          id="portfolio-select"
          value={activePortfolioId}
          onChange={(e) => onSelectPortfolio(e.target.value)}
          className="px-3 py-1.5 text-xs font-semibold border border-gray-300 rounded-lg bg-emerald-50 text-emerald-800 focus:ring-2 focus:ring-emerald-500 shadow-2xs cursor-pointer"
        >
          <option value="consolidated">
            🌟 All Accounts (PKR {totalConsolidatedCash.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
          </option>
          {portfolios.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} (PKR {(p.cash_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
            </option>
          ))}
        </select>

        {/* Transfer Shares */}
        <button
          onClick={onOpenTransferModal}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          title="Move shares between broker and CDC accounts"
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-emerald-600" />
          Transfer Shares
        </button>

        {/* New Account */}
        <button
          onClick={onOpenCreatePortfolio}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors"
          title="Add a new broker or CDC account"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          New Account
        </button>

        {/* Delete Selected Broker Account */}
        {activePortfolioId !== 'consolidated' && activePortfolio && onDeletePortfolio && (
          <button
            onClick={() => onDeletePortfolio(activePortfolio.id, activePortfolio.name)}
            className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
            title={`Delete ${activePortfolio.name}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* User Info, Backup & Logout */}
      <div className="flex items-center gap-3">
        {/* DB Backup Button */}
        <button
          onClick={handleBackup}
          disabled={isBackingUp}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg transition-colors"
          title="Create PostgreSQL database dump on Desktop"
        >
          <Database className="w-3.5 h-3.5 text-emerald-600" />
          {isBackingUp ? 'Backing up...' : 'Backup DB'}
        </button>

        <div className="flex items-center gap-2 text-sm text-gray-700 pl-2 border-l border-gray-200">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
            {user?.full_name?.charAt(0) || <UserIcon className="w-4 h-4" />}
          </div>
          <span className="font-medium hidden sm:inline">{user?.full_name}</span>
        </div>

        <button
          onClick={logout}
          className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="Log Out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};