import React, { useState } from 'react';
import { Sidebar, NavItemKey } from './Sidebar';
import { Header } from './Header';
import { PortfolioListItem } from '../../services/portfolioService';

interface ShellProps {
  children: (activeTab: NavItemKey) => React.ReactNode;
  portfolios: PortfolioListItem[];
  activePortfolioId: string;
  onSelectPortfolio: (id: string) => void;
  onOpenCreatePortfolio: () => void;
  onOpenTransferModal: () => void;
  onDeletePortfolio?: (id: string, name: string) => void;
}

export const Shell: React.FC<ShellProps> = ({
  children,
  portfolios,
  activePortfolioId,
  onSelectPortfolio,
  onOpenCreatePortfolio,
  onOpenTransferModal,
  onDeletePortfolio,
}) => {
  const [activeTab, setActiveTab] = useState<NavItemKey>('dashboard');

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col pl-64">
        <Header
          portfolios={portfolios}
          activePortfolioId={activePortfolioId}
          onSelectPortfolio={onSelectPortfolio}
          onOpenCreatePortfolio={onOpenCreatePortfolio}
          onOpenTransferModal={onOpenTransferModal}
          onDeletePortfolio={onDeletePortfolio}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {children(activeTab)}
        </main>
      </div>
    </div>
  );
};