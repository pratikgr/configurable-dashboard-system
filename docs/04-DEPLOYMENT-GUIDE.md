# Deployment Guide

## Overview

This guide covers deploying the AI-Powered Dashboard System in various environments.

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 2GB
- Disk: 1GB
- OS: Windows 10+, macOS 10.15+, Ubuntu 20.04+

**Recommended (Production):**
- CPU: 4 cores
- RAM: 4GB
- Disk: 5GB
- OS: Ubuntu 22.04 LTS

### Software Requirements

- **Python:** 3.11 or higher
- **Node.js:** 18 or higher
- **npm:** 9 or higher
- **Git:** 2.30 or higher

### Azure Requirements

- Azure subscription
- Azure OpenAI resource with GPT-4 deployment
- API keys and endpoint URL

---

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/dashboard-system.git
cd dashboard-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install --break-system-packages -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Azure credentials
nano .env
```

**Required `.env` Configuration:**
```bash
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db
CORS_ORIGINS=["http://localhost:5173"]

AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

DASHBOARD_CONFIG_DIR=../frontend/src/config/dashboards
```

### 3. Initialize Database

```bash
# Run database initialization
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 5. Frontend Setup

Open new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit if needed (defaults are fine for dev)
nano .env
```

**Frontend `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 6. Start Frontend

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

### 7. Verify Setup

1. Open `http://localhost:5173` in browser
2. Click purple FAB (floating button) bottom-right
3. Chat panel opens
4. Type: "List all queries"
5. AI should respond with query list

---

## Production Deployment

### Option 1: Single Server (Ubuntu)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot (for SSL)
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. Deploy Backend

```bash
# Create app directory
sudo mkdir -p /var/www/dashboard
sudo chown $USER:$USER /var/www/dashboard

# Clone code
cd /var/www/dashboard
git clone https://github.com/your-org/dashboard-system.git .

# Backend setup
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create production .env
nano .env
```

**Production `.env`:**
```bash
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db
CORS_ORIGINS=["https://dashboard.example.com"]

AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

DASHBOARD_CONFIG_DIR=/var/www/dashboard/dashboards
```

#### 3. Create Systemd Service

```bash
sudo nano /etc/systemd/system/dashboard-api.service
```

**Service File:**
```ini
[Unit]
Description=Dashboard API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dashboard/backend
Environment="PATH=/var/www/dashboard/backend/.venv/bin"
ExecStart=/var/www/dashboard/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard-api
sudo systemctl start dashboard-api
sudo systemctl status dashboard-api
```

#### 4. Build Frontend

```bash
cd /var/www/dashboard/frontend

# Install dependencies
npm install

# Create production .env
nano .env
```

**Frontend `.env.production`:**
```bash
VITE_API_BASE_URL=https://api.dashboard.example.com
```

**Build:**
```bash
npm run build
```

Output is in `dist/` folder.

#### 5. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/dashboard
```

**Nginx Configuration:**
```nginx
# Frontend
server {
    listen 80;
    server_name dashboard.example.com;
    
    root /var/www/dashboard/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}

# Backend API
server {
    listen 80;
    server_name api.dashboard.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE specific
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Setup SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d dashboard.example.com -d api.dashboard.example.com
```

Follow prompts. Certbot auto-renews.

#### 7. Verify Deployment

1. Visit `https://dashboard.example.com`
2. Open chat, test AI
3. Create a widget
4. Check logs: `sudo journalctl -u dashboard-api -f`

---

### Option 2: Docker Compose

#### 1. Create Dockerfile (Backend)

**`backend/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create dashboards directory
RUN mkdir -p /app/dashboards

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create Dockerfile (Frontend)

**`frontend/Dockerfile`:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production image with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**`frontend/nginx.conf`:**
```nginx
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

#### 3. Create docker-compose.yml

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: dashboard-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./dashboard.db
      - CORS_ORIGINS=["http://localhost:3000"]
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
      - DASHBOARD_CONFIG_DIR=/app/dashboards
    volumes:
      - ./dashboards:/app/dashboards
      - ./backend/dashboard.db:/app/dashboard.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: dashboard-frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

#### 4. Deploy with Docker

```bash
# Create .env file in root
nano .env

# Add Azure credentials
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: `http://localhost:3000`

---

## Cloud Deployment

### AWS (EC2 + RDS)

**Architecture:**
```
ALB → EC2 (Backend) → RDS (PostgreSQL)
ALB → S3 + CloudFront (Frontend)
```

**Steps:**
1. Launch EC2 instance (Ubuntu 22.04, t3.medium)
2. Follow "Single Server" deployment above
3. Create RDS PostgreSQL instance
4. Update `DATABASE_URL` to PostgreSQL connection string
5. Build frontend, upload to S3
6. Configure CloudFront distribution
7. Setup Route53 for DNS

### Azure (App Service)

**Architecture:**
```
App Service (Backend) → Azure SQL
Static Web App (Frontend)
```

**Steps:**
1. Create App Service (Python 3.11)
2. Deploy backend code via Git or ZIP
3. Configure App Settings with env vars
4. Create Static Web App
5. Deploy frontend build to Static Web App
6. Configure custom domain

### Google Cloud (Cloud Run)

**Architecture:**
```
Cloud Run (Backend) → Cloud SQL
Firebase Hosting (Frontend)
```

**Steps:**
1. Build Docker image for backend
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Build frontend
5. Deploy to Firebase Hosting
6. Configure CORS

---

## Database Migration

### From SQLite to PostgreSQL

**1. Export SQLite Data:**
```bash
sqlite3 dashboard.db .dump > dump.sql
```

**2. Convert SQL:**
```bash
# Remove SQLite-specific syntax
sed -i 's/AUTOINCREMENT/SERIAL/g' dump.sql
sed -i 's/INTEGER PRIMARY KEY/SERIAL PRIMARY KEY/g' dump.sql
```

**3. Import to PostgreSQL:**
```bash
psql -U postgres -d dashboard < dump.sql
```

**4. Update Backend:**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary asyncpg

# Update .env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dashboard
```

---

## Monitoring & Logging

### Application Logs

**Backend (Systemd):**
```bash
sudo journalctl -u dashboard-api -f
```

**Docker:**
```bash
docker-compose logs -f backend
```

### Log Rotation

**`/etc/logrotate.d/dashboard-api`:**
```
/var/log/dashboard/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload dashboard-api
    endscript
}
```

### Health Monitoring

**Setup Uptime Monitoring:**
- UptimeRobot
- Pingdom
- StatusCake

**Endpoints to Monitor:**
- `https://api.dashboard.example.com/api/health` (every 5 min)
- `https://dashboard.example.com` (every 5 min)

### Error Tracking

**Recommended Tools:**
- Sentry (Python + JavaScript)
- Rollbar
- Bugsnag

**Setup Sentry:**
```bash
pip install sentry-sdk[fastapi]
```

```python
# In main.py
import sentry_sdk
sentry_sdk.init(dsn="your-dsn-here")
```

---

## Backup & Recovery

### Database Backup

**SQLite (Automated):**
```bash
# Create backup script
nano /usr/local/bin/backup-dashboard.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/dashboard"
mkdir -p $BACKUP_DIR

# Backup database
cp /var/www/dashboard/backend/dashboard.db $BACKUP_DIR/dashboard_$DATE.db

# Compress
gzip $BACKUP_DIR/dashboard_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

**Cron Job:**
```bash
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-dashboard.sh
```

### Dashboard Config Backup

```bash
# Backup dashboard configs
tar -czf /var/backups/dashboard/configs_$(date +%Y%m%d).tar.gz \
  /var/www/dashboard/dashboards
```

### Recovery

```bash
# Restore database
gunzip -c /var/backups/dashboard/dashboard_20260222.db.gz > dashboard.db

# Restore configs
tar -xzf /var/backups/dashboard/configs_20260222.tar.gz -C /var/www/dashboard/
```

---

## Performance Tuning

### Backend Optimization

**Increase Workers:**
```bash
# In systemd service or docker-compose
--workers 4  # (2 * CPU cores) + 1
```

**Enable Caching:**
```bash
pip install aiocache redis
```

**Connection Pooling:**
```python
# In database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0
)
```

### Frontend Optimization

**Build with Optimization:**
```bash
npm run build -- --mode production
```

**Enable Compression (Nginx):**
```nginx
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript;
```

**CDN:**
- Use CloudFlare
- Or AWS CloudFront
- Cache static assets

---

## Security Hardening

### SSL/TLS

**Force HTTPS (Nginx):**
```nginx
server {
    listen 80;
    server_name dashboard.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Rate Limiting (Nginx)

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20;
    }
}
```

### Environment Variables

**Never commit `.env` files!**

Add to `.gitignore`:
```
.env
.env.*
!.env.example
```

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
sudo journalctl -u dashboard-api -n 50
```

**Common issues:**
- Missing environment variables
- Port 8000 already in use
- Database file permissions
- Python dependencies missing

### Frontend Build Fails

**Check Node version:**
```bash
node --version  # Should be 18+
```

**Clear cache:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### AI Not Responding

**Check Azure OpenAI:**
```bash
curl -X POST http://localhost:8000/api/ai/status
```

**Verify credentials:**
- Endpoint URL correct?
- API key valid?
- Deployment name correct?
- API version supported?

### Database Errors

**Check file permissions:**
```bash
ls -la dashboard.db
# Should be writable by app user
```

**Recreate database:**
```bash
rm dashboard.db
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## Maintenance

### Updates

**Backend:**
```bash
cd /var/www/dashboard/backend
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dashboard-api
```

**Frontend:**
```bash
cd /var/www/dashboard/frontend
git pull
npm install
npm run build
```

### Database Maintenance

**SQLite Vacuum:**
```bash
sqlite3 dashboard.db 'VACUUM;'
```

**Check Size:**
```bash
du -h dashboard.db
```

---

## Rollback Procedure

**1. Stop Services:**
```bash
sudo systemctl stop dashboard-api
```

**2. Restore from Backup:**
```bash
cp /var/backups/dashboard/dashboard_20260222.db.gz .
gunzip dashboard_20260222.db.gz
mv dashboard_20260222.db dashboard.db
```

**3. Revert Code:**
```bash
git checkout v1.0.0  # Previous working version
```

**4. Restart:**
```bash
sudo systemctl start dashboard-api
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-22  
**Deployment Tested On:** Ubuntu 22.04, Docker 24.0
