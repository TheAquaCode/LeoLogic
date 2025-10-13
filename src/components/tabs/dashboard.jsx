import React, { useState } from 'react';
import { FileText, Folder, Archive, Image, Music, Video } from 'lucide-react';

const Dashboard = () => {
  const [files] = useState([
    { id: '1', name: 'Project_Proposal.pdf', type: 'document', size: '2.4 MB', date: '2024-10-10' },
    { id: '2', name: 'Vacation_Photo.jpg', type: 'image', size: '3.8 MB', date: '2024-10-09' },
    { id: '3', name: 'Meeting_Recording.mp3', type: 'audio', size: '15.2 MB', date: '2024-10-08' },
    { id: '4', name: 'Tutorial_Video.mp4', type: 'video', size: '45.6 MB', date: '2024-10-07' },
    { id: '5', name: 'Archive_2024.zip', type: 'archive', size: '128.5 MB', date: '2024-10-06' },
    { id: '6', name: 'Budget_Report.xlsx', type: 'document', size: '1.2 MB', date: '2024-10-05' },
  ]);

  const getFileIcon = (type) => {
    switch (type) {
      case 'document': return <FileText className="w-5 h-5 text-blue-500" />;
      case 'image': return <Image className="w-5 h-5 text-green-500" />;
      case 'audio': return <Music className="w-5 h-5 text-purple-500" />;
      case 'video': return <Video className="w-5 h-5 text-red-500" />;
      case 'archive': return <Archive className="w-5 h-5 text-yellow-500" />;
      default: return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="flex-1 overflow-auto p-8">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Files</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">1,247</p>
            </div>
            <FileText className="w-12 h-12 text-blue-500 opacity-20" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Organized</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">892</p>
            </div>
            <Folder className="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Needs Sorting</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">355</p>
            </div>
            <Archive className="w-12 h-12 text-orange-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Recent Files Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">Recent Files</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {files.map(file => (
            <div key={file.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getFileIcon(file.type)}
                  <div>
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">{file.size} • {file.date}</p>
                  </div>
                </div>
                <button className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                  Sort
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;