import React from 'react';
import clsx from 'clsx';
import './styles.css';

const ChapterCard = ({ number, title, description, link }) => {
  return (
    <a href={link} className="chapter-card">
      <div className="chapter-card-header">
        <span className="chapter-number">Chapter {number}</span>
      </div>
      <h3 className="chapter-card-title">{title}</h3>
      <p className="chapter-card-description">{description}</p>
      <span className="chapter-card-link">
        Read Chapter
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </span>
    </a>
  );
};

export default ChapterCard;
