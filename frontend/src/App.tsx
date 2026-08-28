import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Shell } from './components/layout/Shell';
import { LoginPage } from './features/auth/LoginPage';
import { RegisterPage } from './features/auth/RegisterPage';
import { Card } from './components/ui/Card';
import { Badge } from './components/ui/Badge';

const MainApp: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  if (isLoading) {
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
    <Shell>
      {(activeTab) => (
        <div className="space-y-6">
          {/* Welcome Banner */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900 capitalize">{activeTab.replace('_', ' ')}</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Pakistan Stock Exchange portfolio tracking with FIFO lot precision
              </p>
            </div>
            <Badge variant="green">Connected to PSX Engine</Badge>
          </div>

          {/* Tab Content Placeholder */}
          <Card title={`Active Section: ${activeTab.toUpperCase()}`}>
            <p className="text-sm text-gray-600">
              Frontend foundation initialized. In Phase 8, we will build out the complete interactive
              Dashboard, Holdings Table, Transaction Entry modals, and Corporate Action forms!
            </p>
          </Card>
        </div>
      )}
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