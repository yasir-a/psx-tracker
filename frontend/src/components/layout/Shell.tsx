import React, { useState } from 'react';
import { Header } from './Header';
import { NavItemKey, Sidebar } from './Sidebar';

interface ShellProps {
  children: (activeTab: NavItemKey) => React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<NavItemKey>('dashboard');

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col pl-64">
        <Header />
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {children(activeTab)}
        </main>
      </div>
    </div>
  );
};