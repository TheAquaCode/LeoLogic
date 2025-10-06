import React from 'react';
import StatsCards from '../ui/statscards';
import FileMovements from '../ui/filemovements';

const History = () => {
  return (
    <div className="flex-1 p-6 overflow-hidden">
      <StatsCards />
      <FileMovements />
    </div>
  );
};

export default History;