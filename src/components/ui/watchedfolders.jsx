// src/components/ui/watchedfolders.jsx - Fixed with null safety
import React, { useState } from 'react';
import { Eye, Plus, MoreHorizontal, Folder, Play, Pause, Edit2, Trash2, Zap, Loader, ExternalLink } from 'lucide-react';
import { getStatusColor } from '../../utils/helpers';

const WatchedFolders = ({ 
  folders = [], 
  onAddFolder, 
  onToggleStatus, 
  onEditPath, 
  onDelete,
  onProcessFolder,
  onOpenLocation,
  processingFolder,
  backendOnline = false
}) => {
  const [openMenuId, setOpenMenuId] = useState(null);

  // Ensure folders is always an array
  const safeFolders = Array.isArray(folders) ? folders : [];

  return (
    <div className="flex flex-col min-h-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Eye className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Watched Folders</h3>
        </div>
        <button 
          onClick={onAddFolder}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>
      <p className="text-sm text-gray-600 mb-6">Folders monitored by AI</p>

      <div className="space-y-3 overflow-y-auto flex-1">
        {safeFolders.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Folder className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No folders being watched</p>
            <p className="text-sm">Click "Add" to start monitoring a folder</p>
          </div>
        ) : (
          safeFolders.map((folder) => (
            <div key={folder.id} className="bg-white rounded-lg border border-gray-200 p-4 relative">
              {processingFolder === folder.id && (
                <div className="absolute inset-0 bg-blue-50 bg-opacity-90 rounded-lg flex items-center justify-center z-10">
                  <div className="text-center">
                    <Loader className="w-6 h-6 animate-spin text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-medium text-blue-900">Processing files...</p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
                    <Folder className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="font-medium text-gray-900 truncate">{folder.name}</h4>
                    <p className="text-sm text-gray-500 truncate">{folder.path}</p>
                  </div>
                </div>
                <div className="relative flex-shrink-0 ml-2">
                  <button 
                    onClick={() => setOpenMenuId(openMenuId === folder.id ? null : folder.id)}
                    className="text-gray-400 hover:text-gray-600 p-1"
                  >
                    <MoreHorizontal className="w-5 h-5" />
                  </button>
                  
                  {openMenuId === folder.id && (
                    <>
                      <div 
                        className="fixed inset-0 z-10" 
                        onClick={() => setOpenMenuId(null)}
                      />
                      <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                        {backendOnline && (
                          <button
                            onClick={() => {
                              onProcessFolder(folder.id);
                              setOpenMenuId(null);
                            }}
                            disabled={processingFolder === folder.id}
                            className="w-full px-4 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 flex items-center space-x-2 disabled:opacity-50"
                          >
                            <Zap className="w-4 h-4" />
                            <span>Process Existing Files</span>
                          </button>
                        )}
                        <button
                          onClick={() => {
                            onOpenLocation(folder.path);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>Open Location</span>
                        </button>
                        <button
                          onClick={() => {
                            onToggleStatus(folder.id);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          {folder.status === 'Active' ? (
                            <>
                              <Pause className="w-4 h-4" />
                              <span>Pause Watching</span>
                            </>
                          ) : (
                            <>
                              <Play className="w-4 h-4" />
                              <span>Resume Watching</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => {
                            onEditPath(folder.id);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          <Edit2 className="w-4 h-4" />
                          <span>Edit Path</span>
                        </button>
                        <button
                          onClick={() => {
                            onDelete(folder.id);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between mt-3 text-sm">
                {/* Debug logging */}
                {console.log(`Rendering folder ${folder.name}, fileCount:`, folder.fileCount, typeof folder.fileCount)}
                <span className="text-gray-600">
                  {Number(folder.fileCount ?? 0)} {Number(folder.fileCount ?? 0) === 1 ? 'file' : 'files'}
                </span>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-500">{folder.lastActivity || 'Never'}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(folder.status)}`}>
                    {folder.status}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WatchedFolders;