import React, { useState } from 'react';
import { Upload, Folder, X, CheckCircle, AlertCircle, Loader, FileText } from 'lucide-react';
import apiService from '../../services/api';

const UploadScan = ({ isChatMaximized }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  const handleFileSelect = async (files) => {
    const fileArray = Array.from(files);
    setUploadedFiles(fileArray);
    setShowResults(false);
    setResults([]);
  };

  const handleFolderSelect = async (files) => {
    // When selecting a folder, files are provided as FileList
    const fileArray = Array.from(files);
    setUploadedFiles(fileArray);
    setShowResults(false);
    setResults([]);
  };

  const processFiles = async () => {
    if (uploadedFiles.length === 0) {
      alert('Please select files or a folder first');
      return;
    }

    setProcessing(true);
    setShowResults(false);

    let successCount = 0;
    let errorCount = 0;
    let lowConfidenceCount = 0;

    for (const file of uploadedFiles) {
      try {
        // Create FormData to send file to backend
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:5001/api/upload-and-process', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        
        if (result.status === 'success') {
          successCount++;
        } else if (result.status === 'low_confidence') {
          lowConfidenceCount++;
        } else {
          errorCount++;
        }

      } catch (error) {
        console.error(`Error processing ${file.name}:`, error);
        errorCount++;
      }
    }

    setResults([{ successCount, errorCount, lowConfidenceCount, total: uploadedFiles.length }]);
    setProcessing(false);
    setShowResults(true);
    setUploadedFiles([]); // Clear the file list
  };

  return (
    <div className="flex-1 flex flex-col">
      <div 
        className={`flex-1 p-6 transition-all duration-300 ${
          isChatMaximized ? 'pr-[500px]' : ''
        }`}
      >
        <div className={`mx-auto ${isChatMaximized ? 'max-w-2xl' : 'max-w-4xl'}`}>
          {/* Upload Box */}
          <div className="rounded-lg border p-8 mb-6" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <div className="flex items-center space-x-2 mb-6">
              <Upload className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
              <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Upload Files</h3>
            </div>

            {/* Upload box */}
            <div
              className={`border-2 border-dashed rounded-lg text-center transition-colors ${
                isChatMaximized ? 'p-6' : 'p-8'
              }`}
              style={{
                borderColor: 'var(--theme-border-primary)'
              }}
              onDragOver={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = 'var(--theme-primary)';
                e.currentTarget.style.backgroundColor = 'var(--theme-card-hover)';
              }}
              onDragLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--theme-border-primary)';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = 'var(--theme-border-primary)';
                e.currentTarget.style.backgroundColor = 'transparent';
                handleFileSelect(e.dataTransfer.files);
              }}
            >
              <div 
                className={`rounded-full flex items-center justify-center mx-auto mb-3 ${
                  isChatMaximized ? 'w-10 h-10' : 'w-12 h-12'
                }`} 
                style={{
                  backgroundColor: 'var(--theme-bg-tertiary)'
                }}
              >
                <Upload 
                  className={isChatMaximized ? 'w-5 h-5' : 'w-6 h-6'} 
                  style={{ color: 'var(--theme-text-tertiary)' }} 
                />
              </div>
              <h4 
                className={`font-medium mb-1 ${
                  isChatMaximized ? 'text-sm' : 'text-base'
                }`} 
                style={{ color: 'var(--theme-text-primary)' }}
              >
                Drop files here or click to upload
              </h4>
              <p 
                className={`${isChatMaximized ? 'mb-3 text-xs' : 'mb-4 text-sm'}`}
                style={{ color: 'var(--theme-text-secondary)' }}
              >
                Support for images, videos, documents, and archives
              </p>

              <div 
                className={`flex justify-center ${
                  isChatMaximized ? 'flex-col space-y-2' : 'flex-row space-x-3'
                }`}
              >
                <label
                  className={`flex items-center justify-center space-x-2 px-3 py-2 rounded-lg hover:opacity-80 transition-colors cursor-pointer text-sm ${
                    isChatMaximized ? 'w-full' : ''
                  }`}
                  style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    color: 'var(--theme-text-primary)'
                  }}
                >
                  <Upload className="w-4 h-4" />
                  <span>Choose Files</span>
                  <input 
                    type="file" 
                    multiple 
                    className="hidden"
                    onChange={(e) => handleFileSelect(e.target.files)}
                  />
                </label>
                
                <label
                  className={`flex items-center justify-center space-x-2 px-3 py-2 rounded-lg hover:opacity-80 transition-colors cursor-pointer text-sm ${
                    isChatMaximized ? 'w-full' : ''
                  }`}
                  style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    color: 'var(--theme-text-primary)'
                  }}
                >
                  <Folder className="w-4 h-4" />
                  <span>Choose Folder</span>
                  <input 
                    type="file" 
                    webkitdirectory="true"
                    directory="true"
                    multiple
                    className="hidden"
                    onChange={(e) => handleFolderSelect(e.target.files)}
                  />
                </label>
              </div>
            </div>

            {/* Selected Files Preview */}
            {uploadedFiles.length > 0 && !processing && !showResults && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm" style={{ color: 'var(--theme-text-primary)' }}>
                    Selected Files ({uploadedFiles.length})
                  </h4>
                  <button
                    onClick={() => setUploadedFiles([])}
                    className="text-xs text-red-600 hover:text-red-700"
                  >
                    Clear All
                  </button>
                </div>
                <div className="max-h-32 overflow-y-auto space-y-1.5">
                  {uploadedFiles.slice(0, 8).map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 rounded text-xs" style={{
                      backgroundColor: 'var(--theme-bg-tertiary)'
                    }}>
                      <div className="flex items-center space-x-2 flex-1 min-w-0">
                        <FileText className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--theme-text-tertiary)' }} />
                        <span className="truncate" style={{ color: 'var(--theme-text-primary)' }}>
                          {file.name}
                        </span>
                      </div>
                      <span className="ml-2 flex-shrink-0" style={{ color: 'var(--theme-text-secondary)' }}>
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  ))}
                  {uploadedFiles.length > 8 && (
                    <p className="text-xs text-center py-1" style={{ color: 'var(--theme-text-secondary)' }}>
                      And {uploadedFiles.length - 8} more files...
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Processing Status */}
            {processing && (
              <div className="mt-4 text-center py-6">
                <Loader className="w-10 h-10 animate-spin mx-auto mb-3" style={{ color: 'var(--theme-primary)' }} />
                <h4 className="text-base font-medium mb-1" style={{ color: 'var(--theme-text-primary)' }}>
                  Processing Files...
                </h4>
                <p className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>
                  Organizing your files with AI
                </p>
              </div>
            )}

            {/* Results Summary */}
            {showResults && results.length > 0 && (
              <div className="mt-4 p-4 rounded-lg border" style={{
                backgroundColor: 'var(--theme-bg-tertiary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <div className="text-center">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-600" />
                  <h4 className="text-lg font-semibold mb-3" style={{ color: 'var(--theme-text-primary)' }}>
                    Processing Complete!
                  </h4>
                  <div className="flex justify-center space-x-4 mb-3">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{results[0].successCount}</div>
                      <div className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Organized</div>
                    </div>
                    {results[0].lowConfidenceCount > 0 && (
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">{results[0].lowConfidenceCount}</div>
                        <div className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Low Confidence</div>
                      </div>
                    )}
                    {results[0].errorCount > 0 && (
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{results[0].errorCount}</div>
                        <div className="text-xs" style={{ color: 'var(--theme-text-secondary)' }}>Errors</div>
                      </div>
                    )}
                  </div>
                  <p className="text-xs mb-3" style={{ color: 'var(--theme-text-secondary)' }}>
                    Check the History page to see where your files were organized
                  </p>
                  
                </div>
              </div>
            )}

            {/* Process Button */}
            {uploadedFiles.length > 0 && !processing && !showResults && (
              <button
                onClick={processFiles}
                disabled={processing}
                className="w-full mt-4 py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm"
                style={{
                  backgroundColor: processing ? 'var(--theme-border-primary)' : 'var(--theme-primary)',
                  color: '#ffffff'
                }}
              >
                <Upload className="w-4 h-4" />
                <span>Process & Organize Files</span>
              </button>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadScan;