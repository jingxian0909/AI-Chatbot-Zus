import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Coffee, MapPin, Calculator, RotateCcw } from 'lucide-react';

const ZusChatbot = () => {
 const [messages, setMessages] = useState(() => {
  const saved = localStorage.getItem('zus-chat-history');
  return saved
    ? JSON.parse(saved)
    : [{
        id: 1,
        role: 'assistant',
        content: 'Hi! I\'m the Zus AI assistant. I can help you with our products, outlet locations, and even calculations. Try typing "/" to see quick actions!',
        timestamp: new Date().toISOString(),
        planner: ['Greet', 'Finish']
      }];
  });
  const [input, setInput] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const commands = [
    { cmd: '/calc', icon: Calculator, desc: 'Perform calculations' },
    { cmd: '/products', icon: Coffee, desc: 'View Zus products' },
    { cmd: '/outlets', icon: MapPin, desc: 'Find outlets near you' },
    { cmd: '/reset', icon: RotateCcw, desc: 'Clear conversation' }
  ];

   useEffect(() => {
     localStorage.setItem('zus-chat-history', JSON.stringify(messages));
   }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleCommandClick = (cmd) => {
    setInput(cmd + ' ');
    setShowCommands(false);
    textareaRef.current?.focus();
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setShowCommands(false);

    // Handle reset command
    if (input.toLowerCase().trim().startsWith('/reset')) {
      setTimeout(() => {
        const initialMessage = {
          id: Date.now(),
          role: 'assistant',
          content: 'Hi! I\'m the Zus AI assistant. I can help you with our products, outlet locations, and even calculations. Try typing "/" to see quick actions!',
          timestamp: new Date().toISOString(),
          planner: ['Greet', 'Finish']
        };
        setMessages([initialMessage]);
        localStorage.setItem('zus-chat-history', JSON.stringify([initialMessage])); // clear localStorage
        setIsTyping(false);
      }, 500);

      setIsTyping(true);
        try {
        const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
        });
        /*
        if (!res.ok) throw new Error("Failed to get AI answer");
        const data = await res.json();
        //console.log("res: ", data.message)

        const answerText = (data && (data.message || data.text)) || "(no answer)";
    
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: answerText,
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);*/
      } 
      catch (err) {
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${err.message || "Failed to get answer"}`,
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      }
      return;
    } else{
        setIsTyping(true);
        try {
        const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
        });
        
        if (!res.ok) throw new Error("Failed to get AI answer");
        const data = await res.json();
        //console.log("res: ", data.message)

        const answerText = (data && (data.message || data.text)) || "(no answer)";
    
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: answerText,
          timestamp: new Date().toISOString(),
          planner: data.debug.planner_action
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      } 
      catch (err) {
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${err.message || "Failed to get answer"}`,
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      }
    } 
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
    
    // Show commands when typing "/"
    if (value === '/' || (value.startsWith('/') && !value.includes(' '))) {
      setShowCommands(true);
    } else {
      setShowCommands(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const filteredCommands = commands.filter(c => 
    input.startsWith('/') && c.cmd.toLowerCase().includes(input.toLowerCase())
  );

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 backdrop-blur-sm p-2 rounded-full">
            <Coffee className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Zus Coffee Assistant</h1>
            <p className="text-xs text-blue-100">Always here to help ☕</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              msg.role === 'user' 
                ? 'bg-gradient-to-br from-slate-500 to-slate-600' 
                : 'bg-gradient-to-br from-blue-500 to-cyan-600'
            }`}>
              {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
            </div>

            {/* Message bubble */}
            <div className={`flex flex-col max-w-[70%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`rounded-2xl px-4 py-3 shadow-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-slate-500 to-slate-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-100'
              }`}>
                <div className="text-sm whitespace-pre-wrap break-words" 
                     dangerouslySetInnerHTML={{__html: String(msg.content).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}} />
              </div>
              {/* Planner panel - only for assistant messages */}
              {msg.role === 'assistant' && msg.planner && (
                <div className="mt-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-xs">
                  <span className="font-semibold text-blue-700">Planner:</span>
                  <span className="text-blue-600 ml-2">
                    [{Array.isArray(msg.planner) ? msg.planner.join(' | ') : msg.planner}]
                  </span>
                </div>
              )}
              <span className="text-xs text-gray-500 mt-1 px-2">
                {formatTime(msg.timestamp)}
              </span>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-100">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Command autocomplete */}
      {showCommands && filteredCommands.length > 0 && (
        <div className="mx-4 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
          {filteredCommands.map((cmd) => {
            const Icon = cmd.icon;
            return (
              <button
                key={cmd.cmd}
                onClick={() => handleCommandClick(cmd.cmd)}
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-blue-50 transition-colors text-left border-b last:border-b-0"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">{cmd.cmd}</div>
                  <div className="text-xs text-gray-500">{cmd.desc}</div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Input composer */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask about products, outlets, or type / for commands..."
              rows={1}
              className="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-blue-500 resize-none text-sm"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <div className="absolute right-3 bottom-3 text-xs text-gray-400">
              {input.length > 0 && <span>Shift+Enter for new line</span>}
            </div>
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-3 rounded-2xl hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 disabled:transform-none"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <div className="text-center mt-2 text-xs text-gray-400">
          Type <span className="font-mono bg-gray-100 px-1 rounded">/</span> for quick actions
        </div>
      </div>
    </div>
  );
};

export default ZusChatbot;