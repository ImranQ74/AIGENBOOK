# AIGENBOOK - Physical AI & Humanoid Robotics Textbook

A modern, AI-native textbook for learning Physical AI and Humanoid Robotics, built with Docusaurus and featuring an integrated RAG chatbot.

**Deployed at:** https://imranq74s-projects.vercel.app

## Features

- **6 Comprehensive Chapters**: From Physical AI basics to capstone projects
- **RAG-Powered Chatbot**: Ask questions about any chapter content
- **Select-to-Ask**: Highlight text and get instant AI explanations
- **Urdu Language Support**: Switch to Urdu for bilingual learning
- **Personalization**: Customize font size, theme, and learning goals
- **Free-Tier Architecture**: Qdrant + local embeddings + lightweight models

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- npm or yarn

### Frontend (Textbook)

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
```

### Backend (RAG Chatbot)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py

# The API will be available at http://localhost:8000
```

## Project Structure

```
AIGENBOOK/
├── docs/                    # Textbook content
│   ├── index.mdx           # Homepage
│   ├── chapter-01-physical-ai.mdx
│   ├── chapter-02-humanoid-robotics.mdx
│   ├── chapter-03-ros2-fundamentals.mdx
│   ├── chapter-04-digital-twin.mdx
│   ├── chapter-05-vla-systems.mdx
│   └── chapter-06-capstone.mdx
├── backend/                 # RAG chatbot backend
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── document_processor.py  # Text chunking
│   ├── vector_store.py     # Qdrant interface
│   ├── rag_engine.py       # RAG generation
│   └── user_manager.py     # User preferences
├── src/
│   ├── components/
│   │   ├── Chatbot/        # RAG chatbot UI
│   │   ├── SelectText/     # Text selection popup
│   │   ├── PersonalizeModal/  # User preferences
│   │   └── ChapterCard/    # Chapter preview cards
│   └── theme/Root/         # Theme customization
├── docusaurus.config.js    # Docusaurus configuration
└── package.json
```

## Configuration

### Environment Variables (Backend)

Create a `.env` file in the `backend` directory:

```env
# Qdrant (optional - uses in-memory if not set)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key

# Neon PostgreSQL (optional)
NEON_DATABASE_URL=postgresql://user:pass@host/db

# LLM Configuration
LLM_PROVIDER=transformers
LLM_MODEL=microsoft/Phi-3-mini-4k-instruct

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Docusaurus Configuration

Update `docusaurus.config.js` with your settings:

```js
const config = {
  url: 'https://yourusername.github.io',
  baseUrl: '/AIGENBOOK/',
  // ...
};
```

## Deployment

### GitHub Pages

1. Fork this repository
2. Enable GitHub Pages in repository settings
3. Push to main branch - deployment happens automatically

### Vercel/Netlify

The frontend can be deployed to any static hosting:

```bash
npm run build
# Deploy the build/ folder
```

### Docker

```dockerfile
# Backend
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "main.py"]
```

## Chapter Overview

1. **Introduction to Physical AI** - Understanding embodied AI systems
2. **Basics of Humanoid Robotics** - Robot anatomy, actuation, and locomotion
3. **ROS 2 Fundamentals** - Robot Operating System 2 basics
4. **Digital Twin Simulation** - Gazebo and NVIDIA Isaac Sim
5. **Vision-Language-Action Systems** - VLA models and multimodal AI
6. **Capstone Project** - Complete AI-robot pipeline

## Tech Stack

- **Frontend**: Docusaurus 3, React 18
- **Styling**: CSS Modules, CSS Variables
- **Backend**: FastAPI, Python 3.10
- **Vector Database**: Qdrant (in-memory or cloud)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: Phi-3-mini (CPU-friendly) or OpenAI-compatible API
- **Database**: Neon PostgreSQL (optional)

## License

MIT License - feel free to use and modify.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- Open an issue for bugs
- Use the chatbot for textbook questions
- Check chapter quizzes for self-assessment
