import React, { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Shell } from './components/layout/Shell';
import { LoginPage } from './features/auth/LoginPage';
import { RegisterPage } from './features/auth/RegisterPage';
import { DashboardView } from './components/features/dashboard/DashboardView';
import { HoldingsView } from './components/features/holdings/HoldingsView';
import { TransactionsView } from './components/features/transactions/TransactionsView';
import { TransactionModal } from './components/features/transactions/TransactionModal';
import { CorporateActionsView } from './components/features/corporate_actions/CorporateActionsView';
import { MarketView } from './components/features/market/MarketView';
import { TaxReportView } from './components/features/tax/TaxReportView';
import { CreatePortfolioModal } from './components/features/portfolio/CreatePortfolioModal';
import { TransferSharesModal } from './components/features/portfolio/TransferSharesModal';
import { portfolioService, PortfolioListItem } from './services/portfolioService';
import { PortfolioValuationResponse, TransactionRecord } from './types/portfolio';

const MainApp: React.FC = () => {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [activePortfolioId, setActivePortfolioId] = useState<string>('consolidated');
  const [valuationData, setValuationData] = useState<PortfolioValuationResponse | null>(null);
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);
  
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);
  const [isCreateAccountOpen, setIsCreateAccountOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);

  const fetchPortfolios = async () => {
    try {
      const res = await portfolioService.getMyPortfolios();
      setPortfolios(res.portfolios);
      return res.portfolios;
    } catch {
      return [];
    }
  };

  const refreshValuation = async (pid: string) => {
    try {
      const [val, txs] = await Promise.all([
        portfolioService.getValuation(pid),
        portfolioService.getTransactions(pid),
      ]);
      setValuationData(val);
      setTransactions(txs);
    } catch {
      // Handle error
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchPortfolios().then((pList) => {
        if (pList.length > 0) {
          refreshValuation(activePortfolioId);
        }
      });
    }
  }, [isAuthenticated, activePortfolioId]);

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return authMode === 'login' ? (
      <LoginPage onSwitchToRegister={() => setAuthMode('register')} />
    ) : (
      <RegisterPage onSwitchToLogin={() => setAuthMode('login')} />
    );
  }

  return (
    <Shell
      portfolios={portfolios}
      activePortfolioId={activePortfolioId}
      onSelectPortfolio={(pid) => setActivePortfolioId(pid)}
      onOpenCreatePortfolio={() => setIsCreateAccountOpen(true)}
      onOpenTransferModal={() => setIsTransferModalOpen(true)}
    >
      {(activeTab) => {
        if (!valuationData) {
          return (
            <div className="min-h-[50vh] flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
            </div>
          );
        }

        return (
          <>
            {activeTab === 'dashboard' && (
              <DashboardView
                data={valuationData}
                onOpenTrade={() => setIsTradeModalOpen(true)}
              />
            )}

            {activeTab === 'holdings' && <HoldingsView holdings={valuationData.holdings} />}

            {activeTab === 'transactions' && (
              <TransactionsView
                transactions={transactions}
                onOpenTrade={() => setIsTradeModalOpen(true)}
              />
            )}

            {activeTab === 'corporate_actions' && (
              <CorporateActionsView
                portfolioId={activePortfolioId === 'consolidated' ? (portfolios[0]?.id || '') : activePortfolioId}
                onSuccess={() => refreshValuation(activePortfolioId)}
              />
            )}

            {activeTab === 'market' && <MarketView />}

            {activeTab === 'tax_report' && (
              <TaxReportView
                portfolioId={activePortfolioId === 'consolidated' ? (portfolios[0]?.id || '') : activePortfolioId}
              />
            )}

            {/* Modals */}
            <TransactionModal
              isOpen={isTradeModalOpen}
              onClose={() => setIsTradeModalOpen(false)}
              portfolios={portfolios}
              activePortfolioId={activePortfolioId}
              onSuccess={() => {
                fetchPortfolios();
                refreshValuation(activePortfolioId);
              }}
            />

            <CreatePortfolioModal
              isOpen={isCreateAccountOpen}
              onClose={() => setIsCreateAccountOpen(false)}
              onSuccess={async (newId) => {
                await fetchPortfolios();
                setActivePortfolioId(newId);
              }}
            />

            <TransferSharesModal
              isOpen={isTransferModalOpen}
              onClose={() => setIsTransferModalOpen(false)}
              portfolios={portfolios}
              onSuccess={() => refreshValuation(activePortfolioId)}
            />
          </>
        );
      }}
    </Shell>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};

export default App;