import React from 'react';
import { FolderOpen } from 'lucide-react';
import { sidebarItems } from '../../data/mockdata';
import logo from '../../assets/Clanky_Logo.png';

const Sidebar = ({ activeTab, setActiveTab, autoOrganize, setAutoOrganize, isCollapsed }) => {
  return (
    <div className={`bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      {/* App Header */}
      <div className={`p-6 border-b border-gray-100 dark:border-gray-800 ${isCollapsed ? 'px-2' : ''}`}>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'}`}>
          <img 
            src={logo} 
            alt="AI File Sorter Logo" 
            className="w-10 h-10 rounded-lg object-cover flex-shrink-0"
          />
          {!isCollapsed && (
            <div>
              <h1 className="font-semibold text-gray-900 dark:text-white">AI File Sorter</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Organize with AI</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {sidebarItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = item.name === activeTab;
            return (
              <li key={item.name}>
                <button
                  onClick={() => setActiveTab(item.name)}
                  className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'} px-3 py-2 rounded-lg text-left transition-colors ${
                    isActive 
                      ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white' 
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                  }`}
                  title={isCollapsed ? item.name : undefined}
                >
                  <IconComponent className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && <span className="text-sm font-medium">{item.name}</span>}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Auto-organize Toggle - Only show when NOT collapsed */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Auto-organize</span>
            <button
              onClick={() => setAutoOrganize(!autoOrganize)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoOrganize ? 'bg-green-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoOrganize ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${autoOrganize ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            <span className={`text-sm ${autoOrganize ? 'text-green-600' : 'text-gray-500'}`}>
              {autoOrganize ? 'Active folders auto-sorting' : 'Manual sorting only'}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {autoOrganize 
              ? 'New files in active folders will be automatically organized'
              : 'Enable to automatically organize files in active watched folders'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default Sidebar;