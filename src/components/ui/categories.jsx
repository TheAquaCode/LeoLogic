import React, { useState } from 'react';
import { Tag, Plus, MoreHorizontal, Folder, Trash2, X, Edit2, FileText, ExternalLink } from 'lucide-react';

const Categories = ({ categories = [], onAddCategory, onRenameCategory, onDelete, onEditPath, onOpenLocation }) => {
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showRenameDialog, setShowRenameDialog] = useState(false);
  const [categoryName, setCategoryName] = useState('');
  const [categoryPath, setCategoryPath] = useState('');
  const [renameCategoryId, setRenameCategoryId] = useState(null);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [openMenuId, setOpenMenuId] = useState(null);

  const safeCategories = Array.isArray(categories) ? categories : [];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (categoryName.trim() && categoryPath.trim()) {
      await onAddCategory({
        name: categoryName,
        path: categoryPath
      });
      setCategoryName('');
      setCategoryPath('');
      setShowAddDialog(false);
    }
  };

  const handleRenameSubmit = async (e) => {
    e.preventDefault();
    if (newCategoryName.trim()) {
      await onRenameCategory(renameCategoryId, newCategoryName.trim());
      setShowRenameDialog(false);
      setRenameCategoryId(null);
      setNewCategoryName('');
    }
  };

  const handleSelectFolder = async (categoryId) => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (selectFolderAPI) {
      try {
        const folderPath = await selectFolderAPI();
        if (folderPath) {
          if (categoryId) {
            onEditPath(categoryId);
          } else {
            setCategoryPath(folderPath);
          }
        }
      } catch (error) {
        console.error('Error selecting folder:', error);
      }
    } else {
      alert('Folder selection is only available in the Electron app');
    }
  };

  const openRenameDialog = (category) => {
    setRenameCategoryId(category.id);
    setNewCategoryName(category.name);
    setShowRenameDialog(true);
    setOpenMenuId(null);
  };

  return (
    <div className="flex flex-col min-h-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Tag className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Categories</h3>
        </div>
        <button 
          onClick={() => setShowAddDialog(true)}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>
      <p className="text-sm text-gray-600 mb-6">User-defined organization rules</p>

      <div className="space-y-3 overflow-y-auto flex-1">
        {safeCategories.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Tag className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No categories created</p>
            <p className="text-sm">Click "Add" to create a category</p>
          </div>
        ) : (
          safeCategories.map((category) => (
            <div key={category.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 ${category.color || 'bg-blue-500'} rounded flex items-center justify-center`}>
                    <Folder className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{category.name}</h4>
                    <p className="text-sm text-gray-500 truncate max-w-xs">{category.path}</p>
                  </div>
                </div>
                <div className="relative">
                  <button 
                    onClick={() => setOpenMenuId(openMenuId === category.id ? null : category.id)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <MoreHorizontal className="w-5 h-5" />
                  </button>
                  
                  {openMenuId === category.id && (
                    <>
                      <div 
                        className="fixed inset-0 z-10" 
                        onClick={() => setOpenMenuId(null)}
                      />
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                        <button
                          onClick={() => openRenameDialog(category)}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          <FileText className="w-4 h-4" />
                          <span>Rename</span>
                        </button>
                        <button
                          onClick={() => {
                            onOpenLocation(category.path);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>Open Location</span>
                        </button>
                        <button
                          onClick={() => {
                            handleSelectFolder(category.id);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                        >
                          <Edit2 className="w-4 h-4" />
                          <span>Edit Path</span>
                        </button>
                        <button
                          onClick={() => {
                            onDelete(category.id);
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
              
              {category.fileTypes && category.fileTypes.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {category.fileTypes.map((type, typeIndex) => (
                    <span
                      key={typeIndex}
                      className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="mt-3 text-sm">
                {category.ruleStatus ? (
                  <span className="text-gray-500">{category.ruleStatus}</span>
                ) : (
                  <span className="text-gray-600">{category.rules || 0} rules</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Category Dialog */}
      {showAddDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Add Category</h3>
              <button
                onClick={() => {
                  setShowAddDialog(false);
                  setCategoryName('');
                  setCategoryPath('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category Name
                </label>
                <input
                  type="text"
                  value={categoryName}
                  onChange={(e) => setCategoryName(e.target.value)}
                  placeholder="e.g., Work Documents"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Destination Folder
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={categoryPath}
                    onChange={(e) => setCategoryPath(e.target.value)}
                    placeholder="Select a folder..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => handleSelectFolder(null)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Browse
                  </button>
                </div>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddDialog(false);
                    setCategoryName('');
                    setCategoryPath('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Category
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Rename Category Dialog */}
      {showRenameDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Rename Category</h3>
              <button
                onClick={() => {
                  setShowRenameDialog(false);
                  setRenameCategoryId(null);
                  setNewCategoryName('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleRenameSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Category Name
                </label>
                <input
                  type="text"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  placeholder="Enter new name..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                  required
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowRenameDialog(false);
                    setRenameCategoryId(null);
                    setNewCategoryName('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Rename
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;