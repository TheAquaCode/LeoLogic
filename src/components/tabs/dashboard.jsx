import React, { useState, useEffect } from "react";
import { Activity, RefreshCw } from "lucide-react";
import apiService from "../../services/api";

const Dashboard = ({ isChatMaximized }) => {
  // INSTANT LOAD from sessionStorage
  const [stats, setStats] = useState(() => {
    try {
      const cached = sessionStorage.getItem('dashboard_stats');
      return cached ? JSON.parse(cached) : {
        total: 0,
        completed: 0,
        pending: 0,
        success_rate: '0%'
      };
    } catch {
      return { total: 0, completed: 0, pending: 0, success_rate: '0%' };
    }
  });

  const [watchedFolders, setWatchedFolders] = useState(() => {
    try {
      const cached = sessionStorage.getItem('watched_folders');
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });

  const [categories, setCategories] = useState(() => {
    try {
      const cached = sessionStorage.getItem('categories');
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [historyStats, folders, cats] = await Promise.all([
        apiService.getHistoryStats(),
        apiService.getWatchedFolders(),
        apiService.getCategories()
      ]);
      
      setStats(historyStats);
      setWatchedFolders(Array.isArray(folders) ? folders : []);
      setCategories(Array.isArray(cats) ? cats : []);

      // Cache for instant next load
      sessionStorage.setItem('dashboard_stats', JSON.stringify(historyStats));
      sessionStorage.setItem('watched_folders', JSON.stringify(folders));
      sessionStorage.setItem('categories', JSON.stringify(cats));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalFiles = stats.total || 0;
  const organizedFiles = stats.completed || 0;
  const organizationProgress = totalFiles > 0 ? Math.round((organizedFiles / totalFiles) * 100) : 0;
  
  const activeFolders = watchedFolders.filter(f => f.status === 'Active').length;
  const totalFolders = watchedFolders.length;

  return (
    <div 
      className={`flex-1 overflow-auto p-6 transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`} 
      style={{ backgroundColor: 'var(--theme-bg-primary)' }}
    >
      <div className="max-w-7xl mx-auto w-full space-y-6">
        {/* Dashboard Section */}
        <div>
          <h1 className="text-xl font-semibold mb-1" style={{ color: 'var(--theme-text-primary)' }}>Dashboard</h1>
          <p className="mb-4 text-sm" style={{ color: 'var(--theme-text-secondary)' }}>
            AI-powered file organization overview
          </p>

          {/* Organization Progress */}
          <div className="rounded-lg shadow-sm p-4 border" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <h2 className="text-base font-medium mb-1" style={{ color: 'var(--theme-text-primary)' }}>
              Organization Progress
            </h2>
            <p className="text-xs mb-3" style={{ color: 'var(--theme-text-secondary)' }}>Overall Organization</p>

            {/* Progress Bar */}
            <div className="relative w-full h-2 rounded-full overflow-hidden mb-2" style={{
              backgroundColor: 'var(--theme-border-primary)'
            }}>
              <div className="absolute top-0 left-0 h-full rounded-full transition-all" style={{
                backgroundColor: 'var(--theme-primary)',
                width: `${organizationProgress}%`
              }}></div>
            </div>
            <div className="flex justify-between text-xs mb-4" style={{ color: 'var(--theme-text-secondary)' }}>
              <span>{organizedFiles} files organized</span>
              <span>{organizationProgress}%</span>
            </div>

            {/* Stats - Responsive grid */}
            <div className={`grid gap-3 ${
              isChatMaximized 
                ? 'grid-cols-2' 
                : 'grid-cols-2 md:grid-cols-4'
            }`}>
              <div
                className="border rounded-lg p-3 text-center"
                style={{
                  backgroundColor: 'var(--theme-bg-tertiary)',
                  borderColor: 'var(--theme-border-primary)'
                }}
              >
                <p className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Total Files</p>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--theme-text-primary)' }}>
                  {totalFiles}
                </p>
              </div>
              <div
                className="border rounded-lg p-3 text-center"
                style={{
                  backgroundColor: 'var(--theme-bg-tertiary)',
                  borderColor: 'var(--theme-border-primary)'
                }}
              >
                <p className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Organized</p>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--theme-text-primary)' }}>
                  {organizedFiles}
                </p>
              </div>
              <div
                className="border rounded-lg p-3 text-center"
                style={{
                  backgroundColor: 'var(--theme-bg-tertiary)',
                  borderColor: 'var(--theme-border-primary)'
                }}
              >
                <p className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Categories</p>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--theme-text-primary)' }}>
                  {categories.length}
                </p>
              </div>
              <div
                className="border rounded-lg p-3 text-center"
                style={{
                  backgroundColor: 'var(--theme-bg-tertiary)',
                  borderColor: 'var(--theme-border-primary)'
                }}
              >
                <p className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Success Rate</p>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--theme-text-primary)' }}>
                  {stats.success_rate}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Active Activity Section */}
        <div>
          <h1 className="text-xl font-semibold mb-1" style={{ color: 'var(--theme-text-primary)' }}>
            Active Activity
          </h1>
          <p className="mb-4 text-sm" style={{ color: 'var(--theme-text-secondary)' }}>
            System metrics and task monitoring
          </p>

          {/* Metrics */}
          <div className="rounded-lg shadow-sm p-4 border mb-4" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <div className="flex flex-wrap justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4" style={{ color: 'var(--theme-text-secondary)' }} />
                <span className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                  Watched Folders
                </span>
              </div>
              <span className="font-semibold text-lg" style={{ color: 'var(--theme-text-primary)' }}>
                {activeFolders}/{totalFolders}
              </span>
            </div>
            <div className="w-full h-1.5 rounded-full mb-4 overflow-hidden" style={{
              backgroundColor: 'var(--theme-border-primary)'
            }}>
              <div className="h-full rounded-full" style={{
                backgroundColor: 'var(--theme-primary)',
                width: totalFolders > 0 ? `${(activeFolders / totalFolders) * 100}%` : '0%'
              }}></div>
            </div>

            <div className={`grid gap-4 text-xs ${
              isChatMaximized 
                ? 'grid-cols-1' 
                : 'grid-cols-2 md:grid-cols-3'
            }`} style={{ color: 'var(--theme-text-secondary)' }}>
              <div>
                <p className="font-medium" style={{ color: 'var(--theme-text-primary)' }}>Active Folders</p>
                <p>{activeFolders} monitoring</p>
              </div>
              <div>
                <p className="font-medium" style={{ color: 'var(--theme-text-primary)' }}>Categories</p>
                <p>{categories.length} defined</p>
              </div>
              <div>
                <p className="font-medium" style={{ color: 'var(--theme-text-primary)' }}>Status</p>
                <p className="text-green-600">● Online</p>
              </div>
            </div>
          </div>

          {/* Active Tasks */}
          <div className="rounded-lg shadow-sm p-4 border" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <h2 className="text-base font-medium mb-3" style={{ color: 'var(--theme-text-primary)' }}>
              Active Tasks
            </h2>

            {/* Real task: Organizing files */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-1.5 gap-4">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-sm" style={{ color: 'var(--theme-text-primary)' }}>
                    Organize Files
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    activeFolders > 0
                      ? "bg-blue-100 text-blue-700"
                      : "bg-gray-100 text-gray-600"
                  }`}>
                    {activeFolders > 0 ? 'Running' : 'Idle'}
                  </span>
                </div>
                <span className="text-xs whitespace-nowrap" style={{ color: 'var(--theme-text-secondary)' }}>
                  {organizedFiles}/{totalFiles} files
                </span>
              </div>
              <div className="relative w-full h-1.5 rounded-full overflow-hidden" style={{
                backgroundColor: 'var(--theme-border-primary)'
              }}>
                <div
                  className="bg-blue-500 h-full rounded-full transition-all"
                  style={{ width: `${organizationProgress}%` }}
                ></div>
              </div>
            </div>

            {/* Placeholder tasks */}
            <div className="mb-4 opacity-50">
              <div className="flex justify-between items-center mb-1.5 gap-4">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-sm" style={{ color: 'var(--theme-text-primary)' }}>
                    Remove Duplicates
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                    Not Available
                  </span>
                </div>
                <span className="text-xs whitespace-nowrap" style={{ color: 'var(--theme-text-secondary)' }}>
                  Coming Soon
                </span>
              </div>
              <div className="relative w-full h-1.5 rounded-full overflow-hidden" style={{
                backgroundColor: 'var(--theme-border-primary)'
              }}>
                <div className="bg-gray-400 h-full rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>

            <div className="opacity-50">
              <div className="flex justify-between items-center mb-1.5 gap-4">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-sm" style={{ color: 'var(--theme-text-primary)' }}>
                    Clean Old Files
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                    Not Available
                  </span>
                </div>
                <span className="text-xs whitespace-nowrap" style={{ color: 'var(--theme-text-secondary)' }}>
                  Coming Soon
                </span>
              </div>
              <div className="relative w-full h-1.5 rounded-full overflow-hidden" style={{
                backgroundColor: 'var(--theme-border-primary)'
              }}>
                <div className="bg-gray-400 h-full rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;