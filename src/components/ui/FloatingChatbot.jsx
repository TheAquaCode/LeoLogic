import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Maximize2, Minimize2, Send, Mic, Loader } from 'lucide-react';

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [position, setPosition] = useState({ x: window.innerWidth - 424, y: window.innerHeight - 688 });
  const [size, setSize] = useState({ width: 400, height: 600 });
  const [isDragging, setIsDragging] = useState(false);
  const [resizeEdge, setResizeEdge] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0, posX: 0, posY: 0 });
  
  // Backend state
  const [modelLoaded, setModelLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isWaitingResponse, setIsWaitingResponse] = useState(false);
  
  const chatRef = useRef(null);
  const messagesEndRef = useRef(null);
  const API_BASE = 'http://localhost:5000';

  // Check model status on mount
  useEffect(() => {
    checkModelStatus();
    const interval = setInterval(checkModelStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isWaitingResponse]);

  const checkModelStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`);
      const data = await response.json();
      
      if (data.model_loaded && !modelLoaded) {
        setModelLoaded(true);
        setIsLoading(false);
      } else if (data.loading) {
        setIsLoading(true);
      }
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const addMessage = (type, content) => {
    const newMessage = {
      id: Date.now(),
      type,
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput('');
    
    // Add user message immediately
    addMessage('user', userMessage);
    
    // Show loading state
    setIsWaitingResponse(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();
      
      setIsWaitingResponse(false);
      
      if (data.response) {
        addMessage('ai', data.response);
      }
      
      if (!data.model_ready) {
        setModelLoaded(false);
      }
    } catch (error) {
      setIsWaitingResponse(false);
      addMessage('ai', 'Sorry, I could not connect to the AI backend. Please make sure the server is running.');
      console.error('Chat error:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMouseDown = (e) => {
    if (isMaximized) return;
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  const handleResizeMouseDown = (e, edge) => {
    if (isMaximized) return;
    e.stopPropagation();
    setResizeEdge(edge);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height,
      posX: position.x,
      posY: position.y
    });
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        const newX = e.clientX - dragOffset.x;
        const newY = e.clientY - dragOffset.y;
        
        const maxX = window.innerWidth - size.width;
        const maxY = window.innerHeight - size.height - 88;
        
        setPosition({
          x: Math.max(0, Math.min(maxX, newX)),
          y: Math.max(0, Math.min(maxY, newY))
        });
      } else if (resizeEdge) {
        let newWidth = size.width;
        let newHeight = size.height;
        let newX = position.x;
        let newY = position.y;

        const deltaX = e.clientX - resizeStart.x;
        const deltaY = e.clientY - resizeStart.y;

        if (resizeEdge.includes('right')) {
          newWidth = Math.max(320, Math.min(window.innerWidth - position.x - 24, resizeStart.width + deltaX));
        }
        if (resizeEdge.includes('left')) {
          const proposedWidth = resizeStart.width - deltaX;
          if (proposedWidth >= 320 && resizeStart.posX + deltaX >= 0) {
            newWidth = proposedWidth;
            newX = resizeStart.posX + deltaX;
          }
        }
        if (resizeEdge.includes('bottom')) {
          newHeight = Math.max(400, Math.min(window.innerHeight - position.y - 88, resizeStart.height + deltaY));
        }
        if (resizeEdge.includes('top')) {
          const proposedHeight = resizeStart.height - deltaY;
          if (proposedHeight >= 400 && resizeStart.posY + deltaY >= 0) {
            newHeight = proposedHeight;
            newY = resizeStart.posY + deltaY;
          }
        }

        setSize({ width: newWidth, height: newHeight });
        setPosition({ x: newX, y: newY });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      setResizeEdge(null);
    };

    if (isDragging || resizeEdge) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, resizeEdge, dragOffset, size, resizeStart, position]);

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
  };

  const chatStyle = isMaximized
    ? { top: 0, left: 0, right: 0, bottom: 0, width: '100%', height: '100%' }
    : { left: `${position.x}px`, top: `${position.y}px`, width: `${size.width}px`, height: `${size.height}px` };

  const getStatusIndicator = () => {
    if (isLoading) return { color: 'bg-yellow-500', text: 'Loading AI...' };
    if (modelLoaded) return { color: 'bg-green-500', text: 'Online' };
    return { color: 'bg-red-500', text: 'Offline' };
  };

  const status = getStatusIndicator();

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 flex items-center justify-center z-50"
        >
          <MessageSquare className="w-6 h-6" />
          {modelLoaded && (
            <span className="absolute top-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
          )}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          ref={chatRef}
          className="fixed bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50"
          style={chatStyle}
        >
          {/* Resize Handles */}
          {!isMaximized && (
            <>
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'top')} className="absolute top-0 left-2 right-2 h-1 cursor-n-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'bottom')} className="absolute bottom-0 left-2 right-2 h-1 cursor-s-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'left')} className="absolute left-0 top-2 bottom-2 w-1 cursor-w-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'right')} className="absolute right-0 top-2 bottom-2 w-1 cursor-e-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'top-left')} className="absolute top-0 left-0 w-2 h-2 cursor-nw-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'top-right')} className="absolute top-0 right-0 w-2 h-2 cursor-ne-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'bottom-left')} className="absolute bottom-0 left-0 w-2 h-2 cursor-sw-resize" />
              <div onMouseDown={(e) => handleResizeMouseDown(e, 'bottom-right')} className="absolute bottom-0 right-0 w-2 h-2 cursor-se-resize" />
            </>
          )}

          {/* Header */}
          <div
            onMouseDown={handleMouseDown}
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-3 rounded-t-lg cursor-move flex items-center justify-between select-none"
          >
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5" />
              <span className="font-semibold">AI Assistant</span>
              <div className="flex items-center space-x-1 ml-2">
                <span className={`w-2 h-2 ${status.color} rounded-full`}></span>
                <span className="text-xs opacity-90">{status.text}</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {isMaximized ? (
                <button onClick={toggleMaximize} className="p-1 hover:bg-blue-600 rounded transition-colors">
                  <Minimize2 className="w-4 h-4" />
                </button>
              ) : (
                <button onClick={toggleMaximize} className="p-1 hover:bg-blue-600 rounded transition-colors">
                  <Maximize2 className="w-4 h-4" />
                </button>
              )}
              <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-blue-600 rounded transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Start a conversation with the AI assistant</p>
                {isLoading && <p className="text-sm mt-2">Loading AI model...</p>}
              </div>
            )}
            
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'ai' ? 'bg-gray-900 text-white' : 'bg-blue-600 text-white'
                  }`}>
                    {message.type === 'ai' ? (
                      <MessageSquare className="w-4 h-4" />
                    ) : (
                      <div className="w-4 h-4 rounded-full bg-white"></div>
                    )}
                  </div>
                  
                  <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`rounded-2xl px-4 py-2 ${
                      message.type === 'ai' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'bg-blue-600 text-white'
                    }`}>
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                    <span className="text-xs text-gray-500 mt-1">{message.timestamp}</span>
                  </div>
                </div>
              </div>
            ))}
            
            {isWaitingResponse && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 bg-gray-100 rounded-2xl px-4 py-2">
                  <Loader className="w-4 h-4 animate-spin text-gray-600" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 flex-shrink-0">
            <div className="relative">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={modelLoaded ? "Ask me anything..." : "Waiting for AI model..."}
                disabled={!modelLoaded || isWaitingResponse}
                className="w-full pl-4 pr-20 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                <button 
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  disabled={!modelLoaded}
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || !modelLoaded || isWaitingResponse}
                  className="p-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChatbot;