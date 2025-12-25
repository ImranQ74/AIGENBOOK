import React, { createContext, useContext, useState, useCallback } from 'react';

const ChatbotContext = createContext(null);

export const useChatbot = () => {
  const context = useContext(ChatbotContext);
  if (!context) {
    throw new Error('useChatbot must be used within a ChatbotProvider');
  }
  return context;
};

export const ContextProvider = ({ children }) => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      type: 'bot',
      text: "Hi! I'm your AI learning assistant. Select any text from the textbook and ask me questions, or type below.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (question, selectedText = null) => {
    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      text: selectedText ? `${selectedText}\n\nQuestion: ${question}` : question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const apiEndpoint = window.docusaurus?.plugin_rag_config?.apiEndpoint ||
                          'http://localhost:8000';

      const response = await fetch(`${apiEndpoint}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.text,
          user_id: localStorage.getItem('user_id') || 'anonymous',
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
      return botMessage;
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: 'I apologize, but I encountered an error. Please try again later.',
      };
      setMessages((prev) => [...prev, errorMessage]);
      return errorMessage;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        type: 'bot',
        text: "Hi! I'm your AI learning assistant. Select any text from the textbook and ask me questions, or type below.",
      },
    ]);
  }, []);

  return (
    <ChatbotContext.Provider value={{ messages, sendMessage, isLoading, clearMessages }}>
      {children}
    </ChatbotContext.Provider>
  );
};
