import React from 'react';
import { FileText, Check, Clock } from 'lucide-react';

const StatsCards = () => {
  const stats = [
    {
      label: 'Total Files',
      value: '10',
      icon: FileText,
      bgColor: 'bg-gray-100',
      iconColor: 'text-gray-600'
    },
    {
      label: 'Completed',
      value: '7',
      icon: Check,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600'
    },
    {
      label: 'Pending',
      value: '2',
      icon: Clock,
      bgColor: 'bg-yellow-100',
      iconColor: 'text-yellow-600'
    },
    {
      label: 'Success Rate',
      value: '70%',
      icon: Check,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600'
    }
  ];

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => {
        const IconComponent = stat.icon;
        return (
          <div key={index} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.label}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
              <div className={`w-8 h-8 ${stat.bgColor} rounded flex items-center justify-center`}>
                <IconComponent className={`w-4 h-4 ${stat.iconColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;