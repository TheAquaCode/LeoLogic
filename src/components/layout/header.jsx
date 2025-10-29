import React from 'react';
import { Search, ChevronDown } from 'lucide-react';

const Header = ({ activeTab, actionFilter, setActionFilter, timeFilter, setTimeFilter }) => {
  const getDescription = () => {
    switch (activeTab) {
      case 'Dashboard':
        return 'Overview of your file organization system';
      case 'File Explorer':
        return 'Manage watched folders and categories for AI organization';
      case 'Upload & Scan':
        return 'Add files for AI organization';
      case 'History':
        return 'Track individual file movements and AI decisions';
      case 'Settings':
        return 'Configure AI file sorting preferences';
      default:
        return `${activeTab} page`;
    }
  };

  const getTitle = () => {
    if (activeTab === 'History') return 'File Movement History';
    if (activeTab === 'Dashboard') return 'Dashboard';
    return activeTab;
  };

  return (
    <>
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">{getTitle()}</h2>
            <p className="text-sm text-gray-600">{getDescription()}</p>
          </div>
        </div>
      </header>

      {/* Removed search bar and filters entirely */}
    </>
  );
};

export default Header;
