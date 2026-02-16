# Configurable Dashboard System with GridStack

A production-ready, configuration-driven dashboard system with **drag-drop and resize** capabilities using GridStack. Create Power BI-like dashboards in minutes using only configuration files.

## ✨ **New Features - GridStack Integration**

- ✅ **Drag & Drop** - Reorder widgets by dragging headers
- ✅ **Resize** - Resize widgets from all edges and corners
- ✅ **Edit Mode** - Toggle edit mode to lock/unlock layout  
- ✅ **Auto-Save** - Layout automatically saves to localStorage
- ✅ **Responsive** - 12-column grid system
- ✅ **All Widgets Working** - Line charts, bar charts, pie charts, tables, metrics

## 🚀 **Quick Start**

```bash
# 1. Start everything with Docker
./start.sh

# 2. Access dashboard
open http://localhost:5173

# 3. Click "Edit Layout" and start dragging!
```

## 🎮 **Using Drag & Drop**

1. Open dashboard at http://localhost:5173
2. Click **"Edit Layout"** button (top right)
3. **Drag widgets** by their header
4. **Resize** from corners/edges
5. Click **"Done Editing"** to save

**Your layout is saved automatically!**

## 📊 **Sample Dashboard Included**

Access at: `/dashboard/sales-dashboard`

- 4 draggable KPI cards
- Revenue trend chart (resizable)
- Regional bar chart (resizable)
- Products data table (resizable)
- Global date filters

## 💡 **Create New Dashboard (5 min)**

### 1. Define Query (`backend/queries/my_data.yaml`)

```yaml
queries:
  my_query:
    sql: |
      SELECT date, revenue
      FROM sales
      WHERE date >= :start_date
```

### 2. Create Config (`frontend/src/config/dashboards/my-dash.json`)

```json
{
  "id": "my-dash",
  "title": "My Dashboard",
  "widgets": [{
    "id": "chart1",
    "type": "line-chart",
    "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
    "queryId": "my_query"
  }]
}
```

### 3. Access

Navigate to: `/dashboard/my-dash`

**Done! Now drag and resize!** 🎉

## 📁 **Key Files**

```
backend/
  queries/           ← Add SQL queries here
  app/core/
    query_executor.py  ← Universal query engine

frontend/
  src/
    components/
      Dashboard/
        DashboardRenderer.vue  ← GridStack integration
      widgets/         ← 5 pre-built widgets
    config/
      dashboards/      ← Add dashboard configs here
```

## 🔧 **GridStack Features**

- **12-column grid** with 80px row height
- **5 resize handles**: East, West, South, SE, SW
- **Drag from header** only (prevents accidental drags)
- **Smooth animations**
- **Auto-save** to localStorage

## 📚 **Full Documentation**

- [Getting Started](docs/getting-started.md)
- [Dashboard Config Guide](docs/dashboard-config.md)
- [Deployment Guide](docs/deployment.md)
- [Online Platforms](docs/online-platforms.md)

## 🎨 **Widget Types**

All widgets support drag & resize:

- **metric-card** - KPI with icon
- **line-chart** - Time series
- **bar-chart** - Categorical
- **pie-chart** - Proportions
- **data-table** - Sortable table

## 🛠️ **Tech Stack**

- **Frontend**: Vue 3 + GridStack + ECharts + Tailwind
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **DevOps**: Docker Compose

## 🐛 **Troubleshooting**

**Widgets not dragging?**
- Click "Edit Layout" button first
- Check console for errors

**Layout not saving?**
- Verify localStorage is enabled
- Check `dashboardId` prop

**Backend errors?**
```bash
docker-compose logs backend
```

## 📈 **vs Power BI**

| Feature | Power BI | This System |
|---------|----------|-------------|
| New Dashboard | 30-60 min | 5-10 min |
| Drag & Drop | ✅ | ✅ |
| Resize | ✅ | ✅ |
| Version Control | ❌ | ✅ |
| Cost | $10-20/user | Free |

## 🚀 **Deploy**

See [Deployment Guide](docs/deployment.md) for:
- Railway (easiest)
- Vercel + Railway
- AWS / GCP / Azure
- Docker production

## 📝 **License**

MIT License

---

**Ready?** Run `./start.sh` and start building! 🎉
