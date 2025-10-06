import React from 'react';
import { Image, Check, ArrowRight, RotateCcw, MoreHorizontal } from 'lucide-react';
import { fileMovements } from '../../data/mockdata';

const FileMovements = () => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col min-h-0">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent File Movements</h3>
        <span className="text-sm text-gray-500">{fileMovements.length} files</span>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="divide-y divide-gray-100">
          {fileMovements.map((movement) => (
            <div key={movement.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
                    <Image className="w-4 h-4 text-blue-600" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900 truncate">{movement.filename}</h4>
                      <span className="text-xs text-gray-500 flex-shrink-0">{movement.confidence}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-sm text-gray-500">{movement.timeAgo}</span>
                      <span className="text-gray-300">•</span>
                      <span className="text-sm text-gray-600">{movement.detection}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500">
                      <span>{movement.fromPath}</span>
                      <ArrowRight className="w-3 h-3" />
                      <span>{movement.toPath}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                    <Check className="w-3 h-3 mr-1" />
                    Done
                  </span>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FileMovements;