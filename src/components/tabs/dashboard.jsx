import React, { useState } from 'react';
import { Send, Folder, FileText, Image, Music, Video, Archive } from 'lucide-react';

const AIFileSorter = () => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      text: "Hello! I'm your AI file sorting assistant. I can help you organize, categorize, and manage your files. Try asking me to sort files by type, date, or size!",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
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

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: `I understand you want to "${inputText}". I can help you organize these files by type, name, date, or size. Would you like me to create folders for different file types?`,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);

    setInputText('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-8">
          <Folder className="w-8 h-8 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-800">File Sorter</h1>
        </div>
        
        <nav className="space-y-2">
          <button className="w-full text-left px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium">
            Dashboard
          </button>
          <button className="w-full text-left px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            All Files
          </button>
          <button className="w-full text-left px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            Recent
          </button>
          <button className="w-full text-left px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            Favorites
          </button>
        </nav>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-500 mb-3">STORAGE</h3>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">125 GB of 500 GB used</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '25%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
          <p className="text-gray-600 text-sm mt-1">Manage and organize your files with AI assistance</p>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto p-8">
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
      </div>

      {/* Chat Panel */}
      <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">AI Assistant</h3>
          <p className="text-sm text-gray-500">Ask me to help organize your files</p>
        </div>

        <div className="flex-1 overflow-auto p-6 space-y-4">
          {messages.map(message => (
            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.sender === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <p className="text-sm">{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSendMessage}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFileSorter;