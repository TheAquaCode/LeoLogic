import React, { useState, useEffect } from 'react';
import { Zap, Image, Calendar, HardDrive, Copy, ChevronDown } from 'lucide-react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';
import { loadFromStorage, saveToStorage } from '../../utils/storage';

const QuickSortCard = ({ icon: Icon, title, description, isSelected, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${
      isSelected
        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
        : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
    }`}
  >
    <Icon className={`w-6 h-6 mb-2 ${isSelected ? 'text-blue-500' : 'text-gray-700 dark:text-gray-300'}`} />
    <h3 className={`font-semibold mb-0.5 text-sm ${isSelected ? 'text-gray-900 dark:text-white' : 'text-gray-900 dark:text-gray-100'}`}>{title}</h3>
    <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>
  </button>
);

const FileExplorer = ({ watchedFolders, setWatchedFolders, categories, setCategories }) => {
  const [selectedSort, setSelectedSort] = useState(null);
  const [isQuickSortExpanded, setIsQuickSortExpanded] = useState(() => {
    return loadFromStorage('QUICK_SORT_EXPANDED') ?? true; // Default to expanded if no saved state
  });

  // Save expanded state whenever it changes
  useEffect(() => {
    saveToStorage('QUICK_SORT_EXPANDED', isQuickSortExpanded);
  }, [isQuickSortExpanded]);

  const sortOptions = [
    { id: 'type', icon: Image, title: 'By Type', description: 'Sort by file type' },
    { id: 'date', icon: Calendar, title: 'By Date', description: 'Sort by date modified' },
    { id: 'size', icon: HardDrive, title: 'By Size', description: 'Sort by file size' },
    { id: 'duplicates', icon: Copy, title: 'Duplicates', description: 'Find duplicate files' }
  ];

  const handleStart = () => {
    if (selectedSort) {
      console.log('Starting quick sort:', selectedSort);
      // Add your sort logic here
    }
  };

  const handleAddWatchedFolder = async () => {
    // Check if running in Electron - try multiple possible API structures
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (selectFolderAPI) {
      try {
        const folderPath = await selectFolderAPI();
        if (folderPath) {
          const folderName = folderPath.split('/').pop() || folderPath.split('\\').pop();
          const newFolder = {
            id: Date.now(),
            name: folderName,
            path: folderPath,
            files: 0,
            lastActivity: 'Just now',
            status: 'Active'
          };
          setWatchedFolders([...watchedFolders, newFolder]);
        }
      } catch (error) {
        console.error('Error selecting folder:', error);
        alert('Error selecting folder. Please try again.');
      }
    } else {
      console.log('Available APIs:', { 
        electron: window.electron, 
        electronAPI: window.electronAPI, 
        api: window.api 
      });
      alert('Folder selection is only available in the Electron app');
    }
  };

  const handleToggleFolderStatus = (folderId) => {
    setWatchedFolders(watchedFolders.map(folder => 
      folder.id === folderId 
        ? { ...folder, status: folder.status === 'Active' ? 'Paused' : 'Active' }
        : folder
    ));
  };

  const handleEditFolderPath = async (folderId) => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (selectFolderAPI) {
      try {
        const folderPath = await selectFolderAPI();
        if (folderPath) {
          const folderName = folderPath.split('/').pop() || folderPath.split('\\').pop();
          setWatchedFolders(watchedFolders.map(folder =>
            folder.id === folderId
              ? { ...folder, name: folderName, path: folderPath }
              : folder
          ));
        }
      } catch (error) {
        console.error('Error selecting folder:', error);
      }
    }
  };

  const handleDeleteFolder = (folderId) => {
    setWatchedFolders(watchedFolders.filter(folder => folder.id !== folderId));
  };

  const handleAddCategory = async (categoryData) => {
    const newCategory = {
      id: Date.now(),
      name: categoryData.name,
      path: categoryData.path,
      fileTypes: [],
      rules: 0,
      color: 'bg-blue-500'
    };
    setCategories([...categories, newCategory]);
  };

  const handleEditCategoryPath = async (categoryId) => {
    const selectFolderAPI = window.electron?.selectFolder || 
                           window.electronAPI?.selectFolder || 
                           window.api?.selectFolder;
    
    if (selectFolderAPI) {
      try {
        const folderPath = await selectFolderAPI();
        if (folderPath) {
          setCategories(categories.map(category =>
            category.id === categoryId
              ? { ...category, path: folderPath }
              : category
          ));
        }
      } catch (error) {
        console.error('Error selecting folder:', error);
      }
    }
  };

  const handleDeleteCategory = (categoryId) => {
    setCategories(categories.filter(category => category.id !== categoryId));
  };

  return (
    <div className="flex-1 p-6 overflow-auto">
      {/* Quick Sort Section */}
      <div className="mb-8">
        <button 
          onClick={() => setIsQuickSortExpanded(!isQuickSortExpanded)}
          className="flex items-center gap-2 mb-2 w-full group"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-gray-700 dark:text-gray-300" />
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Quick Sort</h2>
          </div>
          <ChevronDown 
            className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-200 ease-in-out ml-2 ${
              isQuickSortExpanded ? 'transform rotate-180' : ''
            }`}
          />
        </button>
        
        <div className={`transition-all duration-200 ease-in-out overflow-hidden ${
          isQuickSortExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
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
      <div className="grid grid-cols-2 gap-6 h-full">
        <WatchedFolders 
          folders={watchedFolders}
          onAddFolder={handleAddWatchedFolder}
          onToggleStatus={handleToggleFolderStatus}
          onEditPath={handleEditFolderPath}
          onDelete={handleDeleteFolder}
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