import React, { useState } from 'react';
import { Upload, Folder, X } from 'lucide-react';

const UploadScan = () => {
  const [showFilePopup, setShowFilePopup] = useState(false);
  const [showFolderPopup, setShowFolderPopup] = useState(false);

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="rounded-lg border p-8" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <div className="flex items-center space-x-2 mb-6">
              <Upload className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
              <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Upload Files</h3>
            </div>

            {/* Upload box */}
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
              <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style={{
                backgroundColor: 'var(--theme-bg-tertiary)'
              }}>
                <Upload className="w-8 h-8" style={{ color: 'var(--theme-text-tertiary)' }} />
              </div>
              <h4 className="text-lg font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
                Drop files here or click to upload
              </h4>
              <p className="mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
                Support for images, videos, documents, and archives
              </p>

              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setShowFilePopup(true)}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:opacity-80 transition-colors"
                  style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    color: 'var(--theme-text-primary)'
                  }}
                >
                  <Upload className="w-4 h-4" />
                  <span>Choose Files</span>
                </button>
                <button
                  onClick={() => setShowFolderPopup(true)}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:opacity-80 transition-colors"
                  style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    color: 'var(--theme-text-primary)'
                  }}
                >
                  <Folder className="w-4 h-4" />
                  <span>Choose Folder</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* File Popup */}
      {showFilePopup && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="rounded-lg p-6 shadow-lg w-96" style={{
            backgroundColor: 'var(--theme-bg-secondary)'
          }}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Upload Files</h2>
              <button onClick={() => setShowFilePopup(false)}>
                <X className="w-5 h-5 hover:opacity-70" style={{ color: 'var(--theme-text-tertiary)' }} />
              </button>
            </div>
            <input 
              type="file" 
              multiple 
              className="mb-4 w-full" 
              style={{
                color: 'var(--theme-text-primary)'
              }}
            />
            <button
              className="w-full py-2 rounded-lg hover:opacity-90 transition-colors"
              style={{
                backgroundColor: 'var(--theme-primary)',
                color: '#ffffff'
              }}
              onClick={() => setShowFilePopup(false)}
            >
              Upload
            </button>
          </div>
        </div>
      )}

      {/* Folder Popup */}
      {showFolderPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="rounded-lg p-6 shadow-lg w-96" style={{
            backgroundColor: 'var(--theme-bg-secondary)'
          }}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Upload Folder</h2>
              <button onClick={() => setShowFolderPopup(false)}>
                <X className="w-5 h-5 hover:opacity-70" style={{ color: 'var(--theme-text-tertiary)' }} />
              </button>
            </div>
            <input 
              type="file" 
              webkitdirectory="true" 
              directory="true" 
              className="mb-4 w-full" 
              style={{
                color: 'var(--theme-text-primary)'
              }}
            />
            <button
              className="w-full py-2 rounded-lg hover:opacity-90 transition-colors"
              style={{
                backgroundColor: 'var(--theme-primary)',
                color: '#ffffff'
              }}
              onClick={() => setShowFolderPopup(false)}
            >
              Upload
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadScan;