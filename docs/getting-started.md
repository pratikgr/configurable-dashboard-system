# Getting Started Guide

## Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.11+ and Node.js 20+
- PostgreSQL (if not using Docker)

## Quick Start with Docker (Recommended)

### 1. Clone and Start

```bash
# Clone the repository
git clone <your-repo-url>
cd configurable-dashboard-system

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Verify Setup

```bash
# Check if all services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","timestamp":"...","database":"healthy","queries_loaded":6}
```

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb dashboard_db
psql dashboard_db < init.sql

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://dashboard_user:dashboard_pass@localhost:5432/dashboard_db
ENVIRONMENT=development
EOF

# Start backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

## Understanding the System

### Architecture Overview

```
┌─────────────────┐
│  Vue Frontend   │  ← Dashboard UI (Port 5173)
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  FastAPI Server │  ← Universal Query Executor (Port 8000)
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│  PostgreSQL DB  │  ← Data Storage (Port 5432)
└─────────────────┘

Configuration Files:
• queries/*.yaml      → SQL query definitions
• config/dashboards/*.json → Dashboard layouts
```

### Key Concepts

1. **Universal Query Executor**: One API endpoint executes all queries
2. **Configuration-Driven**: Dashboards defined in JSON, no code changes
3. **Reusable Widgets**: Pre-built components (charts, tables, metrics)
4. **Smart Defaults**: Built-in date shortcuts like "30_days_ago"

## Your First Dashboard (5 Minutes)

Let's create a simple "Revenue Dashboard" step by step.

### Step 1: Create Query Definition (2 min)

Create `backend/queries/revenue.yaml`:

```yaml
queries:
  daily_revenue:
    description: "Daily revenue for date range"
    sql: |
      SELECT 
        DATE(order_date) as date,
        SUM(amount) as revenue,
        COUNT(*) as orders
      FROM orders
      WHERE order_date >= :start_date 
        AND order_date <= :end_date
        AND status = 'completed'
      GROUP BY DATE(order_date)
      ORDER BY date ASC
    parameters:
      - name: start_date
        type: date
        default: "30_days_ago"
      - name: end_date
        type: date
        default: "today"
    cache_ttl: 300
```

### Step 2: Create Dashboard Config (3 min)

Create `frontend/src/config/dashboards/revenue-dashboard.json`:

```json
{
  "id": "revenue-dashboard",
  "title": "Revenue Dashboard",
  "description": "Daily revenue tracking",
  
  "globalFilters": [
    {
      "id": "start_date",
      "type": "daterange",
      "label": "Start Date",
      "default": "2024-01-01",
      "applyTo": "*"
    },
    {
      "id": "end_date",
      "type": "daterange",
      "label": "End Date",
      "default": "2024-12-31",
      "applyTo": "*"
    }
  ],
  
  "widgets": [
    {
      "id": "total_revenue",
      "type": "metric-card",
      "position": { "x": 0, "y": 0, "w": 6, "h": 2 },
      "title": "Total Revenue",
      "queryId": "daily_revenue",
      "dataMapping": {
        "value": "SUM(revenue)"
      },
      "format": {
        "type": "currency",
        "currency": "USD"
      },
      "icon": "dollar",
      "color": "green"
    },
    {
      "id": "revenue_chart",
      "type": "line-chart",
      "position": { "x": 0, "y": 2, "w": 12, "h": 4 },
      "title": "Daily Revenue Trend",
      "queryId": "daily_revenue",
      "dataMapping": {
        "x": "date",
        "y": "revenue"
      },
      "chartOptions": {
        "smooth": true,
        "showArea": true,
        "colors": ["#10b981"]
      }
    }
  ]
}
```

### Step 3: Reload and Access

```bash
# Reload queries (if backend is running)
curl -X POST http://localhost:8000/api/query/reload

# Access your dashboard
open http://localhost:5173/dashboard/revenue-dashboard
```

**Done!** Your dashboard is live! 🎉

## Exploring the Sample Dashboard

A complete sales dashboard is included as an example:

```bash
# View the dashboard
open http://localhost:5173/dashboard/sales-dashboard
```

**What you'll see:**
- 4 metric cards (Total Revenue, Orders, Customers, Avg Order Value)
- Line chart showing revenue trend
- Bar chart showing revenue by region
- Data table with top products

**Explore the code:**
- Query definitions: `backend/queries/sales.yaml`
- Dashboard config: `frontend/src/config/dashboards/sales-dashboard.json`

## Common Commands

### Development

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Database

```bash
# Access database
docker-compose exec db psql -U dashboard_user -d dashboard_db

# Run SQL file
docker-compose exec -T db psql -U dashboard_user -d dashboard_db < your_file.sql

# Backup database
docker-compose exec db pg_dump -U dashboard_user dashboard_db > backup.sql
```

### API Testing

```bash
# List all queries
curl http://localhost:8000/api/query/list | jq

# Execute a query
curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "sales_overview",
    "parameters": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  }' | jq

# Get query info
curl http://localhost:8000/api/query/sales_overview | jq

# Health check
curl http://localhost:8000/api/health | jq
```

## Next Steps

### 1. Learn the Configuration System

Read the [Dashboard Configuration Guide](dashboard-config.md) to understand:
- All widget types available
- Advanced configuration options
- Best practices

### 2. Customize Your Queries

Edit `backend/queries/sales.yaml` or create new YAML files.

**Pro tip**: Use smart date defaults:
- `today`, `yesterday`
- `7_days_ago`, `30_days_ago`, `90_days_ago`
- `start_of_month`, `start_of_year`

### 3. Build More Dashboards

Copy `sales-dashboard.json` as a template and modify:
- Change widget positions and sizes
- Add/remove widgets
- Configure filters
- Adjust styling

### 4. Add Your Own Data

Replace sample data with real data:
1. Create your tables in PostgreSQL
2. Write queries in YAML files
3. Create dashboard configs
4. Done!

## Troubleshooting

### Dashboard Not Showing Data

**Check query execution:**
```bash
# Test the query directly
curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d '{"query_id": "your_query_id"}' | jq
```

**Check browser console:**
- Open DevTools (F12)
- Look for red errors in Console
- Check Network tab for failed requests

### Backend Not Starting

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Database not ready: Wait 30 seconds and retry
- Port 8000 in use: Stop other services or change port
- Invalid YAML: Check syntax in query files

### Frontend Not Loading

**Check if Vite is running:**
```bash
docker-compose logs frontend
```

**Common issues:**
- Port 5173 in use: Change in `vite.config.js`
- Node modules missing: Run `npm install`
- API connection failed: Verify backend is running

### Database Connection Issues

**Test connection:**
```bash
docker-compose exec db psql -U dashboard_user -d dashboard_db -c "SELECT 1"
```

**Reset database:**
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Backend**: Auto-reloads when Python files change
- **Frontend**: Auto-reloads when Vue files change
- **Queries**: Call `/api/query/reload` endpoint

### Testing Queries

Use the FastAPI interactive docs:
1. Go to http://localhost:8000/docs
2. Expand `/api/query/execute`
3. Click "Try it out"
4. Enter query ID and parameters
5. Click "Execute"

### Widget Development

To create custom widgets:
1. Create component in `frontend/src/components/widgets/`
2. Register in `frontend/src/utils/widgetRegistry.js`
3. Use in dashboard configs

## Getting Help

- **Documentation**: Check `/docs` directory
- **API Reference**: http://localhost:8000/docs
- **Sample Code**: Explore existing dashboards
- **Logs**: Always check logs first

## Performance Tips

1. **Index your database**: Add indexes to frequently queried columns
2. **Use caching**: Set appropriate `cache_ttl` in queries
3. **Limit data**: Use `LIMIT` clause in SQL
4. **Paginate tables**: Set `pageSize` in table widgets

## What's Next?

Now that you have a working system:

1. **Replace sample data** with your real data
2. **Create custom queries** for your specific needs
3. **Build dashboards** for different teams/use cases
4. **Deploy to production** (see [Deployment Guide](deployment.md))

## Quick Reference

| Task | Command/File |
|------|--------------|
| Add new query | Create YAML in `backend/queries/` |
| Create dashboard | Create JSON in `frontend/src/config/dashboards/` |
| Test query | POST to `/api/query/execute` |
| View API docs | http://localhost:8000/docs |
| Check logs | `docker-compose logs -f` |
| Reload queries | POST to `/api/query/reload` |

---

**Ready to build your first dashboard?** Follow the "Your First Dashboard" section above! 🚀
