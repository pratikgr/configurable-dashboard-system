# Quick Start Guide

Get the dashboard system running in **under 10 minutes**.

---

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] Azure OpenAI API credentials (endpoint, key, deployment)

If missing any, see [Installation Prerequisites](#installation-prerequisites) below.

---

## 5-Minute Setup

### Step 1: Clone & Navigate

```bash
git clone https://github.com/your-org/dashboard-system.git
cd dashboard-system
```

### Step 2: Backend Setup (2 min)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `.env` with your Azure credentials:**
```bash
# Required - Get these from Azure Portal
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Optional - Defaults work fine
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db
CORS_ORIGINS=["http://localhost:5173"]
DASHBOARD_CONFIG_DIR=../frontend/src/config/dashboards
```

**Start backend:**
```bash
uvicorn app.main:app --reload
```

✅ Backend running at `http://localhost:8000`

### Step 3: Frontend Setup (2 min)

Open **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ Frontend running at `http://localhost:5173`

### Step 4: Verify (1 min)

1. Open browser: `http://localhost:5173`
2. Click purple **floating button** (bottom-right)
3. Chat panel opens
4. Type: **"List all queries"**
5. AI responds with query list

🎉 **Success!** System is working.

---

## First Steps

### Test the Dashboard

1. **View Dashboard:**
   - Main page shows Sales Dashboard
   - See 3 widgets: revenue chart, top products table, metrics

2. **Edit Layout:**
   - Click "Edit Layout" button (top-right)
   - Drag widgets by their headers
   - Resize from corners
   - Click "Done Editing" to save

3. **Refresh Data:**
   - Click refresh icon on any widget
   - Or "Refresh All" button

### Test the AI Chat

**Dashboard Builder Mode:**
```
You: "Add a bar chart of revenue by region"
AI: Creates widget preview → Click "Save Widget"
```

**Data Analyst Mode:**
```
You: "Show me the top 5 products"
AI: Displays data table → Click "Add as Widget" (optional)
```

**Query Info:**
```
You: "What queries are available?"
AI: Lists all 4 queries with descriptions
```

---

## Common Commands

### Backend

```bash
# Start server
uvicorn app.main:app --reload

# Check logs (watch mode)
uvicorn app.main:app --reload --log-level debug

# Run tests
pytest

# Check API docs
# Open: http://localhost:8000/docs
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Fix:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

**Error:** `ValueError: Azure OpenAI endpoint not configured`

**Fix:** Check `.env` file has correct Azure credentials

---

### Frontend won't start

**Error:** `Cannot find module '@vitejs/plugin-vue'`

**Fix:**
```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

**Error:** `Port 5173 already in use`

**Fix:**
```bash
# Kill existing process or use different port
npm run dev -- --port 5174
```

---

### AI not responding

**Check AI status:**
```bash
curl http://localhost:8000/api/ai/status
```

**Expected response:**
```json
{
  "status": "configured",
  "endpoint": "https://...",
  "deployment": "gpt-4.1-mini"
}
```

**If not configured:**
1. Double-check `.env` file
2. Verify Azure credentials in Azure Portal
3. Restart backend server

---

### Can't see FAB (floating button)

**Check:**
1. Frontend running at `http://localhost:5173`
2. No console errors (press F12)
3. ChatPanel component imported in App.vue

**Debug:**
```javascript
// Open browser console (F12), paste:
document.querySelector('.ai-fab')
// Should not be null
```

---

## Installation Prerequisites

### Install Python 3.11

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"

**Mac:**
```bash
brew install python@3.11
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify:**
```bash
python --version  # Should be 3.11+
```

---

### Install Node.js 18

**Windows/Mac:**
1. Download from https://nodejs.org/
2. Run installer

**Linux (Ubuntu):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

**Verify:**
```bash
node --version  # Should be 18+
npm --version   # Should be 9+
```

---

### Install Git

**Windows:**
Download from https://git-scm.com/download/win

**Mac:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

**Verify:**
```bash
git --version
```

---

### Get Azure OpenAI Credentials

1. **Login to Azure Portal:** https://portal.azure.com
2. **Navigate to:** Azure AI Foundry or Azure OpenAI
3. **Get Endpoint:**
   - Go to your resource
   - Copy "Endpoint" URL
   - Format: `https://xxx.cognitiveservices.azure.com/`
4. **Get API Key:**
   - Go to "Keys and Endpoint"
   - Copy "KEY 1"
5. **Get Deployment Name:**
   - Go to "Deployments"
   - Copy your model deployment name (e.g., `gpt-4.1-mini`)

---

## What's Included

### Sample Data

The system includes **500 sample orders** from Nov 2025 - Feb 2026:
- 50 customers (5 regions)
- 20 products (4 categories)
- Order amounts $50-$500
- Status: completed/pending

### Queries (4 included)

1. **sales_overview:** Daily sales with revenue/counts
2. **revenue_by_region:** Revenue by geographic region
3. **top_products:** Best-selling products
4. **simple_test:** Quick test query (no params)

### Widgets (3 pre-configured)

1. Bar chart: Revenue by region
2. Data table: Top 10 products
3. Metric cards: Total revenue, order count, avg order

---

## Next Steps

After basic setup works:

1. **Read Full Documentation:**
   - [Requirements](01-REQUIREMENTS.md) - Features and scope
   - [Architecture](02-ARCHITECTURE.md) - System design
   - [API Docs](03-API-DOCUMENTATION.md) - All endpoints
   - [Developer Guide](05-DEVELOPER-GUIDE.md) - Extend the system

2. **Customize:**
   - Add your own data to SQLite
   - Create new queries in `backend/queries/`
   - Build new dashboards in `frontend/src/config/dashboards/`

3. **Deploy:**
   - Follow [Deployment Guide](04-DEPLOYMENT-GUIDE.md)
   - Options: Single server, Docker, or cloud

---

## Quick Reference Card

### URLs
```
Backend:  http://localhost:8000
Frontend: http://localhost:5173
API Docs: http://localhost:8000/docs
```

### File Locations
```
Backend .env:     backend/.env
Frontend .env:    frontend/.env
Database:         backend/dashboard.db
Queries:          backend/queries/*.yaml
Dashboards:       frontend/src/config/dashboards/*.json
```

### Key Commands
```bash
# Start everything
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev

# Stop everything
# Ctrl+C in both terminals
```

### AI Prompts to Try
```
"List all queries"
"Add a pie chart of sales by category"
"Show me revenue from Electronics"
"What can you help me with?"
"Create a line chart of monthly revenue trend"
```

---

## Getting Help

### Check Logs

**Backend:**
```bash
# Terminal shows logs automatically with --reload
# Or check explicitly:
tail -f backend/logs/app.log
```

**Frontend:**
```bash
# Open browser console (F12)
# Check Console tab for errors
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# List queries
curl http://localhost:8000/api/query/list

# AI status
curl http://localhost:8000/api/ai/status
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port in use | Change port or kill process |
| Module not found | Reinstall dependencies |
| Azure error | Check credentials in .env |
| Widget not loading | Check browser console for errors |
| Database error | Delete dashboard.db and restart |

---

## Video Tutorial

*(Placeholder for video walkthrough)*

**Coming Soon:** 10-minute setup video covering:
1. Installing prerequisites
2. Getting Azure credentials
3. Running the system
4. First AI interactions

---

## Support

- **Documentation:** See all docs in `/docs` folder
- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions in GitHub Discussions
- **Email:** support@example.com

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-22  
**Tested On:** Windows 11, macOS 14, Ubuntu 22.04

---

**⭐ You're all set! Happy dashboard building!**
