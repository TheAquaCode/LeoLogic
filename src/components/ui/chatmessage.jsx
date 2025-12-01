import React from 'react';
import { FolderOpen } from 'lucide-react';

const ChatMessage = ({ message }) => {
  // Simple Markdown Bold Parser
  const formatMessage = (content) => {
    if (!content) return null;
    const parts = content.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start space-x-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          message.type === 'ai' ? 'bg-black text-white' : 'bg-blue-600 text-white'
        }`}>
          {message.type === 'ai' ? (
            <FolderOpen className="w-4 h-4" />
          ) : (
            <div className="w-4 h-4 rounded-full bg-white"></div>
          )}
        </div>
        
        {/* Message Content */}
        <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
          <div className={`rounded-2xl px-4 py-3 ${
            message.type === 'ai' 
              ? 'bg-gray-100 text-gray-900' 
              : 'bg-blue-600 text-white'
          }`}>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {formatMessage(message.content)}
            </p>
          </div>
          <span className="text-xs text-gray-500 mt-1">{message.timestamp}</span>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;