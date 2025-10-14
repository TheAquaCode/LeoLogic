import React, { useState } from 'react';
import { Zap, Image, Calendar, HardDrive, Copy } from 'lucide-react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';

const QuickSortCard = ({ icon: Icon, title, description, isSelected, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center p-6 rounded-lg border-2 transition-all ${
      isSelected
        ? 'border-blue-500 bg-blue-50'
        : 'border-gray-200 hover:border-gray-300 bg-white'
    }`}
  >
    <Icon className={`w-8 h-8 mb-3 ${isSelected ? 'text-blue-500' : 'text-gray-700'}`} />
    <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
    <p className="text-sm text-gray-500">{description}</p>
  </button>
);

const FileExplorer = () => {
  const [selectedSort, setSelectedSort] = useState(null);

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

  return (
    <div className="flex-1 p-6 overflow-auto">
      {/* Quick Sort Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Zap className="w-6 h-6" />
          <h2 className="text-2xl font-semibold">Quick Sort</h2>
        </div>
        <p className="text-gray-600 mb-6">Organize files quickly with AI-powered actions</p>
        
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

      {/* Original File Explorer Grid */}
      <div className="grid grid-cols-2 gap-6 h-full">
        <WatchedFolders />
        <Categories />
      </div>
    </div>
  );
};

export default FileExplorer;