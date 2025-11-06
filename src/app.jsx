import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/sidebar';
import Header from './components/layout/header';
import FileExplorer from './components/tabs/FileExplorer';
import History from './components/tabs/History';
import AIAssistant from './components/tabs/AIAssistant';
import FloatingChatbot from './components/ui/FloatingChatbot';
import UploadScan from './components/tabs/UploadScan';
import Settings from './components/tabs/Settings';
import ComingSoon from './components/tabs/ComingSoon';
import Dashboard from './components/tabs/dashboard';

const App = () => {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [actionFilter, setActionFilter] = useState('All Actions');
  const [timeFilter, setTimeFilter] = useState('All Time');
  const [isChatMaximized, setIsChatMaximized] = useState(false);
  
  // Load auto-organize from localStorage (OFF by default)
  const [autoOrganize, setAutoOrganizeState] = useState(() => {
    try {
      const stored = localStorage.getItem('auto_organize');
      return stored ? JSON.parse(stored) : false;
    } catch {
      return false;
    }
  });

  // Sync auto-organize to backend when it changes
  useEffect(() => {
    const syncAutoOrganize = async () => {
      try {
        await fetch('http://localhost:5001/api/settings/auto-organize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: autoOrganize })
        });
      } catch (error) {
        console.error('Error syncing auto-organize:', error);
      }
    };
    
    syncAutoOrganize();
  }, [autoOrganize]);

  // Load auto-organize setting from backend on startup
  useEffect(() => {
    const loadAutoOrganize = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/settings/auto-organize');
        if (response.ok) {
          const data = await response.json();
          setAutoOrganizeState(data.enabled);
          localStorage.setItem('auto_organize', JSON.stringify(data.enabled));
        }
      } catch (error) {
        console.error('Error loading auto-organize:', error);
      }
    };
    
    loadAutoOrganize();
  }, []);

  const setAutoOrganize = (value) => {
    setAutoOrganizeState(value);
    localStorage.setItem('auto_organize', JSON.stringify(value));
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'Dashboard':
        return <Dashboard isChatMaximized={isChatMaximized} />;
      case 'File Explorer':
        return <FileExplorer isChatMaximized={isChatMaximized} />;
      case 'History':
        return <History isChatMaximized={isChatMaximized} />;
      case 'AI Assistant':
        return <AIAssistant isChatMaximized={isChatMaximized} />;
      case 'Upload & Scan':
        return <UploadScan isChatMaximized={isChatMaximized} />;
      case 'Settings':
        return <Settings isChatMaximized={isChatMaximized} />;
      default:
        return <ComingSoon isChatMaximized={isChatMaximized} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        autoOrganize={autoOrganize}
        setAutoOrganize={setAutoOrganize}
        isCollapsed={isChatMaximized}
      />

      <div className="flex-1 flex flex-col">
        <Header
          activeTab={activeTab}
          actionFilter={actionFilter}
          setActionFilter={setActionFilter}
          timeFilter={timeFilter}
          setTimeFilter={setTimeFilter}
        />
        {renderTabContent()}
      </div>
      
      <FloatingChatbot onMaximizeChange={setIsChatMaximized} />
    </div>
  );
};

export default App;