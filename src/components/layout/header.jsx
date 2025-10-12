import React from 'react';
import { Search, ChevronDown } from 'lucide-react';

const Header = ({ activeTab, actionFilter, setActionFilter, timeFilter, setTimeFilter }) => {
  const getDescription = () => {
    switch (activeTab) {
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
    return activeTab === 'History' ? 'File Movement History' : activeTab;
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

      {/* Search Bar and Filters - show for File Explorer and History */}
      {(activeTab === 'File Explorer' || activeTab === 'History') && (
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder={activeTab === 'History' ? "Search files, paths, or reasons..." : "Search folders and categories..."}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                style={{
                  backgroundColor: 'var(--theme-bg-secondary)',
                  color: 'var(--theme-text-primary)',
                  borderColor: 'var(--theme-border-primary)'
                }}
              />
            </div>
            
            {activeTab === 'History' && (
              <>
                <div className="relative">
                  <select
                    value={actionFilter}
                    onChange={(e) => setActionFilter(e.target.value)}
                    className="appearance-none border rounded-lg px-4 py-2 pr-8 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    style={{
                      backgroundColor: 'var(--theme-bg-secondary)',
                      color: 'var(--theme-text-primary)',
                      borderColor: 'var(--theme-border-primary)'
                    }}
                  >
                    <option>All Actions</option>
                    <option>Moved</option>
                    <option>Organized</option>
                    <option>Categorized</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
                
                <div className="relative">
                  <select
                    value={timeFilter}
                    onChange={(e) => setTimeFilter(e.target.value)}
                    className="appearance-none border rounded-lg px-4 py-2 pr-8 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    style={{
                      backgroundColor: 'var(--theme-bg-secondary)',
                      color: 'var(--theme-text-primary)',
                      borderColor: 'var(--theme-border-primary)'
                    }}
                  >
                    <option>All Time</option>
                    <option>Today</option>
                    <option>This Week</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Header;