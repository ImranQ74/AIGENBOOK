# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIGENBOOK is a Docusaurus-based textbook for Physical AI and Humanoid Robotics with an integrated RAG chatbot. The project consists of:

- **Frontend**: Docusaurus 3 + React 18 documentation site with 6 textbook chapters
- **Backend**: FastAPI Python service providing RAG (Retrieval-Augmented Generation) capabilities
- **Vector Database**: Qdrant (in-memory for dev, cloud for production) storing textbook content chunks
- **ML Stack**: Sentence Transformers for embeddings, OpenAI-compatible API for fast responses

## Common Commands

### Frontend (Docusaurus)
```bash
npm install              # Install dependencies
npm run dev              # Start development server at http://localhost:3000
npm run build            # Build for production (output: build/)
npm run deploy           # Deploy to GitHub Pages
```

### Backend (FastAPI)
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Create virtual env
pip install -r requirements.txt                  # Install Python deps
python main.py                                   # Start API at http://localhost:8000
```

### Testing
```bash
# Backend tests
cd backend
pip install pytest pytest-asyncio httpx black isort flake8
pytest tests/ -v                    # Run all tests
pytest tests/ -v --tb=short         # With shorter tracebacks
pytest tests/test_rag_engine.py -v  # Run specific test file

# Linting
black --check .                     # Check code formatting
isort --check .                     # Check import sorting
flake8 .                            # Check style issues
```

### Running Both Simultaneously
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2: Frontend
npm run dev
```

## Architecture

### Data Flow
1. `docs/*.mdx` files are processed by `DocumentProcessor` -> chunked -> stored in Qdrant
2. User query -> embedded via `SentenceTransformer` -> similarity search in Qdrant
3. Retrieved chunks + query -> sent to LLM (OpenAI-compatible API like Groq) -> response
4. Response returned to React chatbot component with sources

### Key Backend Modules (`backend/`)
- `main.py`: FastAPI app, startup event indexes all docs from `/docs`, `/api/chat` endpoint, rate limiting
- `rag_engine.py`: RAG pipeline - search, rerank (optional), prompt building, OpenAI/transformers LLM support
- `vector_store.py`: Qdrant wrapper for document storage and similarity search
- `document_processor.py`: Text chunking with configurable size/overlap
- `user_manager.py`: User preferences and conversation history (Neon PostgreSQL or in-memory)
- `config.py`: Settings via environment variables (pydantic-settings)

### Frontend Components (`src/components/`)
- `Chatbot/`: Main chatbot with localStorage persistence, copy-to-clipboard, clickable sources
- `SelectText/`: Text selection popup that triggers chatbot with selected context
- `PersonalizeModal/`: User preferences (language, theme, font size)
- `ChapterCard/`: Homepage chapter preview cards

## Configuration

### Required Environment Variables (`backend/.env`)
```env
# LLM - Use OpenAI-compatible API (Groq recommended for free-tier speed)
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_...

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Vector DB (leave empty for in-memory)
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=aigenbook_chunks

# Database (optional)
NEON_DATABASE_URL=
```

### Docusaurus Config (`docusaurus.config.js`)
- `ragConfig.apiEndpoint`: Backend URL (default: `http://localhost:8000`)
- `i18n.locales`: English (`en`) and Urdu (`ur`)

## Chapter Structure (`docs/`)
1. **Introduction to Physical AI** - Embodied AI, sensorimotor loop
2. **Basics of Humanoid Robotics** - Robot anatomy, actuation, locomotion
3. **ROS 2 Fundamentals** - Nodes, topics, services, actions
4. **Digital Twin Simulation** - Gazebo, NVIDIA Isaac Sim
5. **Vision-Language-Action Systems** - VLA models, multimodal AI
6. **Capstone** - Complete AI-robot pipeline

## Development Notes

- **Rate Limiting**: 30 requests/minute on `/api/chat` endpoint (slowapi)
- **Message Persistence**: Chat history saved to localStorage (max 50 messages)
- **Select-to-Ask**: Highlight text anywhere -> click "Ask AI" -> opens chatbot with context
- **Sources**: Clickable links to relevant chapter sections
- **CI/CD**: `.github/workflows/ci.yml` for linting/testing, `deploy.yml` for GitHub Pages
