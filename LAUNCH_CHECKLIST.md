# AIGENBOOK Launch Checklist

## Pre-Launch (Day Before)

### Repository Setup
- [ ] Fork repository to your GitHub account
- [ ] Clone locally: `git clone https://github.com/YOUR_USERNAME/AIGENBOOK.git`
- [ ] Create `.env` file in `backend/` directory
- [ ] Test `.env` configuration locally

### API Keys
- [ ] Get Groq API key (free at https://groq.com)
  - Sign up for Groq Cloud
  - Create API key
  - Add to `.env`: `LLM_API_KEY=gsk_...`
- [ ] (Optional) Get Qdrant cloud URL for persistence
  - Sign up at https://cloud.qdrant.io
  - Create collection `aigenbook_chunks`
  - Add URL and API key to `.env`
- [ ] (Optional) Get Neon PostgreSQL URL
  - Sign up at https://neon.tech
  - Create database
  - Add `NEON_DATABASE_URL` to `.env`

### Local Testing
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd ..
npm install
npm run dev
```

- [ ] Open http://localhost:3000
- [ ] Click AI Chatbot button
- [ ] Ask: "What is Physical AI?"
- [ ] Verify response includes sources
- [ ] Test Select-to-Ask (highlight text, click "Ask AI")
- [ ] Check browser console for errors

---

## Launch Day

### 1. GitHub Pages Deployment

#### Update Configuration
Edit `docusaurus.config.js`:
```javascript
const config = {
  url: 'https://YOUR_USERNAME.github.io',
  baseUrl: '/YOUR_REPO_NAME/',
  // ...
};
```

#### Push to Deploy
```bash
git add docusaurus.config.js
git commit -m "Configure for production deployment"
git push origin main
```

#### Verify Frontend Deployment
- [ ] Go to https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/
- [ ] Homepage loads correctly
- [ ] All 6 chapters accessible
- [ ] AI Chatbot button visible
- [ ] Chatbot opens and responds

### 2. Backend Deployment

#### Option A: Railway (Recommended)
1. Go to https://railway.app
2. "New Project" > "Deploy from GitHub repo"
3. Select this repository
4. Set root directory to `backend`
5. Add environment variables in Railway dashboard:
   ```
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-3.5-turbo
   LLM_API_BASE=https://api.groq.com/openai/v1
   LLM_API_KEY=gsk_...
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```
6. Deploy

#### Option B: Render
1. Go to https://render.com
2. "New Web Service"
3. Connect GitHub repo
4. Build Command: `cd backend && pip install -r requirements.txt`
5. Start Command: `cd backend && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
6. Add environment variables
7. Deploy

#### Verify Backend
- [ ] Health check: `https://YOUR_BACKEND.railway.app/`
- [ ] Response: `{"status":"healthy",...}`
- [ ] Health detail: `https://YOUR_BACKEND.railway.app/health`
- [ ] Readiness: `https://YOUR_BACKEND.railway.app/ready`

### 3. Connect Frontend to Backend

Edit `docusaurus.config.js`:
```javascript
themeConfig: {
  ragConfig: {
    apiEndpoint: 'https://YOUR_BACKEND.railway.app',
  },
  // ...
}
```

```bash
git add docusaurus.config.js
git commit -m "Connect to production backend"
git push origin main
```

---

## Post-Launch Verification

### Frontend Checks
- [ ] Homepage displays chapter cards
- [ ] Navigation works (Textbook, AI Chatbot)
- [ ] Chapter pages load correctly
- [ ] Dark/light theme toggle works

### Chatbot Checks
- [ ] Chatbot opens when clicked
- [ ] Welcome message appears
- [ ] Ask a question about Physical AI
- [ ] Response generated (should be fast with Groq)
- [ ] Sources appear below response
- [ ] Click source links navigate to chapters
- [ ] Copy button works
- [ ] Select-to-Ask works from any chapter

### Performance Checks
- [ ] Page load < 3 seconds
- [ ] Chatbot response < 5 seconds
- [ ] No console errors

---

## Rollback Plan

### If Frontend Issues
```bash
git revert HEAD~1
git push origin main
```

### If Backend Issues
1. Railway: Click "Rollback" on deployments list
2. Or revert to previous commit:
```bash
cd backend
git revert HEAD~1
git push origin main
```

---

## Monitoring

### Key Metrics
- **Uptime**: Check deployment dashboard
- **Response Time**: < 5 seconds expected
- **Error Rate**: < 1% target
- **Chat Volume**: Monitor for abuse

### Alerts
- Set up notifications in Railway/Render dashboard
- Monitor GitHub Actions for deploy failures

---

## Post-Launch Tasks

### Day 1
- [ ] Test all features manually
- [ ] Share with first users
- [ ] Monitor error logs

### Week 1
- [ ] Collect user feedback
- [ ] Fix any reported issues
- [ ] Optimize performance if needed

### Month 1
- [ ] Review analytics
- [ ] Plan improvements
- [ ] Consider adding Urdu content translations

---

## Emergency Contacts

| Issue | Action |
|-------|--------|
| Site down | Check Railway/Render status page |
| Chatbot errors | Check backend logs in dashboard |
| Deployment failed | Check GitHub Actions tab |
| API rate limits | Reduce rate or upgrade plan |

---

## Quick Commands Reference

```bash
# Update frontend
git add .
git commit -m "Update"
git push

# View backend logs (Railway)
# Open Railway dashboard > Deployments > View Logs

# Restart backend (Railway)
# Open Railway dashboard > Deployments > Restart
```
