import React from 'react';
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  TrendingUp,
  Receipt,
  FileText,
  BarChart3,
  ShieldCheck,
  Coins,
  ReceiptText,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '../../contexts/AuthContext';

export type NavItemKey =
  | 'dashboard'
  | 'holdings'
  | 'transactions'
  | 'corporate_actions'
  | 'tax_report'
  | 'analytics'
  | 'dividends'
  | 'deductions'
  | 'market'
  | 'admin';

interface SidebarProps {
  activeTab: NavItemKey;
  onSelectTab: (tab: NavItemKey) => void;
}

const navItems: { key: NavItemKey; label: string; icon: React.FC<{ className?: string }> }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { key: 'holdings', label: 'Holdings', icon: Wallet },
  { key: 'transactions', label: 'Transaction Ledger', icon: ArrowLeftRight },
  { key: 'corporate_actions', label: 'Corporate Actions', icon: Receipt },
  { key: 'tax_report', label: 'FBR Tax Report', icon: FileText },
  { key: 'analytics', label: 'Analytics & KSE-100', icon: BarChart3 },
  { key: 'dividends', label: 'Dividend Analysis', icon: Coins },
  { key: 'deductions', label: 'Deduction Analysis', icon: ReceiptText },
  { key: 'market', label: 'PSX Market Data', icon: TrendingUp },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const { user } = useAuth();

  return (
    <aside className="fixed top-0 left-0 z-30 flex flex-col w-64 h-screen bg-white border-r border-gray-200">
      {/* Brand Header */}
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-8 h-8 text-lg font-bold text-white rounded-lg bg-emerald-600">
            P
          </div>
          <div>
            <h1 className="text-base font-bold leading-tight text-gray-900">PSX Tracker</h1>
            <p className="text-[10px] text-gray-500 font-medium tracking-wider">PAKISTAN STOCK EXCHANGE</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onSelectTab(item.key)}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors text-left',
                isActive
                  ? 'bg-emerald-50 text-emerald-700 font-semibold'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon
                className={clsx(
                  'w-5 h-5',
                  isActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-500'
                )}
              />
              <span>{item.label}</span>
            </button>
          );
        })}

        {/* Admin Navigation Item - Visible only to Administrators */}
        {user?.role === 'admin' && (
          <div className="pt-4 mt-4 border-t border-gray-100">
            <div className="px-3 pb-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Administration
            </div>
            <button
              key="admin"
              onClick={() => onSelectTab('admin')}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors text-left',
                activeTab === 'admin'
                  ? 'bg-purple-50 text-purple-700 font-semibold'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <ShieldCheck
                className={clsx(
                  'w-5 h-5',
                  activeTab === 'admin' ? 'text-purple-600' : 'text-purple-500'
                )}
              />
              <span>Admin Dashboard</span>
            </button>
          </div>
        )}
      </nav>
    </aside>
  );
};