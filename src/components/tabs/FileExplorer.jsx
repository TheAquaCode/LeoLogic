// src/components/tabs/FileExplorer.jsx - Enhanced with backend integration
import React, { useState, useEffect, useRef } from 'react';
import { Zap, ChevronDown, AlertCircle } from 'lucide-react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';
import { loadFromStorage, saveToStorage } from '../../utils/storage';
import apiService from '../../services/api';

const FileExplorer = ({ isChatMaximized }) => {
  const [isProcessingAll, setIsProcessingAll] = useState(false);
  const [isQuickSortExpanded, setIsQuickSortExpanded] = useState(() => {
    return loadFromStorage('QUICK_SORT_EXPANDED') ?? true;
  });

  // Ensure active/paused states are properly initialized from storage
  const initializeFromStorage = () => {
    const savedFolders = loadFromStorage('watched_folders', []);
    const savedCategories = loadFromStorage('categories', []);

    // Ensure each folder has a status and file count
    const foldersWithDefaults = savedFolders.map(folder => ({
      ...folder,
      status: folder.status || 'Active', // Default to Active if not set
      fileCount: folder.fileCount !== undefined && folder.fileCount !== null ? folder.fileCount : 0 // Ensure fileCount exists and is 0 if not set
    }));
    saveToStorage('watched_folders', foldersWithDefaults);

    return { folders: foldersWithDefaults, categories: savedCategories };
  };

  const initialData = initializeFromStorage();

  // Backend connection state
  const [backendStatus, setBackendStatus] = useState('checking');
  const [watchedFolders, setWatchedFolders] = useState(initialData.folders);
  const [categories, setCategories] = useState(initialData.categories);
  const [error, setError] = useState(null);
  const [processingFolder, setProcessingFolder] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(() => {
    try {
      const raw = localStorage.getItem('processing_progress');
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const progressPollRef = useRef(null);

  // Save expanded state whenever it changes
  useEffect(() => {
    saveToStorage('QUICK_SORT_EXPANDED', isQuickSortExpanded);
  }, [isQuickSortExpanded]);

  // Persist categories to localStorage whenever they change
  useEffect(() => {
    try {
      saveToStorage('categories', Array.isArray(categories) ? categories : []);
    } catch (e) {
      console.error('Error saving categories to storage:', e);
    }
  }, [categories]);

  // Check backend status and load data (Manual trigger)
  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  // Automatic Polling for Updates (e.g. from Chatbot)
  useEffect(() => {
    const interval = setInterval(() => {
      // Don't poll if we are in the middle of a heavy operation to avoid jitter
      if (!isProcessingAll && !processingFolder) {
        loadData();
      }
    }, 4000); // Check every 4 seconds

    return () => clearInterval(interval);
  }, [isProcessingAll, processingFolder]);

  // Resume polling if a processing job was active when component mounted
  useEffect(() => {
    try {
      const storedFolder = localStorage.getItem('processing_folder');
      if (storedFolder) {
        const folderId = Number(storedFolder);
        setProcessingFolder(folderId);
        startProgressPolling(folderId);
      }
    } catch (e) {
      console.error('Error restoring processing state:', e);
    }

    return () => {
      // cleanup polling
      if (progressPollRef.current) {
        clearInterval(progressPollRef.current);
        progressPollRef.current = null;
      }
    };
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
    try {
      const isOnline = await checkBackendStatus();
      if (isOnline) {
        // Load from backend
        const [foldersResult, categoriesResult] = await Promise.allSettled([
          apiService.getWatchedFolders(),
          apiService.getCategories()
        ]);

        if (foldersResult.status === 'fulfilled') {
          const foldersData = foldersResult.value;
          setWatchedFolders(prev => {
            const newFolders = Array.isArray(foldersData) ? foldersData : [];
            
            // Only update if data actually changed to prevent re-renders?
            // For now, mapping ensures local status is preserved if backend doesn't track it fully yet,
            // though backend is authoritative for ID and Path.
            const updatedFolders = newFolders.map(newFolder => {
              const localFolder = prev.find(f => f.id === newFolder.id);
              const fileCount = Number(newFolder.fileCount ?? 0);
              
              return {
                ...newFolder,
                // If backend sent a status, use it, otherwise fall back to local or Active
                status: newFolder.status || localFolder?.status || 'Active',
                fileCount: isNaN(fileCount) ? 0 : fileCount
              };
            });
            saveToStorage('watched_folders', updatedFolders);
            return updatedFolders;
          });
        }
          
        if (categoriesResult.status === 'fulfilled') {
          const categoriesData = Array.isArray(categoriesResult.value) ? categoriesResult.value : [];
          setCategories(categoriesData);
          // save fetched categories so they are available instantly next load
          try {
            saveToStorage('categories', categoriesData);
          } catch (e) {
            console.error('Error saving fetched categories to storage:', e);
          }
        }
      }
    } catch (error) {
      // Silent error on polling to avoid spam
      if (!isProcessingAll) {
        console.error('Error loading data:', error);
      }
    }
  };

  const handleProcessAllFolders = async () => {
    if (backendStatus !== 'online') {
      alert('Backend must be running to process files');
      return;
    }

    const activeFolders = watchedFolders.filter(folder => folder.status === 'Active');
    
    if (activeFolders.length === 0) {
      alert('No active watched folders to process');
      return;
    }

    if (!window.confirm(`Process all files from ${activeFolders.length} active folder(s)?`)) {
      return;
    }

    setIsProcessingAll(true);
    const results = [];
    
    try {
      for (const folder of activeFolders) {
        try {
          console.log(`Processing folder: ${folder.name}`);
          const result = await apiService.processFolderFiles(folder.id);
          results.push({
            folderName: folder.name,
            processed: result.processed,
            fileCount: result.fileCount
          });
          
          // Update folder file count
          setWatchedFolders(prev => {
            const updatedFolders = prev.map(f => 
              f.id === folder.id ? { ...f, fileCount: result.fileCount || 0 } : f
            );
            saveToStorage('watched_folders', updatedFolders);
            return updatedFolders;
          });
        } catch (error) {
          console.error(`Error processing folder ${folder.name}:`, error);
          results.push({
            folderName: folder.name,
            error: error.message
          });
        }
      }
      
      // Show summary
      const totalProcessed = results.reduce((sum, r) => sum + (r.processed || 0), 0);
      const successCount = results.filter(r => !r.error).length;
      const errorCount = results.filter(r => r.error).length;
      
      let message = `Processing complete!\n\n`;
      message += `Total files processed: ${totalProcessed}\n`;
      message += `Successful folders: ${successCount}\n`;
      if (errorCount > 0) {
        message += `Failed folders: ${errorCount}\n`;
      }
      message += `\nCheck the console for detailed results.`;
      
      alert(message);
      console.log('Processing results:', results);
      
      // Trigger a full refresh
      setRefreshTrigger(prev => prev + 1);
      
    } catch (error) {
      console.error('Error processing folders:', error);
      alert('Error processing folders: ' + error.message);
    } finally {
      setIsProcessingAll(false);
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
      
      // Create new folder object with guaranteed status
      const newFolder = {
        id: Date.now(),
        name: folderName,
        path: folderPath,
        files: 0,
        lastActivity: 'Just now',
        status: 'Active'  // Always initialize with Active status
      };

      // Update local state immediately
      const updatedFolders = [...watchedFolders, newFolder];
      setWatchedFolders(updatedFolders);
      saveToStorage('watched_folders', updatedFolders);

      // Sync with backend if available
      if (backendStatus === 'online') {
        try {
          const result = await apiService.addWatchedFolder({
            name: folderName,
            path: folderPath
          });
          
          // Update with backend response while preserving status
          setWatchedFolders(prev => 
            prev.map(f => f.id === newFolder.id ? { ...result.folder, status: 'Active' } : f)
          );
        } catch (error) {
          console.error('Error syncing with backend:', error);
          // Keep local changes even if backend sync fails
        }
      }
    } catch (error) {
      console.error('Error adding folder:', error);
      alert('Error adding folder: ' + error.message);
    }
  };

  const handleToggleFolderStatus = async (folderId) => {
    // Immediately update local state for instant UI feedback
    const currentFolders = watchedFolders;
    const updated = currentFolders.map(folder => 
      folder.id === folderId 
        ? { ...folder, status: folder.status === 'Active' ? 'Paused' : 'Active' }
        : folder
    );
    setWatchedFolders(updated);
    saveToStorage('watched_folders', updated);

    // Then sync with backend if available
    if (backendStatus === 'online') {
      try {
        const result = await apiService.toggleFolderStatus(folderId);
        setWatchedFolders(prev => prev.map(f => 
          f.id === folderId ? { ...f, ...result.folder } : f
        ));
      } catch (error) {
        console.error('Error syncing folder status with backend:', error);
        // Revert to previous state on error
        setWatchedFolders(currentFolders);
        saveToStorage('watched_folders', currentFolders);
      }
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

  const handleOpenFolderLocation = async (folderPath) => {
    try {
      const openFolderAPI = window.electron?.openFolder || 
                           window.electronAPI?.openFolder || 
                           window.api?.openFolder;
    
      if (openFolderAPI) {
        await openFolderAPI(folderPath);
      } else {
        alert('Opening folder location is only available in the Electron app');
      }
    } catch (error) {
      console.error('Error opening folder location:', error);
      alert('Error opening folder location: ' + error.message);
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

    try {
      // Start processing in background
      const resp = await apiService.startProcessFolder(folderId);

      // If accepted, begin polling for progress
      setProcessingFolder(folderId);
      try { localStorage.setItem('processing_folder', String(folderId)); } catch {}
      // initialize progress entry
      const initProgress = { ...(processingProgress || {}) };
      initProgress[folderId] = { completed: 0, total: resp.total || 0, failed: 0 };
      setProcessingProgress(initProgress);
      try { localStorage.setItem('processing_progress', JSON.stringify(initProgress)); } catch {}

      startProgressPolling(folderId);
    } catch (error) {
      console.error('Error starting folder processing:', error);
      alert('Error starting processing: ' + (error.message || String(error)));
      setProcessingFolder(null);
    }
  };

  const startProgressPolling = (folderId) => {
    // clear existing
    if (progressPollRef.current) {
      clearInterval(progressPollRef.current);
      progressPollRef.current = null;
    }

    progressPollRef.current = setInterval(async () => {
      try {
        const prog = await apiService.getProcessProgress(folderId);
        if (prog && (prog.total !== undefined)) {
          const updated = { ...(processingProgress || {}) };
          updated[folderId] = {
            completed: prog.completed || 0,
            total: prog.total || 0,
            failed: prog.failed || 0,
            in_progress: prog.in_progress || 0
          };
          setProcessingProgress(updated);
          try { localStorage.setItem('processing_progress', JSON.stringify(updated)); } catch {}

          // If completed (success + failed >= total)
          const totalProcessed = (updated[folderId].completed || 0) + (updated[folderId].failed || 0);
          if (updated[folderId].total > 0 && totalProcessed >= updated[folderId].total) {
            // stop polling, clear stored processing folder after a short delay
            clearInterval(progressPollRef.current);
            progressPollRef.current = null;

            // update folder counts and refresh
            setRefreshTrigger(prev => prev + 1);

            setTimeout(() => {
              setProcessingFolder(null);
              try { localStorage.removeItem('processing_folder'); } catch {}
              // Keep progress record for a short period (optional), or remove:
              try { localStorage.removeItem('processing_progress'); } catch {}
              setProcessingProgress(prev => {
                const copy = { ...(prev || {}) };
                delete copy[folderId];
                return copy;
              });
            }, 800);
          }
        }
      } catch (err) {
        console.error('Error polling progress:', err);
      }
    }, 800);
  };

  // Categories handlers
  const handleAddCategory = async (categoryData) => {
    try {
      if (backendStatus === 'online') {
        const result = await apiService.addCategory(categoryData);
        setCategories(prev => [...prev, result.category]);
        // localStorage will be updated by the categories useEffect above
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
        const updated = [...categories, newCategory];
        setCategories(updated);
        saveToStorage('categories', updated);
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

  const handleRenameCategory = async (categoryId, newName) => {
    try {
      // Optimistically update UI
      const updatedCategories = categories.map(category =>
        category.id === categoryId ? { ...category, name: newName } : category
      );
      setCategories(updatedCategories);
      saveToStorage('categories', updatedCategories);

      // Sync with backend if online
      if (backendStatus === 'online') {
        try {
          const result = await apiService.updateCategory(categoryId, { name: newName });
          if (result.category) {
            // Update with backend response
            setCategories(prevCategories =>
              prevCategories.map(category =>
                category.id === categoryId ? { ...category, ...result.category } : category
              )
            );
          }
        } catch (error) {
          // Revert on backend error
          console.error('Error updating category:', error);
          setCategories(categories);
          saveToStorage('categories', categories);
          alert('Error: ' + error.message);
        }
      }
    } catch (error) {
      console.error('Error renaming category:', error);
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

  const activeFoldersCount = watchedFolders.filter(folder => folder.status === 'Active').length;
  const hasActiveFolders = activeFoldersCount > 0;

  return (
    <div 
      className={`flex-1 p-6 overflow-auto transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`}
    >
      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900 dark:text-red-300">Error</p>
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
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
            Process all files from all watched folders with AI-powered organization
          </p>
          
          <button
            onClick={handleProcessAllFolders}
            disabled={!hasActiveFolders || backendStatus !== 'online' || isProcessingAll}
            className={`w-full px-6 py-4 rounded-lg font-semibold text-lg transition-all ${
              hasActiveFolders && backendStatus === 'online' && !isProcessingAll
                ? 'bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 shadow-lg hover:shadow-xl'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
            }`}
          >
            {isProcessingAll ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              `Process All Folders ${hasActiveFolders ? `(${activeFoldersCount})` : ''}`
            )}
          </button>
          
          {!hasActiveFolders && watchedFolders.length > 0 && (
            <p className="text-sm text-amber-600 dark:text-amber-400 mt-2 text-center">
              No active folders. Activate at least one folder to process.
            </p>
          )}
          
          
        </div>
      </div>

      {/* File Explorer Grid */}
      <div className={`grid gap-6 h-full ${
        isChatMaximized ? 'grid-cols-1' : 'grid-cols-2'
      }`}>
        <WatchedFolders 
          folders={Array.isArray(watchedFolders) ? watchedFolders : []}
          onAddFolder={handleAddWatchedFolder}
          onToggleStatus={handleToggleFolderStatus}
          onEditPath={handleEditFolderPath}
          onDelete={handleDeleteFolder}
          onProcessFolder={handleProcessFolder}
          onOpenLocation={handleOpenFolderLocation}
          processingFolder={processingFolder}
          processingProgress={processingProgress}
          backendOnline={backendStatus === 'online'}
        />
        <Categories 
          categories={Array.isArray(categories) ? categories : []}
          onAddCategory={handleAddCategory}
          onEditPath={handleEditCategoryPath}
          onDelete={handleDeleteCategory}
          onRenameCategory={handleRenameCategory}
          onOpenLocation={handleOpenFolderLocation}
        />
      </div>
    </div>
  );
};

export default FileExplorer;