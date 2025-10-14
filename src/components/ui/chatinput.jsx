import React from 'react';
import { Mic, Send } from 'lucide-react';

const ChatInput = ({ chatInput, setChatInput, handleSendMessage, handleKeyPress }) => {
  return (
    <div className="border-t border-gray-200 p-4 flex-shrink-0">
      <div className="relative">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me to organize your files, find duplicates, or clean up old files..."
          className="w-full pl-4 pr-20 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <Mic className="w-4 h-4" />
          </button>
          <button
            onClick={handleSendMessage}
            disabled={!chatInput.trim()}
            className="p-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;