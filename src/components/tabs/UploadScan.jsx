import React from 'react';
import { Upload, Folder } from 'lucide-react';

const UploadScan = () => {
  return (
    <div className="flex-1 flex flex-col">
      {/* Upload Content */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            <div className="flex items-center space-x-2 mb-6">
              <Upload className="w-5 h-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Upload Files</h3>
            </div>
            
            {/* Drag and Drop Area */}
            <div 
              className="border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer"
              style={{
                borderColor: 'var(--theme-border-primary)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--theme-primary)';
                e.currentTarget.style.backgroundColor = 'var(--theme-card-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--theme-border-primary)';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="w-8 h-8 text-gray-400" />
              </div>
              <h4 className="text-lg font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
                Drop files here or click to upload
              </h4>
              <p className="mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
                Support for images, videos, documents, and archives
              </p>
              
              <div className="flex justify-center space-x-4">
                <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                  <Upload className="w-4 h-4" />
                  <span>Choose Files</span>
                </button>
                <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                  <Folder className="w-4 h-4" />
                  <span>Choose Folder</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadScan;