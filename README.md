# Configurable Dashboard System

A production-ready, configuration-driven dashboard system built with Vue 3 and FastAPI that allows you to create Power BI-like dashboards in minutes using only configuration files.

## 🚀 Quick Start

```bash
# Start both backend and frontend with Docker Compose
docker-compose up

# Or run separately:

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Access the dashboard at: http://localhost:5173

## 📁 Project Structure

```
configurable-dashboard-system/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Database & config
│   │   ├── models/      # Data models
│   │   └── utils/       # Utilities
│   └── queries/         # SQL query definitions (YAML)
├── frontend/            # Vue 3 frontend
│   └── src/
│       ├── components/  # Vue components
│       ├── config/      # Dashboard configs (JSON)
│       ├── composables/ # Vue composables
│       └── stores/      # Pinia stores
└── docker/              # Docker configurations
```

## 🎯 Key Features

- **Configuration-Driven**: Create dashboards with JSON configs only
- **Universal Query Executor**: One endpoint executes all SQL queries
- **Pre-built Widgets**: Line charts, bar charts, tables, metrics, pie charts
- **Global Filters**: Automatic filter propagation to all widgets
- **Real-time Updates**: Auto-refresh with configurable intervals
- **Export Ready**: Export tables to CSV/Excel
- **Responsive Grid**: Drag-and-drop layout system
- **Type-Safe**: Full TypeScript support

## 📊 Creating a New Dashboard (5 minutes)

### Step 1: Define SQL Query (queries/my_dashboard.yaml)

```yaml
queries:
  sales_overview:
    sql: |
      SELECT 
        DATE(order_date) as date,
        SUM(amount) as revenue,
        COUNT(*) as orders
      FROM orders
      WHERE order_date >= :start_date
      GROUP BY DATE(order_date)
    parameters:
      - name: start_date
        type: date
        default: "30_days_ago"
```

### Step 2: Create Dashboard Config (config/dashboards/my_dashboard.json)

```json
{
  "id": "my-dashboard",
  "title": "Sales Dashboard",
  "widgets": [
    {
      "id": "revenue_chart",
      "type": "line-chart",
      "queryId": "sales_overview",
      "position": { "x": 0, "y": 0, "w": 6, "h": 4 }
    }
  ]
}
```

### Step 3: Add Route (Done!)

The dashboard is automatically available at `/dashboard/my-dashboard`

## 🔧 Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy
- PostgreSQL / MySQL / SQLite
- Pydantic for validation
- PyYAML for config parsing

**Frontend:**
- Vue 3 (Composition API)
- Pinia (State Management)
- Apache ECharts (Charts)
- TanStack Table (Tables)
- Tailwind CSS
- TypeScript

## 📖 Documentation

- [Backend API Documentation](docs/backend-api.md)
- [Dashboard Configuration Guide](docs/dashboard-config.md)
- [Widget Types Reference](docs/widgets.md)
- [Deployment Guide](docs/deployment.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📦 Environment Setup

### Online Environments

You can run this project on:

1. **StackBlitz** - Instant dev environment in browser
2. **CodeSandbox** - Full-stack development
3. **Gitpod** - Cloud-based IDE
4. **Replit** - Quick prototyping
5. **Railway.app** - Production deployment
6. **Vercel** (Frontend) + **Railway** (Backend)

See [deployment guide](docs/deployment.md) for details.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🆘 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discussions: GitHub Discussions
