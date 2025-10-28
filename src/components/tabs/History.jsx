import React from 'react';
import StatsCards from '../ui/statscards';
import FileMovements from '../ui/filemovements';

const History = ({ isChatMaximized }) => {
  return (
    <div 
      className={`flex-1 p-6 overflow-hidden transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`}
    >
      <StatsCards isChatMaximized={isChatMaximized} />
      <FileMovements isChatMaximized={isChatMaximized} />
    </div>
  );
};

export default History;