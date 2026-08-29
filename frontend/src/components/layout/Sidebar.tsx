import React from 'react';
import { LayoutDashboard, Wallet, ArrowLeftRight, TrendingUp, Receipt, FileText, BarChart3 } from 'lucide-react';
import { clsx } from 'clsx';

export type NavItemKey =
  | 'dashboard'
  | 'holdings'
  | 'transactions'
  | 'corporate_actions'
  | 'analytics'
  | 'market'
  | 'tax_report';

interface SidebarProps {
  activeTab: NavItemKey;
  onSelectTab: (tab: NavItemKey) => void;
}

const navItems: { key: NavItemKey; label: string; icon: React.FC<{ className?: string }> }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { key: 'holdings', label: 'Holdings', icon: Wallet },
  { key: 'transactions', label: 'Transaction Ledger', icon: ArrowLeftRight },
  { key: 'corporate_actions', label: 'Corporate Actions', icon: Receipt },
  { key: 'analytics', label: 'Analytics & KSE-100', icon: BarChart3 },
  { key: 'market', label: 'PSX Market Data', icon: TrendingUp },
  { key: 'tax_report', label: 'FBR Tax Report', icon: FileText },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0 z-30">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-lg">
            P
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">PSX Tracker</h1>
            <p className="text-[10px] text-gray-500 font-medium tracking-wider">PAKISTAN STOCK EXCHANGE</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
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
              <Icon className={clsx('w-5 h-5', isActive ? 'text-emerald-600' : 'text-gray-400')} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-100 text-xs text-gray-400 text-center">
        v0.1.0 • KSE-100 Engine
      </div>
    </aside>
  );
};