import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import './styles.css';

const PersonalizeModal = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [preferences, setPreferences] = useState({
    name: '',
    language: 'en',
    fontSize: 'medium',
    theme: 'system',
    goals: [],
  });

  useEffect(() => {
    // Load saved preferences
    const saved = localStorage.getItem('user_preferences');
    if (saved) {
      setPreferences(JSON.parse(saved));
    }

    // Listen for open modal event
    const handleOpenModal = () => setIsVisible(true);
    document.addEventListener('openPersonalizeModal', handleOpenModal);

    return () => {
      document.removeEventListener('openPersonalizeModal', handleOpenModal);
    };
  }, []);

  const handleClose = () => {
    setIsVisible(false);
  };

  const handleSave = () => {
    localStorage.setItem('user_preferences', JSON.stringify(preferences));

    // Apply language change
    if (preferences.language === 'ur') {
      document.documentElement.setAttribute('lang', 'ur');
    } else {
      document.documentElement.setAttribute('lang', 'en');
    }

    // Apply font size
    document.documentElement.style.setProperty('--ifm-font-size-base', getFontSize(preferences.fontSize));

    setIsVisible(false);
  };

  const getFontSize = (size) => {
    const sizes = {
      small: '14px',
      medium: '16px',
      large: '18px',
      xlarge: '20px',
    };
    return sizes[size] || '16px';
  };

  const handleChange = (field, value) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className={clsx('personalize-modal', { visible: isVisible })} onClick={handleClose}>
      <div className="personalize-modal-content" onClick={e => e.stopPropagation()}>
        <h2>Personalize Your Learning</h2>

        <div className="form-group">
          <label htmlFor="name">Your Name</label>
          <input
            type="text"
            id="name"
            value={preferences.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="Enter your name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="language">Language</label>
          <select
            id="language"
            value={preferences.language}
            onChange={(e) => handleChange('language', e.target.value)}
          >
            <option value="en">English</option>
            <option value="ur">Urdu (اردو)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="fontSize">Font Size</label>
          <select
            id="fontSize"
            value={preferences.fontSize}
            onChange={(e) => handleChange('fontSize', e.target.value)}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
            <option value="xlarge">Extra Large</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="theme">Theme</label>
          <select
            id="theme"
            value={preferences.theme}
            onChange={(e) => handleChange('theme', e.target.value)}
          >
            <option value="system">System Default</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="form-group">
          <label>Learning Goals (optional)</label>
          <div className="checkbox-group">
            {[
              { value: 'basics', label: 'Learn the basics' },
              { value: 'projects', label: 'Build projects' },
              { value: 'career', label: 'Career preparation' },
              { value: 'research', label: 'Research' },
            ].map(goal => (
              <label key={goal.value} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={preferences.goals.includes(goal.value)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleChange('goals', [...preferences.goals, goal.value]);
                    } else {
                      handleChange('goals', preferences.goals.filter(g => g !== goal.value));
                    }
                  }}
                />
                {goal.label}
              </label>
            ))}
          </div>
        </div>

        <div className="modal-actions">
          <button className="cancel" onClick={handleClose}>Cancel</button>
          <button className="save" onClick={handleSave}>Save Preferences</button>
        </div>
      </div>
    </div>
  );
};

export default PersonalizeModal;
