# Dashboard Configuration Guide

## Overview

This guide explains how to create a new dashboard using only configuration files. No code changes required!

## Quick Start: Create a Dashboard in 5 Minutes

### Step 1: Define SQL Queries (2 minutes)

Create a YAML file in `backend/queries/`:

```yaml
# backend/queries/my_dashboard.yaml
queries:
  my_data:
    description: "Description of what this query does"
    sql: |
      SELECT 
        column1,
        column2,
        SUM(column3) as total
      FROM my_table
      WHERE date >= :start_date
      GROUP BY column1, column2
    parameters:
      - name: start_date
        type: date
        default: "30_days_ago"
    cache_ttl: 300
```

### Step 2: Create Dashboard Config (3 minutes)

Create a JSON file in `frontend/src/config/dashboards/`:

```json
{
  "id": "my-dashboard",
  "title": "My Dashboard",
  "description": "Dashboard description",
  
  "globalFilters": [
    {
      "id": "start_date",
      "type": "daterange",
      "label": "Start Date",
      "default": "2024-01-01",
      "applyTo": "*"
    }
  ],
  
  "widgets": [
    {
      "id": "metric1",
      "type": "metric-card",
      "position": { "x": 0, "y": 0, "w": 3, "h": 2 },
      "title": "Total Revenue",
      "queryId": "my_data",
      "dataMapping": {
        "value": "SUM(total)"
      },
      "format": {
        "type": "currency",
        "currency": "USD"
      }
    }
  ]
}
```

### Step 3: Access Your Dashboard

Navigate to: `http://localhost:5173/dashboard/my-dashboard`

Done! 🎉

## Configuration Reference

### Query Configuration (YAML)

```yaml
queries:
  query_id:
    description: "Human-readable description"
    sql: |
      Your SQL query here
      Can span multiple lines
      Use :parameter_name for parameters
    parameters:
      - name: parameter_name
        type: date|int|float|string|bool
        default: default_value
        description: "Parameter description"
    cache_ttl: 300  # Cache duration in seconds
```

#### Smart Date Defaults

Use these built-in date shortcuts:
- `today`
- `yesterday`
- `7_days_ago`
- `30_days_ago`
- `90_days_ago`
- `365_days_ago`
- `start_of_month`
- `start_of_year`

### Dashboard Configuration (JSON)

#### Global Filters

```json
{
  "globalFilters": [
    {
      "id": "filter_id",
      "type": "daterange|dropdown",
      "label": "Display Label",
      "default": "default_value",
      "applyTo": "*",  // or ["widget1", "widget2"]
      "options": ["option1", "option2"]  // For dropdown
    }
  ]
}
```

#### Widget Types

##### 1. Metric Card

```json
{
  "type": "metric-card",
  "queryId": "query_id",
  "dataMapping": {
    "value": "SUM(field_name)"  // or field_name for direct value
  },
  "format": {
    "type": "currency|number|percent",
    "currency": "USD",
    "decimals": 2
  },
  "icon": "users|chart|dollar",
  "color": "blue|green|red|yellow|purple"
}
```

##### 2. Line Chart

```json
{
  "type": "line-chart",
  "queryId": "query_id",
  "dataMapping": {
    "x": "date_field",
    "y": "value_field",
    "series": "category_field"  // Optional for multiple lines
  },
  "chartOptions": {
    "smooth": true,
    "showArea": true,
    "colors": ["#3b82f6", "#10b981"],
    "yAxis": {
      "format": "currency"
    }
  }
}
```

##### 3. Bar Chart

```json
{
  "type": "bar-chart",
  "queryId": "query_id",
  "dataMapping": {
    "x": "category_field",
    "y": "value_field"
  },
  "chartOptions": {
    "colors": ["#10b981"]
  }
}
```

##### 4. Pie Chart

```json
{
  "type": "pie-chart",
  "queryId": "query_id",
  "dataMapping": {
    "name": "category_field",
    "value": "value_field"
  }
}
```

##### 5. Data Table

```json
{
  "type": "data-table",
  "queryId": "query_id",
  "columns": [
    {
      "field": "column_name",
      "header": "Display Name",
      "sortable": true,
      "align": "left|right",
      "format": {
        "type": "currency|number|date|percent"
      }
    }
  ],
  "options": {
    "pageSize": 20,
    "exportable": true
  }
}
```

#### Widget Positioning

```json
{
  "position": {
    "x": 0,     // Column position (0-11)
    "y": 0,     // Row position
    "w": 6,     // Width in columns (1-12)
    "h": 4      // Height in rows
  }
}
```

## Best Practices

### 1. Query Design

- **Keep queries focused**: One query per data need
- **Use parameters**: Make queries reusable with parameters
- **Add descriptions**: Document what each query does
- **Set appropriate cache**: Balance freshness vs performance

### 2. Dashboard Layout

- **Start with metrics**: Put key metrics at the top
- **Group related widgets**: Keep related data together
- **Use consistent sizing**: Maintain visual harmony
- **Leave whitespace**: Don't overcrowd the dashboard

### 3. Performance

- **Limit data volume**: Use LIMIT in queries where appropriate
- **Index your queries**: Ensure database tables are indexed
- **Cache strategically**: Set longer cache for stable data
- **Paginate tables**: Use pageSize option for large tables

## Examples

### Example 1: Customer Dashboard

```yaml
# queries/customers.yaml
queries:
  customer_metrics:
    sql: |
      SELECT 
        COUNT(*) as total_customers,
        COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as new_customers
      FROM customers
```

```json
{
  "id": "customers",
  "title": "Customer Analytics",
  "widgets": [
    {
      "id": "total",
      "type": "metric-card",
      "position": { "x": 0, "y": 0, "w": 6, "h": 2 },
      "title": "Total Customers",
      "queryId": "customer_metrics",
      "dataMapping": { "value": "total_customers" }
    }
  ]
}
```

### Example 2: Financial Dashboard

See `frontend/src/config/dashboards/sales-dashboard.json` for a complete example.

## Troubleshooting

### Dashboard Not Loading

1. Check console for errors
2. Verify dashboard ID matches filename (without .json)
3. Ensure JSON is valid

### Query Not Executing

1. Check backend logs: `docker-compose logs backend`
2. Verify query ID in YAML matches config
3. Test SQL directly in database
4. Check parameter types match

### Widget Shows No Data

1. Verify query returns data
2. Check dataMapping configuration
3. Ensure column names match query results
4. Look for JavaScript errors in console

## Advanced Features

### Conditional Formatting

Coming soon...

### Custom Widgets

Coming soon...

### Real-time Updates

Add to widget config:
```json
{
  "refreshInterval": 30000  // Refresh every 30 seconds
}
```

## Need Help?

- Check API documentation: http://localhost:8000/docs
- Review sample dashboards in `/config/dashboards`
- Check backend logs for query errors
