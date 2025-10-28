// src/components/tabs/FileExplorer.jsx - Enhanced with backend integration
import React, { useState, useEffect } from 'react';
import { Zap, Image, Calendar, HardDrive, Copy, ChevronDown, AlertCircle } from 'lucide-react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';
import { loadFromStorage, saveToStorage } from '../../utils/storage';
import apiService from '../../services/api';

const QuickSortCard = ({ icon: Icon, title, description, isSelected, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${
      isSelected
        ? 'border-blue-500 bg-blue-50'
        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
    }`}
  >
    <Icon className={`w-6 h-6 mb-2 ${isSelected ? 'text-blue-500' : 'text-gray-700'}`} />
    <h3 className={`font-semibold mb-0.5 text-sm ${isSelected ? 'text-gray-900' : 'text-gray-900'}`}>{title}</h3>
    <p className="text-xs text-gray-500">{description}</p>
  </button>
);

const FileExplorer = ({ isChatMaximized }) => {
  const [selectedSort, setSelectedSort] = useState(null);
  const [isQuickSortExpanded, setIsQuickSortExpanded] = useState(() => {
    return loadFromStorage('QUICK_SORT_EXPANDED') ?? true;
  });

  // Backend connection state
  const [backendStatus, setBackendStatus] = useState('checking');
  const [watchedFolders, setWatchedFolders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState(null);
  const [processingFolder, setProcessingFolder] = useState(null);

  // Save expanded state whenever it changes
  useEffect(() => {
    saveToStorage('QUICK_SORT_EXPANDED', isQuickSortExpanded);
  }, [isQuickSortExpanded]);

  // Check backend status and load data
  useEffect(() => {
    loadData();
  }, []);

  const checkBackendStatus = async () => {
    try {
      await apiService.checkHealth();
      setBackendStatus('online');
      return true;
    } catch (err) {
      setBackendStatus('offline');
      return false;
    }
  };

  const loadData = async () => {
    const isOnline = await checkBackendStatus();
    
    if (isOnline) {
      try {
        const [foldersData, categoriesData] = await Promise.all([
          apiService.getWatchedFolders(),
          apiService.getCategories()
        ]);
        
        setWatchedFolders(foldersData || []);
        setCategories(categoriesData || []);
        
      } catch (err) {
        console.error('Error loading data:', err);
        // Load from localStorage as fallback
        const savedFolders = loadFromStorage('watched_folders', []);
        const savedCategories = loadFromStorage('categories', []);
        setWatchedFolders(savedFolders);
        setCategories(savedCategories);
      }
    } else {
      // Load from localStorage
      const savedFolders = loadFromStorage('watched_folders', []);
      const savedCategories = loadFromStorage('categories', []);
      setWatchedFolders(savedFolders);
      setCategories(savedCategories);
    }
  };

  const sortOptions = [
    { id: 'type', icon: Image, title: 'By Type', description: 'Sort by file type' },
    { id: 'date', icon: Calendar, title: 'By Date', description: 'Sort by date modified' },
    { id: 'size', icon: HardDrive, title: 'By Size', description: 'Sort by file size' },
    { id: 'duplicates', icon: Copy, title: 'Duplicates', description: 'Find duplicate files' }
  ];

  const handleStart = () => {
    if (selectedSort) {
      console.log('Starting quick sort:', selectedSort);
      alert(`Quick sort "${selectedSort}" feature coming soon!`);
    }
  };

  // Watched Folders handlers
  const handleAddWatchedFolder = async () => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (!selectFolderAPI) {
      alert('Folder selection is only available in the Electron app');
      return;
    }

    try {
      const folderPath = await selectFolderAPI();
      if (!folderPath) return;

      const folderName = folderPath.split('/').pop() || folderPath.split('\\').pop();
      
      if (backendStatus === 'online') {
        // Add via backend
        const result = await apiService.addWatchedFolder({
          name: folderName,
          path: folderPath
        });
        
        setWatchedFolders([...watchedFolders, result.folder]);
      } else {
        // Fallback: local only
        const newFolder = {
          id: Date.now(),
          name: folderName,
          path: folderPath,
          files: 0,
          lastActivity: 'Just now',
          status: 'Active'
        };
        setWatchedFolders([...watchedFolders, newFolder]);
        saveToStorage('watched_folders', [...watchedFolders, newFolder]);
      }
    } catch (error) {
      console.error('Error adding folder:', error);
      alert('Error adding folder: ' + error.message);
    }
  };

  const handleToggleFolderStatus = async (folderId) => {
    try {
      if (backendStatus === 'online') {
        const result = await apiService.toggleFolderStatus(folderId);
        setWatchedFolders(watchedFolders.map(f => 
          f.id === folderId ? result.folder : f
        ));
      } else {
        // Local fallback
        const updated = watchedFolders.map(folder => 
          folder.id === folderId 
            ? { ...folder, status: folder.status === 'Active' ? 'Paused' : 'Active' }
            : folder
        );
        setWatchedFolders(updated);
        saveToStorage('watched_folders', updated);
      }
    } catch (error) {
      console.error('Error toggling folder status:', error);
      alert('Error: ' + error.message);
    }
  };

  const handleEditFolderPath = async (folderId) => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (!selectFolderAPI) {
      alert('Folder selection is only available in the Electron app');
      return;
    }

    try {
      const folderPath = await selectFolderAPI();
      if (!folderPath) return;

      const folderName = folderPath.split('/').pop() || folderPath.split('\\').pop();
      
      const updated = watchedFolders.map(folder =>
        folder.id === folderId
          ? { ...folder, name: folderName, path: folderPath }
          : folder
      );
      
      setWatchedFolders(updated);
      
      if (backendStatus === 'offline') {
        saveToStorage('watched_folders', updated);
      }
    } catch (error) {
      console.error('Error editing folder:', error);
    }
  };

  const handleDeleteFolder = async (folderId) => {
    if (!window.confirm('Are you sure you want to stop watching this folder?')) {
      return;
    }

    try {
      if (backendStatus === 'online') {
        await apiService.deleteWatchedFolder(folderId);
      }
      
      const updated = watchedFolders.filter(folder => folder.id !== folderId);
      setWatchedFolders(updated);
      
      if (backendStatus === 'offline') {
        saveToStorage('watched_folders', updated);
      }
    } catch (error) {
      console.error('Error deleting folder:', error);
      alert('Error: ' + error.message);
    }
  };

  const handleProcessFolder = async (folderId) => {
    if (backendStatus !== 'online') {
      alert('Backend must be running to process files');
      return;
    }

    if (!window.confirm('Process all existing files in this folder?')) {
      return;
    }

    setProcessingFolder(folderId);
    
    try {
      const result = await apiService.processFolderFiles(folderId);
      alert(`Processed ${result.processed} files!\n\nCheck the console for details.`);
      console.log('Processing results:', result);
    } catch (error) {
      console.error('Error processing folder:', error);
      alert('Error processing folder: ' + error.message);
    } finally {
      setProcessingFolder(null);
    }
  };

  // Categories handlers
  const handleAddCategory = async (categoryData) => {
    try {
      if (backendStatus === 'online') {
        const result = await apiService.addCategory(categoryData);
        setCategories([...categories, result.category]);
      } else {
        // Local fallback
        const newCategory = {
          id: Date.now(),
          name: categoryData.name,
          path: categoryData.path,
          fileTypes: [],
          rules: 0,
          color: 'bg-blue-500'
        };
        setCategories([...categories, newCategory]);
        saveToStorage('categories', [...categories, newCategory]);
      }
    } catch (error) {
      console.error('Error adding category:', error);
      alert('Error: ' + error.message);
    }
  };

  const handleEditCategoryPath = async (categoryId) => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (!selectFolderAPI) {
      alert('Folder selection is only available in the Electron app');
      return;
    }

    try {
      const folderPath = await selectFolderAPI();
      if (!folderPath) return;

      if (backendStatus === 'online') {
        await apiService.updateCategory(categoryId, { path: folderPath });
      }
      
      const updated = categories.map(category =>
        category.id === categoryId
          ? { ...category, path: folderPath }
          : category
      );
      
      setCategories(updated);
      
      if (backendStatus === 'offline') {
        saveToStorage('categories', updated);
      }
    } catch (error) {
      console.error('Error editing category:', error);
      alert('Error: ' + error.message);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('Are you sure you want to delete this category?')) {
      return;
    }

    try {
      if (backendStatus === 'online') {
        await apiService.deleteCategory(categoryId);
      }
      
      const updated = categories.filter(category => category.id !== categoryId);
      setCategories(updated);
      
      if (backendStatus === 'offline') {
        saveToStorage('categories', updated);
      }
    } catch (error) {
      console.error('Error deleting category:', error);
      alert('Error: ' + error.message);
    }
  };

  return (
    <div 
      className={`flex-1 p-6 overflow-auto transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`}
    >
      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">Error</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Sort Section */}
      <div className="mb-8">
        <button 
          onClick={() => setIsQuickSortExpanded(!isQuickSortExpanded)}
          className="flex items-center gap-2 mb-2 w-full group"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-gray-700" />
            <h2 className="text-2xl font-semibold text-gray-900">Quick Sort</h2>
          </div>
          <ChevronDown 
            className={`w-5 h-5 text-gray-500 transition-transform duration-200 ease-in-out ml-2 ${
              isQuickSortExpanded ? 'transform rotate-180' : ''
            }`}
          />
        </button>
        
        <div className={`transition-all duration-200 ease-in-out overflow-hidden ${
          isQuickSortExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <p className="text-gray-600 mb-6">
            Organize files quickly with AI-powered actions
          </p>
          
          <div className="grid grid-cols-4 gap-4 mb-4">
            {sortOptions.map((option) => (
              <QuickSortCard
                key={option.id}
                icon={option.icon}
                title={option.title}
                description={option.description}
                isSelected={selectedSort === option.id}
                onClick={() => setSelectedSort(option.id)}
              />
            ))}
          </div>

          <button
            onClick={handleStart}
            disabled={!selectedSort}
            className={`w-full px-6 py-2 rounded-lg font-medium transition-all ${
              selectedSort
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            Start
          </button>
        </div>
      </div>

      {/* File Explorer Grid */}
      <div className={`grid gap-6 h-full ${
        isChatMaximized ? 'grid-cols-1' : 'grid-cols-2'
      }`}>
        <WatchedFolders 
          folders={watchedFolders}
          onAddFolder={handleAddWatchedFolder}
          onToggleStatus={handleToggleFolderStatus}
          onEditPath={handleEditFolderPath}
          onDelete={handleDeleteFolder}
          onProcessFolder={handleProcessFolder}
          processingFolder={processingFolder}
          backendOnline={backendStatus === 'online'}
        />
        <Categories 
          categories={categories}
          onAddCategory={handleAddCategory}
          onEditPath={handleEditCategoryPath}
          onDelete={handleDeleteCategory}
        />
      </div>
    </div>
  );
};

export default FileExplorer;