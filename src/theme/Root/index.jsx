import React, { useEffect, useState } from 'react';
import Chatbot from '@site/src/components/Chatbot';
import SelectText from '@site/src/components/SelectText';
import PersonalizeModal from '@site/src/components/PersonalizeModal';
import { ContextProvider } from '@site/src/components/Chatbot/context';
import './styles.css';

export default function Root({ children }) {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  useEffect(() => {
    // Load user preferences from localStorage
    const userPrefs = localStorage.getItem('user_preferences');
    if (userPrefs) {
      const prefs = JSON.parse(userPrefs);
      if (prefs.language === 'ur') {
        document.documentElement.setAttribute('lang', 'ur');
      }
      // Apply font size
      if (prefs.fontSize) {
        const sizes = { small: '14px', medium: '16px', large: '18px', xlarge: '20px' };
        document.documentElement.style.setProperty('--ifm-font-size-base', sizes[prefs.fontSize] || '16px');
      }
    }
  }, []);

  // Expose chatbot toggle to window for the navbar button
  useEffect(() => {
    window.toggleChatbot = () => setIsChatbotOpen(prev => !prev);
    window.openPersonalizeModal = () => {
      document.dispatchEvent(new CustomEvent('openPersonalizeModal'));
    };
  }, []);

  return (
    <ContextProvider>
      <SelectText />
      <PersonalizeModal />
      {children}
      <Chatbot isOpen={isChatbotOpen} onClose={() => setIsChatbotOpen(false)} />
    </ContextProvider>
  );
}
