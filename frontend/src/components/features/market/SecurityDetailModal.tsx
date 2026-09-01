import React, { useEffect, useState } from 'react';
import { SecurityDetails } from '../../../types/market';
import { marketService } from '../../../services/marketService';
import { Modal } from '../../ui/Modal';
import { LiveTab } from './tabs/LiveTab';
import { FundamentalsTab } from './tabs/FundamentalsTab';
import { TechnicalsTab } from './tabs/TechnicalsTab';
import { AnnouncementsTab } from './tabs/AnnouncementsTab';
import { ProfileTab } from './tabs/ProfileTab';
import { CompetitorsTab } from './tabs/CompetitorsTab';
import { Radio, PieChart, Activity, Bell, Building, Users } from 'lucide-react';

interface SecurityDetailModalProps {
  symbol: string | null;
  isOpen: boolean;
  onClose: () => void;
}

type SubTabKey = 'live' | 'fundamentals' | 'technicals' | 'announcements' | 'profile' | 'competitors';

export const SecurityDetailModal: React.FC<SecurityDetailModalProps> = ({
  symbol,
  isOpen,
  onClose,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<SubTabKey>('live');
  const [details, setDetails] = useState<SecurityDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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
    }
  }, [symbol, isOpen]);

  if (!isOpen || !symbol) return null;

  const subTabs = [
    { key: 'live', label: 'Live', icon: Radio },
    { key: 'fundamentals', label: 'Fundamentals', icon: PieChart },
    { key: 'technicals', label: 'Technicals', icon: Activity },
    { key: 'announcements', label: 'Announcements', icon: Bell },
    { key: 'profile', label: 'Profile', icon: Building },
    { key: 'competitors', label: 'Competitors', icon: Users },
  ] as const;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={details ? `${details.name} (${details.symbol})` : 'Loading Security...'}>
      <div className="space-y-5 -mt-2">
        {/* Terminal Sub-Tab Navigation */}
        <div className="flex gap-1.5 overflow-x-auto border-b border-gray-200 pb-2 scrollbar-none">
          {subTabs.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveSubTab(key)}
              className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                activeSubTab === key
                  ? 'bg-amber-500 text-gray-950 shadow-xs'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>

        {isLoading || !details ? (
          <div className="py-20 flex flex-col items-center justify-center text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mb-3"></div>
            <p className="text-xs font-semibold">Loading Market Intelligence for {symbol}...</p>
          </div>
        ) : (
          <div className="max-h-[72vh] overflow-y-auto pr-1">
            {activeSubTab === 'live' && <LiveTab data={details} />}
            {activeSubTab === 'fundamentals' && <FundamentalsTab fundamentals={details.fundamentals} />}
            {activeSubTab === 'technicals' && <TechnicalsTab technicals={details.technicals} />}
            {activeSubTab === 'announcements' && <AnnouncementsTab announcements={details.announcements} />}
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
                competitors={details.competitors}
                sector={details.sector}
                onSelectCompetitor={(sym) => fetchDetails(sym)}
              />
            )}
          </div>
        )}
      </div>
    </Modal>
  );
};