import React, { useState } from 'react';
import ChatMessage from '../ui/chatmessage';
import ChatInput from '../ui/chatinput';
import { initialMessages, aiResponses } from '../../data/mockdata';

const AIAssistant = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [chatInput, setChatInput] = useState('');

  const handleSendMessage = () => {
    if (chatInput.trim()) {
      // Add user message
      const userMessage = {
        id: messages.length + 1,
        type: 'user',
        content: chatInput,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };
      
      // Add AI response
      const aiMessage = {
        id: messages.length + 2,
        type: 'ai',
        content: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };
      
      setMessages(prev => [...prev, userMessage, aiMessage]);
      setChatInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 p-6">
      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full min-h-0">
        {/* Chat Messages Container */}
        <div className="flex-1 bg-white rounded-lg border border-gray-200 flex flex-col min-h-0">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
          </div>
          
          {/* Chat Input */}
          <ChatInput
            chatInput={chatInput}
            setChatInput={setChatInput}
            handleSendMessage={handleSendMessage}
            handleKeyPress={handleKeyPress}
          />
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;