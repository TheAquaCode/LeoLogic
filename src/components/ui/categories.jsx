import React from 'react';
import { Tag, Plus, MoreHorizontal, Folder } from 'lucide-react';
import { categories } from '../../data/mockdata';

const Categories = () => {
  return (
    <div className="flex flex-col min-h-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Tag className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Categories</h3>
        </div>
        <button className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>
      <p className="text-sm text-gray-600 mb-6">User-defined organization rules</p>

      <div className="space-y-3 overflow-y-auto flex-1">
        {categories.map((category, index) => (
          <div key={index} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-8 h-8 ${category.color} rounded flex items-center justify-center`}>
                  <Folder className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">{category.name}</h4>
                  <p className="text-sm text-gray-500">{category.path}</p>
                </div>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <MoreHorizontal className="w-5 h-5" />
              </button>
            </div>
            
            {category.fileTypes.length > 0 && (
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
                <span className="text-gray-600">{category.rules} rules</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Categories;