import React from 'react';
import WatchedFolders from '../ui/watchedfolders';
import Categories from '../ui/categories';

const FileExplorer = () => {
  return (
    <div className="flex-1 p-6 overflow-hidden">
      <div className="grid grid-cols-2 gap-6 h-full">
        <WatchedFolders />
        <Categories />
      </div>
    </div>
  );
};

export default FileExplorer;