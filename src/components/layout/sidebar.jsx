import React from 'react';
import { FolderOpen } from 'lucide-react';
import { sidebarItems } from '../../data/mockdata';
import Toggle from '../common/toggle';

const Sidebar = ({ activeTab, setActiveTab, autoOrganize, setAutoOrganize }) => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* App Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <FolderOpen className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">AI File Sorter</h1>
            <p className="text-sm text-gray-500">Organize with AI</p>
          </div>
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
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    isActive 
                      ? 'bg-gray-100 text-gray-900' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <IconComponent className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.name}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Auto-organize Toggle */}
      <Toggle
        label="Auto-organize"
        value={autoOrganize}
        onChange={setAutoOrganize}
        statusText="AI Status"
        description="Ready to organize your files"
      />
    </div>
  );
};

export default Sidebar;