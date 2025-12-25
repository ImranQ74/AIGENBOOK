import React, { useState, useEffect, useCallback } from 'react';
import clsx from 'clsx';
import './styles.css';

const SelectText = () => {
  const [selection, setSelection] = useState(null);
  const [popupPosition, setPopupPosition] = useState({ top: 0, left: 0 });
  const [showPopup, setShowPopup] = useState(false);
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const handleTextSelection = useCallback(() => {
    const selectedText = window.getSelection();
    const text = selectedText?.toString().trim();

    if (!text || text.length < 3) {
      setSelection(null);
      setShowPopup(false);
      return;
    }

    const range = selectedText?.getRangeAt(0);
    const rect = range?.getBoundingClientRect();

    if (rect) {
      setPopupPosition({
        top: rect.top + window.scrollY - 45,
        left: rect.left + window.scrollX + (rect.width / 2),
      });
      setSelection(text);
      setShowPopup(true);
    }
  }, []);

  const handleAskAI = () => {
    setShowPopup(false);
    setChatbotOpen(true);
    // The chatbot component will pick up the selection from a data attribute or localStorage
    localStorage.setItem('pending_question', `Can you explain this concept: "${selection}"`);
    window.dispatchEvent(new CustomEvent('selectText', { detail: selection }));
  };

  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('mousedown', (e) => {
      if (!e.target.closest('.selection-popup')) {
        setShowPopup(false);
      }
    });

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('mousedown', handleTextSelection);
    };
  }, [handleTextSelection]);

  return (
    <>
      <div
        className={clsx('selection-popup', { visible: showPopup })}
        style={{
          position: 'absolute',
          top: popupPosition.top,
          left: popupPosition.left,
          transform: 'translateX(-50%)',
        }}
      >
        <button onClick={handleAskAI}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px', verticalAlign: 'middle' }}>
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
          Ask AI
        </button>
      </div>
    </>
  );
};

export default SelectText;
