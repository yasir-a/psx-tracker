import React from 'react';
import { LogOut, User as UserIcon, PlusCircle, ArrowLeftRight } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { PortfolioListItem } from '../../services/portfolioService';

interface HeaderProps {
  portfolios: PortfolioListItem[];
  activePortfolioId: string;
  onSelectPortfolio: (id: string) => void;
  onOpenCreatePortfolio: () => void;
  onOpenTransferModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  portfolios,
  activePortfolioId,
  onSelectPortfolio,
  onOpenCreatePortfolio,
  onOpenTransferModal,
}) => {
  const { user, logout } = useAuth();

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
          <option value="consolidated">🌟 All Accounts (Consolidated Total)</option>
          {portfolios.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} (PKR)
            </option>
          ))}
        </select>

        {/* Transfer & Create Account Buttons */}
        <button
          onClick={onOpenTransferModal}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          title="Move shares between broker and CDC accounts"
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-emerald-600" />
          Transfer Shares
        </button>

        <button
          onClick={onOpenCreatePortfolio}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors"
          title="Add a new broker or CDC account"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          New Account
        </button>
      </div>

      {/* User Actions */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gray-100 border border-gray-300 flex items-center justify-center text-gray-600">
            <UserIcon className="w-4 h-4" />
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-gray-900">{user?.full_name}</p>
            <p className="text-[10px] text-gray-500">{user?.email}</p>
          </div>
        </div>

        <button
          onClick={logout}
          title="Logout"
          className="p-1.5 rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
          aria-label="Logout"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};