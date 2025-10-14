import React from 'react';
import { Eye, Plus, MoreHorizontal } from 'lucide-react';
import { watchedFolders } from '../../data/mockdata';
import { getStatusColor } from '../../utils/helpers';

const WatchedFolders = () => {
  return (
    <div className="flex flex-col min-h-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Eye className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Watched Folders</h3>
        </div>
        <button className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>
      <p className="text-sm text-gray-600 mb-6">Folders monitored by AI</p>

      <div className="space-y-3 overflow-y-auto flex-1">
        {watchedFolders.map((folder, index) => {
          const IconComponent = folder.icon;
          return (
            <div key={index} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                    <IconComponent className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{folder.name}</h4>
                    <p className="text-sm text-gray-500">{folder.path}</p>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-gray-600">
                  <MoreHorizontal className="w-5 h-5" />
                </button>
              </div>
              <div className="flex items-center justify-between mt-3 text-sm">
                <span className="text-gray-600">{folder.files} files</span>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-500">{folder.lastActivity}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(folder.status)}`}>
                    {folder.status}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WatchedFolders;