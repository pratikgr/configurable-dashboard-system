# 🚀 GridStack Dashboard - Quick Start Guide

## What You Got

A **fully working** dashboard system with:
- ✅ **Drag & Drop** - Move widgets around
- ✅ **Resize** - Make widgets bigger/smaller
- ✅ **5 Working Widgets** - Charts, tables, metrics
- ✅ **Sample Data** - 500+ orders ready to visualize
- ✅ **Auto-Save** - Your layout persists

## Start in 3 Commands

```bash
# 1. Extract the ZIP file
unzip configurable-dashboard-system-gridstack.zip
cd configurable-dashboard-system

# 2. Start everything
./start.sh

# 3. Open browser
open http://localhost:5173
```

**That's it!** 🎉

## Using Drag & Drop (30 seconds)

1. **See the sample dashboard** - It loads automatically
2. **Click "Edit Layout"** (top right corner)
3. **Drag any widget** by clicking its header and moving
4. **Resize any widget** by dragging corners or edges
5. **Click "Done Editing"** - Your layout is saved!

**Refresh the page** - Your layout persists! 🎨

## What's in the Sample Dashboard?

✅ **4 Metric Cards** (top row)
- Total Revenue
- Total Orders  
- Unique Customers
- Avg Order Value

✅ **Revenue Trend** (line chart)
✅ **Revenue by Region** (bar chart)
✅ **Top Products** (data table with sorting)

**All widgets are draggable and resizable!**

## Create Your First Dashboard (5 minutes)

### Step 1: Add a Query (2 min)

Create `backend/queries/products.yaml`:

```yaml
queries:
  product_list:
    sql: |
      SELECT 
        product_name,
        category,
        unit_price
      FROM products
      ORDER BY unit_price DESC
      LIMIT 20
```

### Step 2: Create Dashboard (3 min)

Create `frontend/src/config/dashboards/products.json`:

```json
{
  "id": "products",
  "title": "Products Dashboard",
  "widgets": [
    {
      "id": "products_table",
      "type": "data-table",
      "position": { "x": 0, "y": 0, "w": 12, "h": 5 },
      "title": "All Products",
      "queryId": "product_list",
      "columns": [
        { "field": "product_name", "header": "Product" },
        { "field": "category", "header": "Category" },
        { 
          "field": "unit_price", 
          "header": "Price",
          "format": { "type": "currency", "currency": "USD" }
        }
      ]
    }
  ]
}
```

### Step 3: View Your Dashboard

Navigate to: `http://localhost:5173/dashboard/products`

**Now drag and resize it!** ✨

## File Structure (What to Edit)

```
configurable-dashboard-system/
│
├── backend/
│   └── queries/              ← ADD YOUR SQL QUERIES HERE
│       ├── sales.yaml        (example)
│       └── products.yaml     (your new one)
│
├── frontend/
│   └── src/
│       └── config/
│           └── dashboards/   ← ADD YOUR DASHBOARDS HERE
│               ├── sales-dashboard.json  (example)
│               └── products.json         (your new one)
│
└── start.sh                  ← RUN THIS TO START
```

## Verify Everything Works

```bash
# Run the verification script
./verify.sh
```

Should show: **"🎉 All checks passed!"**

## Troubleshooting

### Drag not working?
- Click "Edit Layout" button first
- Try refreshing the page

### Widgets not loading?
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Should return: {"status":"healthy",...}
```

### Port already in use?
```bash
# Stop everything
docker-compose down

# Start again
docker-compose up
```

### Still having issues?
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild everything
docker-compose down
docker-compose up --build
```

## What's Different from Power BI?

| Task | Power BI | This System |
|------|----------|-------------|
| **Create dashboard** | 30-60 min | 5 min |
| **Drag & drop** | GUI clicks | Edit mode + drag |
| **Version control** | ❌ | ✅ Git |
| **Cost** | $10/user/month | Free |
| **Customization** | Limited | Unlimited |

## Key Features

### GridStack Integration
- 12-column grid system
- Drag from widget header
- Resize from 5 handles (E, W, S, SE, SW)
- Auto-save to localStorage
- Smooth animations

### Widget Types
All support drag & resize:
- `metric-card` - KPI with icon
- `line-chart` - Time series
- `bar-chart` - Categories
- `pie-chart` - Proportions
- `data-table` - Sortable tables

### Smart Features
- Date shortcuts: `30_days_ago`, `today`
- Auto-caching (5 min default)
- Global filters
- Widget refresh
- Error handling per widget

## Next Steps

1. ✅ **Play with sample dashboard** - Drag and resize
2. ✅ **Create your own dashboard** - Follow 5-min guide above
3. ✅ **Read full docs** - Check `/docs` folder
4. ✅ **Deploy** - See `docs/deployment.md`

## Documentation

- **Getting Started**: `docs/getting-started.md`
- **Config Guide**: `docs/dashboard-config.md`  
- **Deployment**: `docs/deployment.md`
- **Online Platforms**: `docs/online-platforms.md`

## Support

- **Check logs**: `docker-compose logs`
- **API docs**: http://localhost:8000/docs
- **Verify setup**: `./verify.sh`

## Pro Tips

1. **Start small** - Create simple dashboards first
2. **Use samples** - Copy and modify existing configs
3. **Test queries** - Use API docs to test queries
4. **Save often** - Edit mode auto-saves, but click "Done Editing"
5. **Check console** - Browser console shows helpful errors

## Ready to Build?

```bash
./start.sh
open http://localhost:5173
# Click "Edit Layout" and have fun! 🎉
```

---

**Questions?** Check `/docs` or open the browser console (F12) for debugging!

**Happy Dashboard Building!** 🚀
