# API Documentation

## Base URL

**Development:** `http://localhost:8000`  
**Production:** `https://your-domain.com`

---

## Authentication

Currently **no authentication required**. All endpoints are public.

**Future:** JWT Bearer tokens will be required for all endpoints except `/health`.

---

## API Endpoints

### Health & Status

#### GET /
Get API information

**Response:**
```json
{
  "message": "Configurable Dashboard API",
  "version": "2.0.0",
  "features": [
    "Configuration-driven dashboards",
    "5 widget types (line, bar, pie, table, metric)",
    "AI-powered natural language interface",
    "Dual-mode: Dashboard builder + Data analyst"
  ],
  "docs": "/docs",
  "ai_status": "/api/ai/status"
}
```

---

#### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-22T10:30:00Z"
}
```

---

#### GET /api/ai/status
Check AI service configuration status

**Response:**
```json
{
  "status": "configured",
  "endpoint": "https://xxx.cognitiveservices.azure.com/",
  "deployment": "gpt-4.1-mini",
  "api_version": "2024-12-01-preview"
}
```

**Error Response (503):**
```json
{
  "status": "not_configured",
  "message": "Azure OpenAI credentials not configured"
}
```

---

### Query Management

#### GET /api/query/list
List all available queries

**Response:**
```json
{
  "queries": [
    {
      "id": "sales_overview",
      "description": "Get daily sales overview with revenue and order counts",
      "parameters": [
        {
          "name": "start_date",
          "type": "date",
          "required": true,
          "default": "30_days_ago"
        },
        {
          "name": "end_date",
          "type": "date",
          "required": true,
          "default": "today"
        }
      ]
    }
  ],
  "total": 4
}
```

---

#### GET /api/query/{query_id}
Get schema and metadata for a specific query

**Path Parameters:**
- `query_id` (string, required): Query identifier

**Response:**
```json
{
  "id": "revenue_by_region",
  "description": "Revenue breakdown by geographic region",
  "sql": "SELECT c.region, SUM(o.amount) as total_revenue...",
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "required": false,
      "default": "2025-11-01"
    }
  ],
  "cache_ttl": 600,
  "columns": [
    {
      "name": "region",
      "type": "TEXT"
    },
    {
      "name": "total_revenue",
      "type": "REAL"
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "Query 'invalid_query' not found"
}
```

---

#### POST /api/query/execute
Execute a query and return results

**Request Body:**
```json
{
  "query_id": "top_products",
  "parameters": {
    "start_date": "2025-11-01",
    "category": "Electronics"
  }
}
```

**Parameters:**
- `query_id` (string, required): Query identifier
- `parameters` (object, optional): Query parameters (null uses YAML defaults)

**Response:**
```json
{
  "query_id": "top_products",
  "data": [
    {
      "product_name": "Laptop Pro 15",
      "category": "Electronics",
      "total_revenue": 45000.00,
      "units_sold": 150
    }
  ],
  "columns": ["product_name", "category", "total_revenue", "units_sold"],
  "row_count": 10,
  "execution_time_ms": 24
}
```

**Error Responses:**

*404 - Query Not Found:*
```json
{
  "detail": "Query 'invalid_query' not found"
}
```

*400 - Missing Required Parameter:*
```json
{
  "detail": "Missing required parameter: start_date"
}
```

*500 - Execution Error:*
```json
{
  "detail": "Query execution failed: (error details)"
}
```

---

### Dashboard Management

#### GET /api/dashboards
List all available dashboards

**Response:**
```json
{
  "total": 1,
  "dashboards": [
    {
      "id": "sales-dashboard",
      "title": "Sales Dashboard",
      "description": "Real-time sales metrics and KPIs",
      "file": "sales-dashboard.json"
    }
  ]
}
```

---

#### GET /api/dashboards/{dashboard_id}
Get full dashboard configuration

**Path Parameters:**
- `dashboard_id` (string, required): Dashboard identifier

**Response:**
```json
{
  "id": "sales-dashboard",
  "title": "Sales Dashboard",
  "description": "Real-time sales metrics",
  "globalFilters": [...],
  "widgets": [...]
}
```

**Error Response (404):**
```json
{
  "detail": "Dashboard 'invalid-dashboard' not found"
}
```

---

#### POST /api/dashboard/{dashboard_id}/widget
Add a widget to a dashboard

**Path Parameters:**
- `dashboard_id` (string, required): Dashboard identifier

**Request Body:**
```json
{
  "id": "widget-revenue-chart",
  "type": "bar-chart",
  "title": "Revenue by Region",
  "queryId": "revenue_by_region",
  "position": {
    "x": 0,
    "y": 0,
    "w": 6,
    "h": 4
  },
  "dataMapping": {
    "x": "region",
    "y": "total_revenue"
  },
  "chartOptions": {
    "colors": ["#667eea", "#764ba2"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Widget added successfully",
  "widget_id": "widget-revenue-chart"
}
```

**Error Responses:**

*404 - Dashboard Not Found:*
```json
{
  "detail": "Dashboard 'invalid-dashboard' not found"
}
```

*500 - Save Failed:*
```json
{
  "detail": "Failed to save widget: (error details)"
}
```

---

#### DELETE /api/dashboard/{dashboard_id}/widget/{widget_id}
Delete a widget from a dashboard

**Path Parameters:**
- `dashboard_id` (string, required): Dashboard identifier
- `widget_id` (string, required): Widget identifier

**Response:**
```json
{
  "success": true,
  "message": "Widget deleted successfully"
}
```

**Error Responses:**

*404 - Dashboard Not Found:*
```json
{
  "detail": "Dashboard 'invalid-dashboard' not found"
}
```

*404 - Widget Not Found:*
```json
{
  "detail": "Widget 'invalid-widget' not found"
}
```

---

### AI Chat (Server-Sent Events)

#### POST /api/ai/chat
Chat with AI assistant using streaming SSE

**Request Body:**
```json
{
  "message": "Add a bar chart of revenue by region",
  "dashboard_id": "sales-dashboard",
  "conversation_history": [
    {
      "role": "user",
      "content": "List all queries"
    },
    {
      "role": "assistant",
      "content": "Here are the queries..."
    }
  ]
}
```

**Parameters:**
- `message` (string, required): User's message
- `dashboard_id` (string, optional): Current dashboard context
- `conversation_history` (array, optional): Previous messages

**Response Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**SSE Event Types:**

1. **text** - Streaming text response
```
event: text
data: Here are the available queries

event: text
data: :

event: text
data:  

event: text
data: 1. sales_overview
```

2. **widget** - Widget configuration (JSON)
```
event: widget
data: {"id":"widget-001","type":"bar-chart",...}
```

3. **data** - Query results (JSON)
```
event: data
data: {"data":[...],"columns":[...],"row_count":5}
```

4. **error** - Error occurred
```
event: error
data: {"error":"Failed to execute query"}
```

5. **done** - Stream complete
```
event: done
data: 
```

**Full Example Response:**
```
event: text
data: I'll create a bar chart for you.

event: text
data:  Let me fetch the data first.

event: widget
data: {"id":"widget-revenue","type":"bar-chart","title":"Revenue by Region","queryId":"revenue_by_region","position":{"x":0,"y":0,"w":6,"h":4},"dataMapping":{"x":"region","y":"total_revenue"}}

event: text
data: I've created a preview of your widget. Click Save to add it permanently.

event: done
data: 
```

**Error Response (503):**
```json
{
  "detail": "AI service not configured"
}
```

---

## AI Tools (Internal)

These are tools the AI can call during conversation. Not directly accessible via API.

### list_queries()
Returns list of available queries with descriptions

### get_query_schema(query_id: str)
Returns detailed schema for a query including columns and parameters

### execute_query_preview(query_id: str, parameters: dict)
Executes query and returns first 5 rows for preview

### create_widget(config: dict)
Validates and returns widget configuration

---

## Data Models

### Widget Configuration

```typescript
interface Widget {
  id: string                    // Unique identifier
  type: WidgetType             // "line-chart" | "bar-chart" | "pie-chart" | "data-table" | "metric-card"
  title: string                 // Display title
  queryId: string              // Query to fetch data
  position: {
    x: number                   // Grid column (0-11)
    y: number                   // Grid row
    w: number                   // Width in columns (1-12)
    h: number                   // Height in rows
  }
  dataMapping: object           // Chart-specific field mappings
  parameters?: object           // Query parameters
  chartOptions?: object         // Chart customization
  columns?: string[]            // For data-table type
}
```

### Query Result

```typescript
interface QueryResult {
  query_id: string
  data: Array<Record<string, any>>
  columns: string[]
  row_count: number
  execution_time_ms: number
  cached?: boolean
}
```

### Chat Message

```typescript
interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp?: string
  hasWidget?: boolean
  hasData?: boolean
}
```

---

## Rate Limits

**Current:** No rate limiting

**Recommended for Production:**
- `/api/query/execute`: 100 requests/minute per IP
- `/api/ai/chat`: 20 requests/minute per IP
- Other endpoints: 300 requests/minute per IP

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (query/dashboard doesn't exist) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (AI not configured) |

---

## CORS Configuration

**Allowed Origins:** Configured via `CORS_ORIGINS` environment variable

**Default (Development):**
```json
["http://localhost:5173", "http://localhost:3000"]
```

**Production Example:**
```json
["https://dashboard.example.com", "https://app.example.com"]
```

---

## Testing Endpoints

### Using cURL

**List Queries:**
```bash
curl http://localhost:8000/api/query/list
```

**Execute Query:**
```bash
curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d '{"query_id":"sales_overview","parameters":null}'
```

**AI Chat (SSE):**
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"List all queries"}' \
  --no-buffer
```

### Using Python

```python
import requests

# Execute query
response = requests.post(
    "http://localhost:8000/api/query/execute",
    json={
        "query_id": "top_products",
        "parameters": {"start_date": "2025-11-01"}
    }
)
print(response.json())

# AI Chat with SSE
response = requests.post(
    "http://localhost:8000/api/ai/chat",
    json={"message": "Show top 5 products"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### Using JavaScript (Fetch)

```javascript
// Execute query
const response = await fetch('http://localhost:8000/api/query/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query_id: 'revenue_by_region',
    parameters: null
  })
})
const data = await response.json()
console.log(data)

// AI Chat with SSE
const eventSource = new EventSource('http://localhost:8000/api/ai/chat')
eventSource.onmessage = (event) => {
  console.log('Data:', event.data)
}
```

---

## WebSocket Support

**Status:** Not implemented

**Future:** Consider WebSockets for real-time dashboard updates

---

## API Versioning

**Current:** No versioning (all endpoints at `/api/`)

**Future:** Version in URL path:
- v1: `/api/v1/query/execute`
- v2: `/api/v2/query/execute`

---

## OpenAPI Documentation

**Interactive Docs:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`  
**OpenAPI JSON:** `http://localhost:8000/openapi.json`

FastAPI automatically generates OpenAPI 3.0 documentation from code.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-22  
**API Version:** 2.0.0
