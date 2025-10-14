import React, { useState } from 'react';
import { Zap, Image, Calendar, HardDrive, Copy } from 'lucide-react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';

const QuickSortCard = ({ icon: Icon, title, description, isSelected, onClick }) => (
  <button
    onClick={onClick}
    className="flex flex-col items-center justify-center p-6 rounded-lg border-2 transition-all"
    style={{
      borderColor: isSelected ? 'var(--theme-primary)' : 'var(--theme-border-primary)',
      backgroundColor: isSelected ? 'rgba(37, 99, 235, 0.1)' : 'var(--theme-bg-secondary)'
    }}
    onMouseEnter={(e) => {
      if (!isSelected) {
        e.currentTarget.style.borderColor = 'var(--theme-border-primary)';
        e.currentTarget.style.backgroundColor = 'var(--theme-card-hover)';
      }
    }}
    onMouseLeave={(e) => {
      if (!isSelected) {
        e.currentTarget.style.borderColor = 'var(--theme-border-primary)';
        e.currentTarget.style.backgroundColor = 'var(--theme-bg-secondary)';
      }
    }}
  >
    <Icon 
      className="w-8 h-8 mb-3" 
      style={{ color: isSelected ? 'var(--theme-primary)' : 'var(--theme-text-secondary)' }}
    />
    <h3 className="font-semibold mb-1" style={{ color: 'var(--theme-text-primary)' }}>
      {title}
    </h3>
    <p className="text-sm" style={{ color: 'var(--theme-text-secondary)' }}>
      {description}
    </p>
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
          <Zap className="w-6 h-6" style={{ color: 'var(--theme-text-primary)' }} />
          <h2 className="text-2xl font-semibold" style={{ color: 'var(--theme-text-primary)' }}>
            Quick Sort
          </h2>
        </div>
        <p className="mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
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
          className="w-full px-6 py-2 rounded-lg font-medium transition-all"
          style={{
            backgroundColor: selectedSort ? 'var(--theme-primary)' : 'var(--theme-border-primary)',
            color: selectedSort ? '#ffffff' : 'var(--theme-text-tertiary)',
            cursor: selectedSort ? 'pointer' : 'not-allowed',
            opacity: selectedSort ? 1 : 0.6
          }}
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