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
import { AnalyticsView } from './components/features/analytics/AnalyticsView';
import { MarketView } from './components/features/market/MarketView';
import { TaxReportView } from './components/features/tax/TaxReportView';
import { AdminView } from './components/features/admin/AdminView';
import { CreatePortfolioModal } from './components/features/portfolio/CreatePortfolioModal';
import { TransferSharesModal } from './components/features/portfolio/TransferSharesModal';
import { portfolioService, PortfolioListItem } from './services/portfolioService';
import { PortfolioValuationResponse, TransactionRecord } from './types/portfolio';
import { Button } from './components/ui/Button';
import { PlusCircle, Wallet } from 'lucide-react';

const MainApp: React.FC = () => {
  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [activePortfolioId, setActivePortfolioId] = useState<string>('consolidated');
  const [valuationData, setValuationData] = useState<PortfolioValuationResponse | null>(null);
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);

  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);
  const [editingTx, setEditingTx] = useState<TransactionRecord | null>(null);
  const [isCreateAccountOpen, setIsCreateAccountOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

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
    setIsActionLoading(true);
    try {
      const [val, txs] = await Promise.all([
        portfolioService.getValuation(pid),
        portfolioService.getTransactions(pid),
      ]);
      setValuationData(val);
      setTransactions(txs);
    } catch {
      // Handled silently
    } finally {
      setIsActionLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchPortfolios().then((ports) => {
        if (ports.length > 0) {
          refreshValuation(activePortfolioId);
        }
      });
    }
  }, [isAuthenticated, activePortfolioId]);

  const handleCreateTrade = () => {
    setEditingTx(null);
    setIsTradeModalOpen(true);
  };

  const handleDeletePortfolio = async (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
      try {
        await portfolioService.deletePortfolio(id);
        showToast(`Account "${name}" deleted successfully.`);
        const updated = await fetchPortfolios();
        if (activePortfolioId === id) {
          setActivePortfolioId(updated.length > 0 ? 'consolidated' : '');
        }
      } catch (err: any) {
        showToast(
          err?.response?.data?.error?.message ||
            'Cannot delete account because it contains active securities. Please transfer or sell your shares first.'
        );
      }
    }
  };

  const handleEditTransaction = (tx: TransactionRecord) => {
    setEditingTx(tx);
    setIsTradeModalOpen(true);
  };

  if (isAuthLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="w-8 h-8 border-b-2 rounded-full animate-spin border-emerald-600"></div>
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
      onDeletePortfolio={handleDeletePortfolio}
    >
      {(activeTab) => {
        // Allow Admin Dashboard even if admin has 0 broker accounts
        if (activeTab === 'admin' && user?.role === 'admin') {
          return <AdminView />;
        }

        // Allow PSX Market Data Terminal even if user has 0 accounts
        if (activeTab === 'market') {
          return <MarketView />;
        }

        if (!valuationData && portfolios.length > 0) {
          return (
            <div className="min-h-[50vh] flex items-center justify-center">
              <div className="w-8 h-8 border-b-2 rounded-full animate-spin border-emerald-600"></div>
            </div>
          );
        }

        // Onboarding Empty State for Brand New User with 0 Accounts
        if (portfolios.length === 0) {
          return (
            <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6 bg-white border border-gray-200 rounded-2xl shadow-xs my-4">
              <div className="flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-emerald-50 text-emerald-600">
                <Wallet className="w-8 h-8" />
              </div>
              <h2 className="mb-1 text-xl font-bold text-gray-900">Welcome to PSX Portfolio Tracker</h2>
              <p className="max-w-md mb-6 text-sm text-gray-500">
                You don't have any portfolio accounts yet. Add your first broker account (e.g., Darson Securities, BMA Capital) or CDC Investor Account to get started!
              </p>
              <Button variant="primary" onClick={() => setIsCreateAccountOpen(true)}>
                <PlusCircle className="w-4 h-4 mr-2" />
                Add Your First Account
              </Button>

              <CreatePortfolioModal
                isOpen={isCreateAccountOpen}
                onClose={() => setIsCreateAccountOpen(false)}
                onSuccess={async (newId) => {
                  showToast('Account created successfully!');
                  await fetchPortfolios();
                  setActivePortfolioId(newId);
                }}
              />
            </div>
          );
        }

        return (
          <>
            {/* Toast Notification Banner */}
            {toastMessage && (
              <div className="fixed z-50 flex items-center gap-2 px-4 py-3 text-xs text-white bg-gray-900 border border-gray-700 shadow-lg bottom-5 right-5 rounded-xl animate-fade-in">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                {toastMessage}
              </div>
            )}

            {/* Spinner Overlay during DB requests */}
            {isActionLoading && (
              <div className="fixed top-3 right-5 z-50 flex items-center gap-2 bg-white border border-gray-200 px-3 py-1.5 rounded-lg shadow-sm text-xs text-gray-600 font-medium">
                <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-emerald-600"></div>
                Updating Portfolio...
              </div>
            )}

            {activeTab === 'dashboard' && valuationData && (
              <DashboardView
                data={valuationData}
                onOpenTrade={handleCreateTrade}
              />
            )}

            {activeTab === 'holdings' && valuationData && (
              <HoldingsView holdings={valuationData.holdings} />
            )}

            {activeTab === 'transactions' && (
              <TransactionsView
                transactions={transactions}
                onOpenTrade={handleCreateTrade}
                onEditTransaction={handleEditTransaction}
                onDeleteTransaction={async (portfolioId, transactionId) => {
                  try {
                    await portfolioService.deleteTransaction(portfolioId, transactionId);
                    showToast('Transaction deleted successfully!');
                    fetchPortfolios();
                    refreshValuation(activePortfolioId);
                  } catch (err: any) {
                    showToast(err?.response?.data?.error?.message || 'Failed to delete transaction');
                  }
                }}
              />
            )}

            {activeTab === 'corporate_actions' && (
              <CorporateActionsView
                portfolioId={activePortfolioId}
                portfolios={portfolios}
                onSuccess={() => {
                  showToast('Corporate action recorded successfully!');
                  refreshValuation(activePortfolioId);
                }}
              />
            )}

            {activeTab === 'analytics' && <AnalyticsView portfolioId={activePortfolioId} />}

            {activeTab === 'tax_report' && (
              <TaxReportView
                portfolioId={activePortfolioId === 'consolidated' ? (portfolios[0]?.id || '') : activePortfolioId}
              />
            )}

            {/* Modals */}
            <TransactionModal
              isOpen={isTradeModalOpen}
              editingTransaction={editingTx}
              onClose={() => {
                setIsTradeModalOpen(false);
                setEditingTx(null);
              }}
              portfolios={portfolios}
              activePortfolioId={activePortfolioId}
              onSuccess={() => {
                showToast(editingTx ? 'Transaction updated successfully!' : 'Transaction saved successfully!');
                fetchPortfolios();
                refreshValuation(activePortfolioId);
              }}
            />

            <CreatePortfolioModal
              isOpen={isCreateAccountOpen}
              onClose={() => setIsCreateAccountOpen(false)}
              onSuccess={async (newId) => {
                showToast('Account created successfully!');
                await fetchPortfolios();
                setActivePortfolioId(newId);
              }}
            />

            <TransferSharesModal
              isOpen={isTransferModalOpen}
              portfolios={portfolios}
              onClose={() => setIsTransferModalOpen(false)}
              onSuccess={async () => {
                showToast('Shares transferred successfully!');
                await fetchPortfolios();
                refreshValuation(activePortfolioId);
              }}
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