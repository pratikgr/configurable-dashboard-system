# Configuration-Only Dashboard System

## 🎯 Your Goal: ZERO Code Changes

**Add dashboards = Add 2 config files**
**Change chart types = Change 1 line in JSON**

---

## 📋 Answer to Your Questions

### **1. Yes, PieChart needs same fix**

✅ Fixed PieChart.vue included in package

### **2. Top Products Query Issue**

Problem: `order_items` table was empty in SQLite
✅ Fixed init_sqlite.sql - properly generates order_items

### **3. Universal Chart Type Conversion**

✅ Enhanced dataTransformers.js - converts ANY chart to ANY chart via config only!

---

## 🚀 How to Add New Dashboard (5 Minutes - No Code!)

### **Step 1: Create Query (2 min)**

Assume there are data and tables exist.
Example to load sample data:

# Initialize main database

python -c "import sqlite3; conn = sqlite3.connect('backend/dashboard.db'); conn.executescript(open('backend/init_sqlite.sql').read()); conn.commit(); conn.close(); print('✅ Main DB initialized!')"

# Add customer analytics

python -c "import sqlite3; conn = sqlite3.connect('backend/dashboard.db'); conn.executescript(open('customer_analytics_data.sql').read()); conn.commit(); conn.close(); print('✅ Customer analytics added!')"

File: `backend/queries/inventory.yaml`

```yaml
queries:
  stock_levels:
    sql: |
      SELECT 
        product_name as name,
        quantity as value,
        category
      FROM inventory
      WHERE quantity > 0
      ORDER BY quantity DESC
      LIMIT 20
    parameters: []
```

### **Step 2: Create Dashboard Config (3 min)**

File: `frontend/src/config/dashboards/inventory.json`

```json
{
  "id": "inventory",
  "title": "Inventory Dashboard",
  "widgets": [
    {
      "id": "stock_pie",
      "type": "pie-chart",
      "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "title": "Stock by Product",
      "queryId": "stock_levels",
      "dataMapping": {
        "name": "name",
        "value": "value"
      }
    }
  ]
}
```

### **Step 3: Access**

Navigate to: `http://localhost:5173/dashboard/inventory`

**Done! No code changes!** 🎉

---

## 🔄 Change Chart Types - Config Only!

### **Example: Same Query, 4 Different Visualizations**

Query returns:

```sql
SELECT region, revenue FROM sales
```

### **As Pie Chart:**

```json
{
  "type": "pie-chart",
  "dataMapping": {
    "name": "region",
    "value": "revenue"
  }
}
```

### **As Bar Chart:**

```json
{
  "type": "bar-chart",
  "dataMapping": {
    "x": "region",
    "y": "revenue"
  }
}
```

### **As Line Chart:**

```json
{
  "type": "line-chart",
  "dataMapping": {
    "x": "region",
    "y": "revenue"
  }
}
```

### **As Data Table:**

```json
{
  "type": "data-table",
  "columns": [
    { "field": "region", "header": "Region" },
    {
      "field": "revenue",
      "header": "Revenue",
      "format": { "type": "currency" }
    }
  ]
}
```

**Just change the `type` and `dataMapping` - no code changes!**

---

## 🎨 All Supported Widget Types

### **1. line-chart**

```json
{
  "type": "line-chart",
  "dataMapping": {
    "x": "date",
    "y": "value"
  },
  "chartOptions": {
    "smooth": true,
    "showArea": true,
    "colors": ["#3b82f6"]
  }
}
```

### **2. bar-chart**

```json
{
  "type": "bar-chart",
  "dataMapping": {
    "x": "category",
    "y": "value"
  },
  "chartOptions": {
    "colors": ["#10b981"]
  }
}
```

### **3. pie-chart**

```json
{
  "type": "pie-chart",
  "dataMapping": {
    "name": "category",
    "value": "amount"
  }
}
```

### **4. data-table**

```json
{
  "type": "data-table",
  "columns": [
    { "field": "name", "header": "Name", "sortable": true },
    { "field": "value", "header": "Value", "format": { "type": "number" } }
  ],
  "options": {
    "pageSize": 20
  }
}
```

### **5. metric-card**

```json
{
  "type": "metric-card",
  "dataMapping": {
    "value": "SUM(revenue)"
  },
  "format": {
    "type": "currency"
  },
  "icon": "dollar",
  "color": "green"
}
```

---

## 🔄 Universal Data Transformation

The system automatically converts between formats:

### **Table → Chart**

```json
// Query returns: [{product: "A", sales: 100}, {product: "B", sales: 200}]

// As Table:
{"type": "data-table", "columns": ["product", "sales"]}

// As Bar Chart (NO CODE CHANGE):
{"type": "bar-chart", "dataMapping": {"x": "product", "y": "sales"}}
```

### **Chart → Pie**

```json
// Same query data

// As Bar:
{"type": "bar-chart", "dataMapping": {"x": "product", "y": "sales"}}

// As Pie (NO CODE CHANGE):
{"type": "pie-chart", "dataMapping": {"name": "product", "value": "sales"}}
```

### **Pie → Table**

```json
// Same query data

// As Pie:
{"type": "pie-chart", "dataMapping": {"name": "product", "value": "sales"}}

// As Table (NO CODE CHANGE):
{"type": "data-table", "columns": [
  {"field": "product", "header": "Product"},
  {"field": "sales", "header": "Sales"}
]}
```

---

## 📊 Real Example: Revenue Dashboard 3 Ways

### **Query (One Query for All):**

```yaml
queries:
  revenue_by_category:
    sql: |
      SELECT category, SUM(amount) as revenue
      FROM sales
      GROUP BY category
```

### **Version 1: Bar Chart**

```json
{
  "id": "revenue-bars",
  "type": "bar-chart",
  "queryId": "revenue_by_category",
  "dataMapping": { "x": "category", "y": "revenue" }
}
```

### **Version 2: Pie Chart**

```json
{
  "id": "revenue-pie",
  "type": "pie-chart",
  "queryId": "revenue_by_category",
  "dataMapping": { "name": "category", "value": "revenue" }
}
```

### **Version 3: Table**

```json
{
  "id": "revenue-table",
  "type": "data-table",
  "queryId": "revenue_by_category",
  "columns": [
    { "field": "category", "header": "Category" },
    {
      "field": "revenue",
      "header": "Revenue",
      "format": { "type": "currency" }
    }
  ]
}
```

**Same query, 3 different visualizations, ZERO code changes!**

---

## 🎯 Complete Dashboard Example

File: `frontend/src/config/dashboards/sales-multi.json`

```json
{
  "id": "sales-multi",
  "title": "Sales Dashboard - Multiple Views",
  "globalFilters": [
    {
      "id": "start_date",
      "type": "daterange",
      "label": "Start Date",
      "default": "2024-01-01"
    }
  ],
  "widgets": [
    {
      "id": "total_revenue",
      "type": "metric-card",
      "position": { "x": 0, "y": 0, "w": 3, "h": 2 },
      "title": "Total Revenue",
      "queryId": "sales_overview",
      "dataMapping": { "value": "SUM(total_revenue)" },
      "format": { "type": "currency" },
      "icon": "dollar",
      "color": "green"
    },
    {
      "id": "revenue_line",
      "type": "line-chart",
      "position": { "x": 0, "y": 2, "w": 6, "h": 4 },
      "title": "Revenue Trend",
      "queryId": "sales_overview",
      "dataMapping": { "x": "date", "y": "total_revenue" }
    },
    {
      "id": "revenue_pie",
      "type": "pie-chart",
      "position": { "x": 6, "y": 2, "w": 6, "h": 4 },
      "title": "Revenue by Region",
      "queryId": "revenue_by_region",
      "dataMapping": { "name": "region", "value": "total_revenue" }
    },
    {
      "id": "products_table",
      "type": "data-table",
      "position": { "x": 0, "y": 6, "w": 12, "h": 4 },
      "title": "Products",
      "queryId": "top_products",
      "columns": [
        { "field": "product_name", "header": "Product" },
        { "field": "category", "header": "Category" },
        { "field": "units_sold", "header": "Units" },
        {
          "field": "total_revenue",
          "header": "Revenue",
          "format": { "type": "currency" }
        }
      ]
    }
  ]
}
```

---

## 🔧 Format Options (Config Only!)

### **Currency:**

```json
{ "format": { "type": "currency", "currency": "USD" } }
```

### **Number:**

```json
{ "format": { "type": "number", "decimals": 2 } }
```

### **Percent:**

```json
{ "format": { "type": "percent", "decimals": 1 } }
```

### **Date:**

```json
{ "format": { "type": "date" } }
```

### **Compact:**

```json
{ "format": { "type": "compact" } } // 1000 → 1K, 1000000 → 1M
```

---

## 🎨 Chart Styling (Config Only!)

### **Colors:**

```json
{
  "chartOptions": {
    "colors": ["#3b82f6", "#10b981", "#f59e0b"]
  }
}
```

### **Line Chart Options:**

```json
{
  "chartOptions": {
    "smooth": true,
    "showArea": true,
    "colors": ["#3b82f6"]
  }
}
```

### **Y-Axis Format:**

```json
{
  "chartOptions": {
    "yAxis": { "format": "currency" }
  }
}
```

---

## 📐 Widget Positioning (Config Only!)

### **Grid System (12 columns):**

```json
{
  "position": {
    "x": 0, // Column (0-11)
    "y": 0, // Row
    "w": 6, // Width (1-12 columns)
    "h": 4 // Height (in rows)
  }
}
```

### **Common Layouts:**

**Full Width:**

```json
{ "x": 0, "y": 0, "w": 12, "h": 4 }
```

**Half Width:**

```json
{ "x": 0, "y": 0, "w": 6, "h": 4 }
```

**Quarter Width:**

```json
{ "x": 0, "y": 0, "w": 3, "h": 2 }
```

---

## 🔍 Query Examples

### **Simple Query:**

```yaml
queries:
  users:
    sql: "SELECT * FROM users"
```

### **With Parameters:**

```yaml
queries:
  filtered_users:
    sql: |
      SELECT * FROM users
      WHERE created_at >= :start_date
    parameters:
      - name: start_date
        type: date
        default: "30_days_ago"
```

### **Aggregated:**

```yaml
queries:
  summary:
    sql: |
      SELECT 
        category,
        COUNT(*) as count,
        SUM(amount) as total
      FROM transactions
      GROUP BY category
```

---

## ✅ Checklist: Adding New Dashboard

- [ ] Create query YAML in `backend/queries/`
- [ ] Create dashboard JSON in `frontend/src/config/dashboards/`
- [ ] Choose widget types (line-chart, bar-chart, pie-chart, data-table, metric-card)
- [ ] Define dataMapping for each widget
- [ ] Set position for each widget
- [ ] Add any formatting options
- [ ] Navigate to `/dashboard/{your-dashboard-id}`

**NO CODE CHANGES NEEDED!**

---

## 🎯 Summary

### **What You Can Do With Config Only:**

✅ Add unlimited dashboards
✅ Change any chart to any other chart type
✅ Add/remove widgets
✅ Change colors and styling
✅ Modify layouts (drag/drop in UI)
✅ Add filters
✅ Format numbers/dates/currency
✅ Sort/paginate tables

### **What Requires Code Changes:**

❌ Adding NEW widget types (beyond the 5 provided)
❌ Adding NEW data transformations
❌ Changing core GridStack behavior
❌ Modifying backend query executor

### **The 5 Universal Widgets Cover Everything:**

1. **metric-card** - KPIs
2. **line-chart** - Trends over time
3. **bar-chart** - Category comparisons
4. **pie-chart** - Proportions
5. **data-table** - Detailed data

**These 5 widgets + config = Unlimited dashboards!**

---

## 📚 Next Steps

1. **Fix current issues**: Apply the 5 files from package
2. **Test configuration changes**: Change a bar to pie chart
3. **Create new dashboard**: Use examples above
4. **Experiment**: Try different chart types with same query

---

**Remember: NEVER touch the code - just edit YAML and JSON!** 🎉
