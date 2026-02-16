# Deployment Guide

## Online Development Environments

### 1. StackBlitz (Recommended for Quick Demo)

StackBlitz provides instant, browser-based development.

**Steps:**
1. Go to [stackblitz.com](https://stackblitz.com)
2. Click "Import from GitHub"
3. Paste your repository URL
4. Wait for environment to load
5. Terminal will be available for running commands

**Limitations:**
- No PostgreSQL support (use SQLite instead)
- Limited file system access

**Setup for StackBlitz:**

Update `backend/app/core/config.py`:
```python
DATABASE_URL: str = "sqlite:///./dashboard.db"  # For StackBlitz
```

### 2. CodeSandbox

Full-stack development environment with better database support.

**Steps:**
1. Visit [codesandbox.io](https://codesandbox.io)
2. Create new Sandbox
3. Choose "Import from GitHub"
4. Select your repository
5. CodeSandbox will auto-detect Docker Compose

**Advantages:**
- Supports Docker Compose
- Full PostgreSQL support
- Better for production-like testing

### 3. Gitpod

Cloud-based VS Code experience.

**Steps:**
1. Prefix your GitHub repo URL with: `gitpod.io/#`
2. Example: `gitpod.io/#https://github.com/yourusername/your-repo`
3. Create `.gitpod.yml` in root:

```yaml
tasks:
  - name: Backend
    init: cd backend && pip install -r requirements.txt
    command: cd backend && uvicorn app.main:app --reload --host 0.0.0.0
  
  - name: Frontend
    init: cd frontend && npm install
    command: cd frontend && npm run dev

ports:
  - port: 8000
    onOpen: ignore
  - port: 5173
    onOpen: open-preview
```

### 4. Replit

Simplified online IDE, good for quick prototyping.

**Steps:**
1. Go to [replit.com](https://replit.com)
2. Create new Repl
3. Choose "Import from GitHub"
4. Add `.replit` file:

```toml
run = "docker-compose up"
language = "bash"

[nix]
channel = "stable-22_11"
```

## Cloud Deployment

### Railway.app (Easiest Production Deployment)

Railway provides free tier with PostgreSQL included.

**Steps:**

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
railway login
```

2. **Initialize Project:**
```bash
railway init
```

3. **Deploy Backend:**
```bash
cd backend
railway up
```

4. **Deploy Frontend:**
```bash
cd frontend
railway up
```

5. **Add PostgreSQL:**
- Go to Railway dashboard
- Click "New" → "Database" → "PostgreSQL"
- Copy connection string
- Add to backend environment variables

**Environment Variables (Railway):**
```
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://your-frontend.railway.app
```

### Vercel (Frontend) + Railway (Backend)

Best combination for production.

**Frontend (Vercel):**

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Set environment variable:
```
VITE_API_BASE_URL=https://your-backend.railway.app
```

**Backend (Railway):**
Follow Railway steps above.

### AWS Deployment

**Using AWS Elastic Beanstalk:**

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize:**
```bash
cd backend
eb init -p python-3.11 dashboard-backend
```

3. **Create environment:**
```bash
eb create dashboard-prod
```

4. **Deploy:**
```bash
eb deploy
```

**Using AWS ECS (Docker):**

1. Build and push images:
```bash
docker build -t dashboard-backend ./backend
docker tag dashboard-backend:latest YOUR_ECR_URI/dashboard-backend:latest
docker push YOUR_ECR_URI/dashboard-backend:latest
```

2. Create ECS task definition
3. Create ECS service
4. Configure Application Load Balancer

### Google Cloud Run

**Steps:**

1. **Build container:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/dashboard-backend ./backend
```

2. **Deploy:**
```bash
gcloud run deploy dashboard-backend \
  --image gcr.io/YOUR_PROJECT/dashboard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Docker Deployment

### Local with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: always

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_API_BASE_URL=${API_URL}
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres_data:
```

## Database Setup

### PostgreSQL (Production)

```bash
# Create database
createdb dashboard_db

# Run migrations
psql dashboard_db < backend/init.sql

# Or using Docker
docker-compose exec db psql -U dashboard_user -d dashboard_db -f /docker-entrypoint-initdb.d/init.sql
```

### Environment Variables

Create `.env` file:

```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/dashboard_db
ENVIRONMENT=production
SECRET_KEY=your-secret-key-change-this
CORS_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Monitoring & Logging

### Setup Logging

Add to `backend/app/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Health Checks

Built-in endpoints:
- `GET /api/health` - Overall health
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

### Monitoring with Prometheus

Add to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

## SSL/HTTPS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

## Performance Optimization

### Backend

1. **Enable caching:**
```python
# Install Redis
docker run -d -p 6379:6379 redis

# Update config
CACHE_ENABLED: bool = True
REDIS_URL: str = "redis://localhost:6379"
```

2. **Database connection pooling:**
Already configured in SQLAlchemy settings.

3. **Query optimization:**
- Add database indexes
- Use query result caching
- Limit result sizes

### Frontend

1. **Build optimizations:**
```bash
npm run build
```

2. **CDN for static assets:**
Upload `/dist` folder to CDN.

3. **Enable compression:**
Nginx gzip configuration included.

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using port
lsof -i :8000
lsof -i :5173

# Kill process
kill -9 PID
```

**Database connection errors:**
```bash
# Test connection
psql -h localhost -U dashboard_user -d dashboard_db

# Check Docker network
docker network inspect dashboard-network
```

**CORS errors:**
Verify `CORS_ORIGINS` in backend config matches frontend URL.

## Scaling

### Horizontal Scaling

1. **Load balancer setup**
2. **Multiple backend instances**
3. **Shared Redis cache**
4. **Database read replicas**

### Vertical Scaling

Increase Docker resources:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U dashboard_user dashboard_db > backup.sql

# Restore
docker-compose exec -T db psql -U dashboard_user dashboard_db < backup.sql
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Use strong database passwords
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review documentation
- Open GitHub issue
- Check health endpoints
