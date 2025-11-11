import React, { useState, useEffect } from 'react';
import { FileText, Check, Clock, Image, ArrowRight, RotateCcw, MoreHorizontal, Folder, AlertCircle, Search, ChevronDown } from 'lucide-react';
import apiService from '../../services/api';

const StatsCards = ({ stats, isChatMaximized }) => {
  const statsConfig = [
    {
      label: 'Total Files',
      value: stats.total || 0,
      icon: FileText,
      bgColor: 'bg-gray-100 dark:bg-gray-700',
      iconColor: 'text-gray-600 dark:text-gray-300'
    },
    {
      label: 'Completed',
      value: stats.completed || 0,
      icon: Check,
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      iconColor: 'text-green-600 dark:text-green-400'
    },
    {
      label: 'Undone',
      value: stats.undone || 0,
      icon: Clock,
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      iconColor: 'text-yellow-600 dark:text-yellow-400'
    },
    {
      label: 'Success Rate',
      value: stats.success_rate || '0%',
      icon: Check,
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      iconColor: 'text-green-600 dark:text-green-400'
    }
  ];

  return (
    <div className={`grid gap-4 mb-6 ${isChatMaximized ? 'grid-cols-2' : 'grid-cols-4'}`}>
      {statsConfig.map((stat, index) => {
        const IconComponent = stat.icon;
        return (
          <div key={index} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
              <div className={`w-8 h-8 ${stat.bgColor} rounded flex items-center justify-center`}>
                <IconComponent className={`w-4 h-4 ${stat.iconColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const truncatePath = (path, maxLength = 50) => {
  if (path.length <= maxLength) return path;
  
  const parts = path.split(/[/\\]/);
  
  // Show at least parent folder and filename
  if (parts.length <= 3) return path;
  
  const fileName = parts[parts.length - 1];
  const parentFolder = parts[parts.length - 2];
  const rootDir = parts[0];
  
  // Format: C:/...../ParentFolder/file.txt
  return `${rootDir}/...../${parentFolder}/${fileName}`;
};

const FileMovements = ({ isChatMaximized, searchQuery, actionFilter, timeFilter }) => {
  const [movements, setMovements] = useState(() => {
    // Try to load from sessionStorage for instant display
    try {
      const cached = sessionStorage.getItem('history_movements');
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [processingUndo, setProcessingUndo] = useState(null);

  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadHistory = async () => {
    try {
      const data = await apiService.getHistory(100);
      setMovements(data);
      setError(null);
      
      // Cache in sessionStorage for instant access
      sessionStorage.setItem('history_movements', JSON.stringify(data));
    } catch (err) {
      console.error('Error loading history:', err);
      setError('Unable to load file history');
    } finally {
      setLoading(false);
    }
  };

  const handleUndo = async (movementId) => {
    if (!window.confirm('Are you sure you want to undo this file movement?')) {
      return;
    }

    setProcessingUndo(movementId);
    try {
      await apiService.undoMovement(movementId);
      await loadHistory();
      setOpenMenuId(null);
    } catch (err) {
      console.error('Error undoing movement:', err);
      alert('Failed to undo file movement: ' + err.message);
    } finally {
      setProcessingUndo(null);
    }
  };

  const handleOpenLocation = async (movementId) => {
    try {
      const result = await apiService.openFileLocation(movementId);
      
      const openFolderAPI = window.electron?.openFolder || 
                           window.electronAPI?.openFolder || 
                           window.api?.openFolder;
      
      if (openFolderAPI) {
        await openFolderAPI(result.directory);
      } else {
        navigator.clipboard.writeText(result.directory);
        alert(`Path copied to clipboard:\n${result.directory}`);
      }
      
      setOpenMenuId(null);
    } catch (err) {
      console.error('Error opening location:', err);
      alert('Failed to open file location: ' + err.message);
    }
  };

  // Filter movements based on search and filters
  const getFilteredMovements = () => {
    let filtered = [...movements];

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(m => 
        m.filename?.toLowerCase().includes(query) ||
        m.fromPath?.toLowerCase().includes(query) ||
        m.toPath?.toLowerCase().includes(query) ||
        m.category?.toLowerCase().includes(query) ||
        m.detection?.toLowerCase().includes(query)
      );
    }

    // Action filter
    if (actionFilter !== 'All Actions') {
      if (actionFilter === 'Moved') {
        filtered = filtered.filter(m => m.status === 'completed');
      } else if (actionFilter === 'Organized') {
        filtered = filtered.filter(m => m.detection?.includes('AI'));
      } else if (actionFilter === 'Categorized') {
        filtered = filtered.filter(m => m.category);
      }
    }

    // Time filter
    if (timeFilter !== 'All Time') {
      const now = Date.now();
      const oneDayMs = 24 * 60 * 60 * 1000;
      const oneWeekMs = 7 * oneDayMs;

      filtered = filtered.filter(m => {
        const movementTime = m.timestamp * 1000; // Convert to ms
        const timeDiff = now - movementTime;

        if (timeFilter === 'Today') {
          return timeDiff < oneDayMs;
        } else if (timeFilter === 'This Week') {
          return timeDiff < oneWeekMs;
        }
        return true;
      });
    }

    return filtered;
  };

  const filteredMovements = getFilteredMovements();

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-red-500 dark:text-red-400 mx-auto mb-4" />
          <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
          <button 
            onClick={loadHistory}
            className="mt-4 px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (filteredMovements.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 font-medium mb-2">
            {searchQuery || actionFilter !== 'All Actions' || timeFilter !== 'All Time' 
              ? 'No matching file movements'
              : 'No file movements yet'}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            {searchQuery || actionFilter !== 'All Actions' || timeFilter !== 'All Time'
              ? 'Try adjusting your filters'
              : 'Files organized by the AI will appear here'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex-1 flex flex-col min-h-0">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent File Movements</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {filteredMovements.length} {filteredMovements.length === 1 ? 'file' : 'files'}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {filteredMovements.map((movement) => (
            <div key={movement.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 relative transition-colors">
              {processingUndo === movement.id && (
                <div className="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-75 dark:bg-opacity-75 flex items-center justify-center z-10">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 dark:border-blue-400"></div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded flex items-center justify-center flex-shrink-0">
                    <Image className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900 dark:text-white truncate">{movement.filename}</h4>
                      <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">{movement.confidence}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-sm text-gray-500 dark:text-gray-400">{movement.timeAgo}</span>
                      <span className="text-gray-300 dark:text-gray-600">•</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">{movement.detection}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500 dark:text-gray-400">
                      <span className="truncate max-w-[250px]" title={movement.fromPath}>
                        {truncatePath(movement.fromPath)}
                      </span>
                      <ArrowRight className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate max-w-[250px]" title={movement.toPath}>
                        {truncatePath(movement.toPath)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4 flex-shrink-0">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    movement.status === 'undone' 
                      ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                      : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  }`}>
                    <Check className="w-3 h-3 mr-1" />
                    {movement.status === 'undone' ? 'Undone' : 'Done'}
                  </span>
                  
                  {movement.status !== 'undone' && (
                    <button 
                      onClick={() => handleUndo(movement.id)}
                      disabled={processingUndo === movement.id}
                      className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors disabled:opacity-50"
                      title="Undo movement"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  )}
                  
                  <div className="relative">
                    <button 
                      onClick={() => setOpenMenuId(openMenuId === movement.id ? null : movement.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                    
                    {openMenuId === movement.id && (
                      <>
                        <div 
                          className="fixed inset-0 z-10" 
                          onClick={() => setOpenMenuId(null)}
                        />
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20">
                          <button
                            onClick={() => handleOpenLocation(movement.id)}
                            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center space-x-2"
                          >
                            <Folder className="w-4 h-4" />
                            <span>Open Location</span>
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const History = ({ isChatMaximized }) => {
  const [stats, setStats] = useState(() => {
    // Try to load from sessionStorage for instant display
    try {
      const cached = sessionStorage.getItem('history_stats');
      return cached ? JSON.parse(cached) : {
        total: 0,
        completed: 0,
        undone: 0,
        pending: 0,
        success_rate: '0%'
      };
    } catch {
      return {
        total: 0,
        completed: 0,
        undone: 0,
        pending: 0,
        success_rate: '0%'
      };
    }
  });
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('All Actions');
  const [timeFilter, setTimeFilter] = useState('All Time');

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiService.getHistoryStats();
      setStats(data);
      
      // Cache in sessionStorage for instant access
      sessionStorage.setItem('history_stats', JSON.stringify(data));
    } catch (err) {
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Search and Filters Bar */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
            <input
              type="text"
              placeholder="Search files, paths, or reasons..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div className="relative">
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="appearance-none border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-8 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
            >
              <option>All Actions</option>
              <option>Moved</option>
              <option>Organized</option>
              <option>Categorized</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none" />
          </div>
          
          <div className="relative">
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="appearance-none border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-8 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
            >
              <option>All Time</option>
              <option>Today</option>
              <option>This Week</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div 
        className={`flex-1 p-6 overflow-hidden transition-all duration-300 flex flex-col ${
          isChatMaximized ? 'pr-[500px]' : ''
        }`}
      >
        {loading ? (
          <div className="flex items-center justify-center flex-1">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
          </div>
        ) : (
          <>
            <StatsCards stats={stats} isChatMaximized={isChatMaximized} />
            <FileMovements 
              isChatMaximized={isChatMaximized} 
              searchQuery={searchQuery}
              actionFilter={actionFilter}
              timeFilter={timeFilter}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default History;