import React, { useState } from 'react';
import Sidebar from './components/layout/sidebar';
import Header from './components/layout/header';
import FileExplorer from './components/tabs/FileExplorer';
import History from './components/tabs/History';
import AIAssistant from './components/tabs/AIAssistant';
import FloatingChatbot from './components/ui/FloatingChatbot';
import UploadScan from './components/tabs/UploadScan';
import Settings from './components/tabs/Settings';
import ComingSoon from './components/tabs/ComingSoon';
import Dashboard from './components/tabs/dashboard'; // ADD THIS LINE - Import the Dashboard component
import { defaultSettings } from './data/mockdata';

const App = () => {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [autoOrganize, setAutoOrganize] = useState(true);
  const [actionFilter, setActionFilter] = useState('All Actions');
  const [timeFilter, setTimeFilter] = useState('All Time');
  const [settings, setSettings] = useState(defaultSettings);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'Dashboard':  // Change to capital D
        return <Dashboard />;
      case 'File Explorer':
        return <FileExplorer />;
      case 'History':
        return <History />;
      case 'AI Assistant':
        return <AIAssistant />;
      case 'Upload & Scan':
        return <UploadScan />;
      case 'Settings':
        return <Settings />;
      default:
        return <ComingSoon />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        autoOrganize={autoOrganize}
        setAutoOrganize={setAutoOrganize}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Header
          activeTab={activeTab}
          actionFilter={actionFilter}
          setActionFilter={setActionFilter}
          timeFilter={timeFilter}
          setTimeFilter={setTimeFilter}
        />

        {/* Content */}
        {renderTabContent()}
      </div>
      <FloatingChatbot />

    </div>
  );
};

export default App;