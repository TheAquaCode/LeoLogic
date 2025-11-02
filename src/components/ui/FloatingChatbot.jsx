import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Maximize2, Minimize2, Send, Mic, ChevronRight } from 'lucide-react';
import clankyIcon from '../../assets/Clanky_icon.png';

const FloatingChatbot = ({ onMaximizeChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hi! I'm your AI file organizer. I can help you sort, categorize, and manage your files. What would you like me to help you with today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ online: false, ready: false });
  const [size, setSize] = useState({ width: 400, height: 600 });
  const [isDragging, setIsDragging] = useState(false);
  const [resizeEdge, setResizeEdge] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0, posX: 0, posY: 0 });
  const [position, setPosition] = useState({ x: window.innerWidth - 424, y: window.innerHeight - 688 });
  
  const chatRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:5000/health');
        const data = await response.json();
        setBackendStatus({ online: true, ready: data.model_ready });
      } catch (error) {
        setBackendStatus({ online: false, ready: false });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (onMaximizeChange) {
      onMaximizeChange(isMaximized);
    }
  }, [isMaximized, onMaximizeChange]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isLoading) return;

    const currentMessage = chatInput.trim();

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentMessage })
      });

      const data = await response.json();

      const aiMessage = {
        id: messages.length + 2,
        type: 'ai',
        content: data.response || 'Sorry, I encountered an error.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        type: 'ai',
        content: 'Sorry, I cannot connect to the backend. Make sure the Flask server is running on port 5000.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
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
    ? { top: 0, right: 0, bottom: 0, width: '480px', height: '100vh', borderRadius: 0 }
    : { left: `${position.x}px`, top: `${position.y}px`, width: `${size.width}px`, height: `${size.height}px` };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 flex items-center justify-center z-50"
        >
          <MessageSquare className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          ref={chatRef}
          className={`fixed bg-white shadow-2xl border-l border-gray-200 flex flex-col z-50 ${isMaximized ? '' : 'rounded-lg border'}`}
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

          {/* Header - Draggable - UPDATED WITH LOGO */}
          <div
            onMouseDown={handleMouseDown}
            className={`bg-black text-white px-4 py-3 ${isMaximized ? '' : 'rounded-t-lg'} ${isMaximized ? 'cursor-default' : 'cursor-move'} flex items-center justify-between select-none`}
          >
            <div className="flex items-center space-x-2">
              <img 
                src={clankyIcon} 
                alt="Clanky AI" 
                className="w-6 h-6 rounded-full object-cover"
              />
              <span className="font-semibold">AI Assistant</span>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={toggleMaximize}
                className="p-1.5 hover:bg-gray-800 rounded transition-colors"
              >
                {isMaximized ? (
                  <ChevronRight className="w-5 h-5" />
                ) : (
                  <Maximize2 className="w-4 h-4" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-gray-800 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0 bg-white">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start space-x-3 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden ${
                    message.type === 'ai' ? 'bg-gray-900' : 'bg-blue-600'
                  }`}>
                    {message.type === 'ai' ? (
                      <img 
                        src={clankyIcon} 
                        alt="Clanky AI" 
                        className="w-9 h-9 object-cover"
                      />
                    ) : (
                      <div className="w-5 h-5 rounded-full bg-white"></div>
                    )}
                  </div>
                  
                  <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`rounded-2xl px-4 py-3 ${
                      message.type === 'ai' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'bg-blue-600 text-white'
                    }`}>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <span className="text-xs text-gray-500 mt-1.5">{message.timestamp}</span>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-2 max-w-[80%]">
                  <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                    <img 
                      src={clankyIcon} 
                      alt="Clanky AI" 
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  </div>
                  <div className="flex flex-col items-start">
                    <div className="rounded-2xl px-4 py-3 bg-gray-100">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 flex-shrink-0 bg-white">
            <div className="relative">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className="w-full pl-4 pr-20 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || isLoading || !backendStatus.online}
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