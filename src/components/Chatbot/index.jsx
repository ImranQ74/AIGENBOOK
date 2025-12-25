import React, { useState, useEffect, useRef, useCallback } from 'react';
import clsx from 'clsx';
import MDXComponents from '@theme-original/MDXComponents';
import './styles.css';

const STORAGE_KEY = 'aigenbook_chat_history';

// Get user ID from localStorage or generate one
const getUserId = () => {
  let userId = localStorage.getItem('user_id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('user_id', userId);
  }
  return userId;
};

// Copy button component
const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <button
      className="chatbot-copy-btn"
      onClick={handleCopy}
      title={copied ? 'Copied!' : 'Copy to clipboard'}
    >
      {copied ? (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
        </svg>
      )}
    </button>
  );
};

// Source link component
const SourceLink = ({ source }) => {
  // Convert chapter filename to URL path
  const getSourceUrl = (title) => {
    // Extract chapter number and name
    const match = title.match(/chapter-(\d+)/i);
    if (match) {
      const chapterNum = match[1];
      // Map chapter numbers to paths
      const chapterPaths = {
        '01': '/docs/chapter-01-physical-ai',
        '02': '/docs/chapter-02-humanoid-robotics',
        '03': '/docs/chapter-03-ros2-fundamentals',
        '04': '/docs/chapter-04-digital-twin',
        '05': '/docs/chapter-05-vla-systems',
        '06': '/docs/chapter-06-capstone',
      };
      return chapterPaths[chapterNum] || `/docs/${title.replace('.mdx', '')}`;
    }
    return `/docs/${title.replace('.mdx', '')}`;
  };

  return (
    <a
      href={getSourceUrl(source.title)}
      className="chatbot-source-link"
      target="_blank"
      rel="noopener noreferrer"
      title={source.title}
    >
      {source.title.replace('.mdx', '').replace(/-/g, ' ').replace('chapter ', 'Ch. ')}
    </a>
  );
};

// Loading spinner component
const LoadingSpinner = () => (
  <div className="chatbot-spinner">
    <div className="chatbot-spinner-dot" />
    <div className="chatbot-spinner-dot" />
    <div className="chatbot-spinner-dot" />
  </div>
);

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      type: 'bot',
      text: 'Hi! I\'m your AI learning assistant. Select any text from the textbook and ask me questions, or type below.',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState(null);
  const messagesEndRef = useRef(null);

  // Listen for selectText events from SelectText component
  useEffect(() => {
    const handleSelection = (e) => {
      const text = e.detail;
      if (text) {
        setSelectedText(text);
        setIsOpen(true);
        // Check for pending question from localStorage
        const pending = localStorage.getItem('pending_question');
        if (pending) {
          setInput(pending);
          localStorage.removeItem('pending_question');
        }
      }
    };

    window.addEventListener('selectText', handleSelection);
    return () => window.removeEventListener('selectText', handleSelection);
  }, []);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY);
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        // Keep only last 50 messages
        const recentMessages = parsed.slice(-50);
        if (recentMessages.length > 0) {
          setMessages(recentMessages);
        }
      } catch (e) {
        console.error('Failed to load chat history:', e);
      }
    }
  }, []);

  // Save chat history to localStorage when messages change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      text: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const apiEndpoint = window.docusaurus?.plugin_rag_config?.apiEndpoint ||
                          document.querySelector('[data-rag-endpoint]')?.dataset?.ragEndpoint ||
                          'http://localhost:8000';

      const response = await fetch(`${apiEndpoint}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.text,
          user_id: getUserId(),
          selected_text: selectedText,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: data.answer,
        sources: data.sources || [],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: 'I apologize, but I encountered an error. Please try again later.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText(null);
    }
  }, [input, isLoading, selectedText, selection]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Clear chat history?')) {
      setMessages([
        {
          id: 'welcome',
          type: 'bot',
          text: 'Hi! I\'m your AI learning assistant. Select any text from the textbook and ask me questions, or type below.',
        },
      ]);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  return (
    <>
      <button className="chatbot-fab" onClick={() => setIsOpen(!isOpen)} aria-label="Open chat">
        {isOpen ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        )}
      </button>

      <div className={clsx('chatbot-panel', { open: isOpen })}>
        <div className="chatbot-header">
          <h3>AI Learning Assistant</h3>
          <div className="chatbot-header-actions">
            <button
              className="chatbot-clear-btn"
              onClick={handleClearHistory}
              title="Clear chat history"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
            </button>
            <button className="chatbot-close" onClick={() => setIsOpen(false)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={clsx('chatbot-message', msg.type)}>
              {msg.type === 'bot' && <CopyButton text={msg.text} />}
              <div className="chatbot-message-content">
                {msg.text}
              </div>
              {msg.type === 'bot' && msg.sources && msg.sources.length > 0 && (
                <div className="chatbot-message-sources">
                  <span className="chatbot-sources-label">Sources:</span>
                  <div className="chatbot-sources-list">
                    {msg.sources.map((source, idx) => (
                      <SourceLink key={idx} source={source} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="chatbot-message bot">
              <LoadingSpinner />
              <span>Thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading || !input.trim()}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </div>
    </>
  );
};

export default Chatbot;
