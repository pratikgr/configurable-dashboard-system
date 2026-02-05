# Running Online - Platform-Specific Guides

## 🌐 Best Options for Running This Project Online

### Option 1: GitHub + Gitpod (Recommended - Easiest)

**Best for:** Quick demo, development, testing
**Cost:** Free tier available
**Setup time:** 2 minutes

#### Steps:

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/dashboard-system.git
git push -u origin main
```

2. **Open in Gitpod:**
   - Go to: `https://gitpod.io/#https://github.com/YOUR_USERNAME/dashboard-system`
   - Or install Gitpod browser extension and click "Gitpod" button on your repo

3. **Gitpod will automatically:**
   - Setup the environment
   - Install dependencies
   - Start Docker containers

4. **Access your app:**
   - Gitpod will show you the URLs
   - Typically: `https://5173-yourworkspace.gitpod.io`

**Create `.gitpod.yml` in root:**
```yaml
tasks:
  - name: Start Application
    init: |
      # Copy environment files
      cp backend/.env.example backend/.env
      cp frontend/.env.example frontend/.env
    command: |
      docker-compose up

ports:
  - port: 5173
    onOpen: open-preview
    visibility: public
  - port: 8000
    onOpen: ignore
    visibility: public
  - port: 5432
    onOpen: ignore
    visibility: private

vscode:
  extensions:
    - dbaeumer.vscode-eslint
    - Vue.volar
    - ms-python.python
```

---

### Option 2: Replit (Simplest - No Docker)

**Best for:** Quick prototyping, simple demos
**Cost:** Free tier available
**Setup time:** 5 minutes
**Note:** Use SQLite instead of PostgreSQL

#### Steps:

1. **Go to [replit.com](https://replit.com)**
2. **Create new Repl > Import from GitHub**
3. **Modify for Replit:**

**Update `backend/app/core/config.py`:**
```python
DATABASE_URL: str = "sqlite:///./dashboard.db"  # Use SQLite
```

**Create `.replit` file:**
```toml
run = "bash start-replit.sh"
language = "bash"

[nix]
channel = "stable-22_11"

[deployment]
run = ["bash", "start-replit.sh"]
```

**Create `start-replit.sh`:**
```bash
#!/bin/bash

# Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start frontend
cd ../frontend
npm install
npm run dev -- --host &

wait
```

4. **Click "Run"**

---

### Option 3: Railway (Best for Production)

**Best for:** Production deployment
**Cost:** Free $5/month credit, then pay-as-you-go
**Setup time:** 10 minutes

#### Steps:

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
railway login
```

2. **Create New Project:**
```bash
railway init
```

3. **Add PostgreSQL:**
   - Go to Railway dashboard
   - Click "New" → "Database" → "PostgreSQL"
   - Copy DATABASE_URL from variables

4. **Deploy Backend:**
```bash
cd backend
railway up
```

5. **Set Environment Variables:**
   - In Railway dashboard, go to backend service
   - Add variables:
     - `DATABASE_URL` (from PostgreSQL service)
     - `CORS_ORIGINS` (your frontend URL)

6. **Deploy Frontend:**
```bash
cd ../frontend
railway up
```

7. **Set Frontend Variable:**
   - `VITE_API_BASE_URL` (your backend URL)

8. **Generate Domains:**
   - Click on each service
   - Go to "Settings" → "Generate Domain"

**Railway Configuration (`railway.json`):**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### Option 4: Render (Good Alternative)

**Best for:** Production, simpler than Railway
**Cost:** Free tier available
**Setup time:** 15 minutes

#### Steps:

1. **Go to [render.com](https://render.com)**

2. **Create PostgreSQL Database:**
   - Dashboard → New → PostgreSQL
   - Copy Internal/External Database URL

3. **Create Backend Web Service:**
   - New → Web Service
   - Connect your GitHub repo
   - Settings:
     - **Root Directory:** `backend`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `DATABASE_URL` (from step 2)
     - `CORS_ORIGINS` (will be frontend URL)

4. **Create Frontend Web Service:**
   - New → Web Service
   - Same repo
   - Settings:
     - **Root Directory:** `frontend`
     - **Build Command:** `npm install && npm run build`
     - **Start Command:** `npm run preview`
   - Environment Variables:
     - `VITE_API_BASE_URL` (backend URL from step 3)

5. **Update CORS:**
   - Go back to backend service
   - Update `CORS_ORIGINS` with frontend URL

---

### Option 5: StackBlitz (Browser-Only)

**Best for:** Quick demos, no backend persistence
**Cost:** Free
**Setup time:** 2 minutes
**Limitations:** In-memory database only

#### Steps:

1. **Go to [stackblitz.com](https://stackblitz.com)**
2. **Create new project → Import from GitHub**
3. **Use SQLite:**

**Modify backend config:**
```python
DATABASE_URL: str = "sqlite:///./dashboard.db"
```

**Note:** Data will be lost on restart

---

### Option 6: Vercel (Frontend) + Railway (Backend)

**Best for:** Production, separate concerns
**Cost:** Free tiers available
**Setup time:** 20 minutes

#### Frontend on Vercel:

1. **Go to [vercel.com](https://vercel.com)**
2. **Import your GitHub repo**
3. **Framework:** Vite
4. **Root Directory:** `frontend`
5. **Build Command:** `npm run build`
6. **Output Directory:** `dist`
7. **Environment Variable:**
   - `VITE_API_BASE_URL` (your Railway backend URL)

#### Backend on Railway:

Follow Railway steps above.

---

## 🔧 Platform Comparison

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Gitpod** | Full Docker support, VS Code in browser | Limited free hours | Development |
| **Replit** | Super simple, no Docker needed | Performance limitations | Quick demos |
| **Railway** | Easy deployment, great DX | Costs after free credit | Production |
| **Render** | Free tier, reliable | Slower cold starts | Small projects |
| **StackBlitz** | Instant, no setup | No real backend | Frontend demos |
| **Vercel+Railway** | Best performance | More complex setup | Production apps |

---

## 🚀 Recommended Path

### For Learning/Development:
1. **Start with Gitpod** (full features)
2. Use for development and testing
3. Free tier is generous

### For Production:
1. **Use Railway** (easiest)
2. Or **Vercel + Railway** (best performance)
3. Set up monitoring and backups

---

## 📝 Environment Variables Checklist

### Backend (.env):
```bash
DATABASE_URL=postgresql://...
ENVIRONMENT=production
SECRET_KEY=<generate-random-key>
CORS_ORIGINS=https://your-frontend.com
```

### Frontend (.env):
```bash
VITE_API_BASE_URL=https://your-backend.com
```

---

## 🔐 Security for Production

Before deploying:

1. **Change SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Enable HTTPS** (most platforms do this automatically)

3. **Set environment to production:**
```bash
ENVIRONMENT=production
DEBUG=false
```

4. **Use strong database password**

5. **Set up firewall rules** (platform-specific)

---

## 🐛 Troubleshooting Online Deployments

### Database Connection Issues:
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### CORS Errors:
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check protocol (http vs https)
- No trailing slashes in URLs

### Build Failures:
```bash
# Check logs on platform
# Verify all dependencies in requirements.txt/package.json
# Test build locally first
```

### Port Issues:
Most platforms set `PORT` environment variable:
```python
# Use platform's PORT
port = int(os.getenv("PORT", 8000))
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

---

## 📞 Platform-Specific Support

- **Gitpod:** https://www.gitpod.io/docs
- **Railway:** https://docs.railway.app
- **Render:** https://render.com/docs
- **Vercel:** https://vercel.com/docs
- **Replit:** https://docs.replit.com

---

## 💡 Pro Tips

1. **Start with Gitpod** - get familiar with the system
2. **Test locally first** - easier to debug
3. **Use platform-provided PostgreSQL** - don't manage your own
4. **Monitor costs** - set up billing alerts
5. **Use environment variables** - never commit secrets
6. **Set up logging** - use platform logging features
7. **Enable auto-deploy** - connect to GitHub for CI/CD

---

Ready to deploy? Pick a platform and follow the steps above! 🚀
