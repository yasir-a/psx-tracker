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
  onRefreshMarket?: () => void;
  isRefreshingMarket?: boolean;
}

export const Shell: React.FC<ShellProps> = ({
  children,
  portfolios,
  activePortfolioId,
  onSelectPortfolio,
  onOpenCreatePortfolio,
  onOpenTransferModal,
  onDeletePortfolio,
  onRefreshMarket,
  isRefreshingMarket,
}) => {
  const [activeTab, setActiveTab] = useState<NavItemKey>('dashboard');

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 pl-64">
        <Header
          portfolios={portfolios}
          activePortfolioId={activePortfolioId}
          onSelectPortfolio={onSelectPortfolio}
          onOpenCreatePortfolio={onOpenCreatePortfolio}
          onOpenTransferModal={onOpenTransferModal}
          onDeletePortfolio={onDeletePortfolio}
          onRefreshMarket={onRefreshMarket}
          isRefreshingMarket={isRefreshingMarket}
        />

        <main className="flex-1 w-full p-6 mx-auto max-w-7xl">
          {children(activeTab)}
        </main>
      </div>
    </div>
  );
};