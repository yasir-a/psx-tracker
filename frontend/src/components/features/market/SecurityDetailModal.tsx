import React, { useEffect, useState } from 'react';
import { SecurityDetails } from '../../../types/market';
import { marketService } from '../../../services/marketService';
import { LiveTab } from './tabs/LiveTab';
import { FundamentalsTab } from './tabs/FundamentalsTab';
import { TechnicalsTab } from './tabs/TechnicalsTab';
import { AnnouncementsTab } from './tabs/AnnouncementsTab';
import { ProfileTab } from './tabs/ProfileTab';
import { CompetitorsTab } from './tabs/CompetitorsTab';
import {
  Radio,
  PieChart,
  Activity,
  Bell,
  Building,
  Users,
  Minus,
  Maximize2,
  Minimize2,
  X,
  Loader2,
  ExternalLink,
} from 'lucide-react';
import { clsx } from 'clsx';

interface SecurityDetailModalProps {
  symbol: string | null;
  isOpen: boolean;
  onClose: () => void;
}

type SubTabKey = 'live' | 'fundamentals' | 'technicals' | 'announcements' | 'profile' | 'competitors';
type WindowMode = 'normal' | 'maximized' | 'minimized';

export const SecurityDetailModal: React.FC<SecurityDetailModalProps> = ({
  symbol,
  isOpen,
  onClose,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<SubTabKey>('live');
  const [details, setDetails] = useState<SecurityDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [windowMode, setWindowMode] = useState<WindowMode>('normal');

  const fetchDetails = async (sym: string) => {
    setIsLoading(true);
    try {
      const res = await marketService.getSecurityDetails(sym);
      setDetails(res);
    } catch {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (symbol && isOpen) {
      fetchDetails(symbol);
      setActiveSubTab('live');
      setWindowMode('normal');
    }
  }, [symbol, isOpen]);

  if (!isOpen || !symbol) return null;

  const isUp = (details?.change || 0) >= 0;

  // 1. Minimized View (Floating Pip in bottom-right corner)
  if (windowMode === 'minimized') {
    return (
      <div className="fixed z-50 flex items-center gap-4 px-4 py-3 text-white bg-gray-900 border border-gray-700 shadow-2xl bottom-5 right-5 rounded-2xl animate-fade-in">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
          <div>
            <div className="text-sm font-bold tracking-wide">{symbol}</div>
            <div className="text-xs text-gray-400">
              PKR {(details?.current_price || 0).toFixed(2)}{' '}
              <span className={isUp ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                {isUp ? '+' : ''}{(details?.change_percent || 0).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5 pl-2 border-l border-gray-700">
          <button
            onClick={() => setWindowMode('normal')}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title="Restore Window"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-rose-400 transition-colors"
            title="Close Terminal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  const subTabs = [
    { key: 'live', label: 'Live', icon: Radio },
    { key: 'fundamentals', label: 'Fundamentals', icon: PieChart },
    { key: 'technicals', label: 'Technicals', icon: Activity },
    { key: 'announcements', label: 'Announcements', icon: Bell },
    { key: 'profile', label: 'Profile', icon: Building },
    { key: 'competitors', label: 'Competitors', icon: Users },
  ] as const;

  const isMaximized = windowMode === 'maximized';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-0 md:p-4">
      {/* Backdrop */}
      {!isMaximized && (
        <div
          className="fixed inset-0 transition-opacity bg-gray-900/50 backdrop-blur-xs"
          onClick={onClose}
        />
      )}

      {/* Main Terminal Dialog */}
      <div
        className={clsx(
          'relative bg-white flex flex-col shadow-2xl z-10 border border-gray-200 transition-all duration-200',
          isMaximized
            ? 'w-screen h-screen max-w-none max-h-none rounded-none inset-0'
            : 'w-full max-w-4xl max-h-[90vh] rounded-2xl overflow-hidden'
        )}
      >
        {/* Window Titlebar Controls */}
        <div className="flex items-center justify-between px-6 py-3.5 border-b border-gray-100 bg-gray-50/70">
          <div className="flex items-center gap-3">
            <span className="bg-emerald-600 text-white font-bold text-xs px-2.5 py-1 rounded-md tracking-wider">
              {symbol}
            </span>
            <div>
              <h3 className="text-sm font-bold text-gray-900">{details?.name || symbol}</h3>
              <p className="text-[10px] text-gray-500 font-medium">PSX LIVE FINANCIAL TERMINAL</p>
            </div>
          </div>

          {/* Window Control Buttons (Minimize, Maximize/Restore, Close) */}
          <div className="flex items-center gap-1 text-gray-400">
            <button
              onClick={() => setWindowMode('minimized')}
              className="p-1.5 rounded-lg hover:bg-gray-200/70 hover:text-gray-700 transition-colors"
              title="Minimize to floating bar"
            >
              <Minus className="w-4 h-4" />
            </button>
            <button
              onClick={() => setWindowMode(isMaximized ? 'normal' : 'maximized')}
              className="p-1.5 rounded-lg hover:bg-gray-200/70 hover:text-gray-700 transition-colors"
              title={isMaximized ? 'Restore window size' : 'Maximize window'}
            >
              {isMaximized ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-rose-100 hover:text-rose-600 transition-colors"
              title="Close window"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Selection Header */}
        <div className="flex items-center gap-1 px-4 overflow-x-auto bg-white border-b border-gray-200">
          {subTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveSubTab(tab.key)}
                className={clsx(
                  'flex items-center gap-1.5 px-3.5 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors border-b-2',
                  isActive
                    ? 'border-emerald-600 text-emerald-700 bg-emerald-50/50'
                    : 'border-transparent text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Body Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-24 text-gray-400">
              <Loader2 className="w-8 h-8 mb-3 animate-spin text-emerald-600" />
              <p className="text-xs font-semibold">Loading real-time PSX intelligence for {symbol}...</p>
            </div>
          ) : !details ? (
            <div className="py-20 text-sm text-center text-gray-500">
              Unable to load security intelligence for {symbol}.
            </div>
          ) : (
            <div className={clsx(isMaximized ? 'max-w-6xl mx-auto' : 'w-full')}>
              {activeSubTab === 'live' && <LiveTab data={details} />}
              {activeSubTab === 'fundamentals' && <FundamentalsTab fundamentals={details.fundamentals} />}
              {activeSubTab === 'technicals' && <TechnicalsTab technicals={details.technicals} />}
              {activeSubTab === 'announcements' && (
                <AnnouncementsTab announcements={details.announcements || []} />
              )}
              {activeSubTab === 'profile' && (
                <ProfileTab 
                  profile={details.profile} 
                  symbol={details.symbol} 
                  name={details.name}
                  sector={details.sector}
                />
              )}
              {activeSubTab === 'competitors' && (
                <CompetitorsTab
                  competitors={details.competitors || []}
                  sector={details.sector}
                  onSelectCompetitor={(peerSym: string) => {
                    fetchDetails(peerSym);
                    setActiveSubTab('live');
                  }}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};