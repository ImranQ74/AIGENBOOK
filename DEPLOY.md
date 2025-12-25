# AIGENBOOK Deployment Guide

## Overview

This guide covers deploying AIGENBOOK to production:
- **Frontend**: Docusaurus on GitHub Pages
- **Backend**: FastAPI on Railway or Render

---

## Frontend Deployment (GitHub Pages)

### Automatic Deployment (Recommended)

1. **Fork this repository** to your GitHub account

2. **Enable GitHub Pages**:
   - Go to Settings > Pages
   - Source: "GitHub Actions"
   - Click Save

3. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Deploy AIGENBOOK"
   git push origin main
   ```

4. **Deployment happens automatically** via `.github/workflows/deploy.yml`

### Manual Deployment

```bash
npm run build
npm run deploy
```

### Frontend Configuration

Update `docusaurus.config.js`:
```javascript
const config = {
  url: 'https://yourusername.github.io',
  baseUrl: '/AIGENBOOK/',
  // ...
};
```

---

## Backend Deployment (Railway/Render)

### Option 1: Railway Deployment (Recommended)

1. **Create Railway account** at https://railway.app

2. **Deploy from GitHub**:
   - New Project > Deploy from GitHub repo
   - Select this repository
   - Select "Backend" as the root directory

3. **Set Environment Variables** in Railway dashboard:
   ```
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-3.5-turbo
   LLM_API_BASE=https://api.groq.com/openai/v1
   LLM_API_KEY=gsk_...
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   QDRANT_URL=https://xxx-xxx.aws.cloud.qdrant.io
   QDRANT_API_KEY=...
   ```

4. **Add Persistent Disk** (optional, for Qdrant data)

5. **Deploy** - Railway will automatically detect FastAPI

### Option 2: Render Deployment

1. **Create Render account** at https://render.com

2. **Create Web Service**:
   - New > Web Service
   - Connect GitHub repo
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`

3. **Set Environment Variables** in Render dashboard

4. **Deploy**

---

## Environment Variables

### Required for Backend

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider | `openai` |
| `LLM_MODEL` | Model name | `gpt-3.5-turbo` |
| `LLM_API_BASE` | API endpoint | `https://api.groq.com/openai/v1` |
| `LLM_API_KEY` | API key | `gsk_...` |
| `EMBEDDING_MODEL` | Embedding model | `all-MiniLM-L6-v2` |
| `QDRANT_URL` | Qdrant cloud URL | (optional) |
| `QDRANT_API_KEY` | Qdrant API key | (optional) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `NEON_DATABASE_URL` | PostgreSQL URL | (in-memory) |
| `DEBUG` | Debug mode | `false` |

---

## Health Checks

The backend exposes health check endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service health check |
| `GET /api/stats` | Vector store statistics |

### Example Health Check Response

```json
{
  "status": "healthy",
  "service": "AIGENBOOK RAG Chatbot",
  "version": "1.0.0"
}
```

---

## Production Checklist

### Before Launch

- [ ] Fork repository
- [ ] Configure GitHub Pages
- [ ] Set LLM_API_KEY (Groq recommended)
- [ ] Configure Qdrant (optional, for persistence)
- [ ] Update docusaurus.config.js with your URL
- [ ] Test locally with `npm run dev` and `python main.py`
- [ ] Verify chatbot responses
- [ ] Test Select-to-Ask feature

### After Deployment

- [ ] Verify GitHub Pages URL loads
- [ ] Verify backend health endpoint
- [ ] Test chatbot functionality
- [ ] Check browser console for errors
- [ ] Verify sources link to correct chapters

---

## Architecture Diagram

```
                    ┌─────────────────┐
                    │   GitHub Pages  │
                    │   (Frontend)    │
                    └────────┬────────┘
                             │
                    User loads textbook
                             │
                             ▼
┌─────────────────┐   ┌───────────────┐
│   User Browser  │──▶│  Docusaurus   │
│                 │   │  React App    │
└─────────────────┘   └───────┬───────┘
                              │
                    API calls to backend
                              │
                              ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    │   (Railway)   │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌─────────┐  ┌───────────┐  ┌─────────┐
        │ Qdrant  │  │  OpenAI   │  │ Neon    │
        │ Vector  │  │   API     │  │Postgres │
        └─────────┘  └───────────┘  └─────────┘
```

---

## Troubleshooting

### Frontend Issues

| Problem | Solution |
|---------|----------|
| 404 on pages | Check `baseUrl` in docusaurus.config.js |
| Styles broken | Run `npm run clear` then rebuild |
| Images not loading | Check `static/img` folder |

### Backend Issues

| Problem | Solution |
|---------|----------|
| Slow responses | Switch to Groq API (free-tier fast) |
| No sources | Check Qdrant is configured |
| Rate limited | Reduce request frequency |
| CORS errors | Update `allow_origins` in main.py |

### Get Help

- Open a GitHub issue
- Check chapter quizzes for self-assessment
- Use the chatbot for textbook questions
