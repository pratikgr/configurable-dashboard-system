# Architecture & Design Documentation

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Vue 3 Application                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │ Dashboard  │  │  AI Chat   │  │  Widget Library  │   │  │
│  │  │  Renderer  │  │   Panel    │  │  (5 types)       │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  │         │               │                   │             │  │
│  │         └───────────────┴───────────────────┘             │  │
│  │                         │                                  │  │
│  │                    Pinia Store                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────│─────────────────────────────────────┘
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVER TIER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │    API     │  │     AI     │  │     Query        │   │  │
│  │  │  Endpoints │  │  Service   │  │   Executor       │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  │         │               │                   │             │  │
│  │         └───────────────┴───────────────────┘             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬──────────────┬───────────────────┘
                               │              │
                    ┌──────────┘              └─────────┐
                    ▼                                   ▼
         ┌──────────────────┐                ┌──────────────────┐
         │   SQLite DB      │                │  Azure OpenAI    │
         │  (Persistent)    │                │   GPT-4 API      │
         └──────────────────┘                └──────────────────┘
```

---

## Component Architecture

### Frontend Architecture (Vue 3)

```
src/
├── main.js                    # App entry, Pinia setup
├── App.vue                    # Root component
├── router/
│   └── index.js              # Route definitions
├── stores/
│   └── useDashboardStore.js  # Pinia store for dashboard & AI state
├── composables/
│   ├── useQueryExecutor.js   # API calls for queries
│   └── useAiChat.js          # SSE streaming for AI
├── components/
│   ├── Dashboard/
│   │   └── DashboardRenderer.vue  # GridStack layout manager
│   ├── Chat/
│   │   ├── ChatPanel.vue          # AI chat interface
│   │   ├── ChatMessage.vue        # Message display
│   │   ├── WidgetPreviewCard.vue  # Preview for AI widgets
│   │   └── DataPreviewCard.vue    # Preview for query results
│   └── Widgets/
│       ├── LineChartWidget.vue
│       ├── BarChartWidget.vue
│       ├── PieChartWidget.vue
│       ├── DataTableWidget.vue
│       └── MetricCardWidget.vue
├── utils/
│   ├── widgetRegistry.js     # Widget type mapping
│   └── dataTransformers.js   # Data format conversion
├── plugins/
│   └── axios.js              # Global API client
└── config/
    └── dashboards/
        └── sales-dashboard.json  # Dashboard configs
```

### Backend Architecture (FastAPI)

```
backend/
├── app/
│   ├── main.py                # FastAPI app initialization
│   ├── core/
│   │   ├── config.py          # Settings from env vars
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── query_executor.py # YAML query runner
│   │   ├── ai_service.py      # Azure OpenAI integration
│   │   └── widget_validator.py  # Widget config validation
│   ├── api/
│   │   └── endpoints/
│   │       ├── health.py      # Health checks
│   │       ├── query.py       # Query execution APIs
│   │       ├── dashboards.py  # Dashboard CRUD
│   │       └── ai.py          # AI chat endpoint
│   └── models/
│       └── database.py        # SQLAlchemy models
├── queries/
│   └── sales.yaml            # Query definitions
├── .env                      # Environment configuration
└── requirements.txt          # Python dependencies
```

---

## Data Flow Diagrams

### 1. Dashboard Loading Flow

```
User Opens Dashboard
        │
        ▼
┌──────────────────┐
│ Router Matches   │
│ Dashboard ID     │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ DashboardRenderer.vue        │
│ - loadDashboardConfig()      │
│ - Imports JSON from config/  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Initialize GridStack         │
│ - Create 12-column grid      │
│ - Mount all widgets          │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Load Each Widget Data        │
│ For each widget:             │
│   ├─ buildQueryParams()      │
│   ├─ executeQuery()          │
│   └─ transformData()         │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Render Complete Dashboard    │
└──────────────────────────────┘
```

### 2. AI Widget Creation Flow

```
User: "Add a bar chart of revenue by region"
        │
        ▼
┌──────────────────────────────┐
│ ChatPanel.vue                │
│ - sendMessage()              │
└────────┬─────────────────────┘
         │ HTTP POST
         ▼
┌──────────────────────────────┐
│ Backend: /api/ai/chat        │
│ - create_chat_stream()       │
└────────┬─────────────────────┘
         │ SSE Stream
         ▼
┌──────────────────────────────────────┐
│ AI Processes Request                 │
│ Iteration 1:                         │
│   ├─ Calls list_queries()            │
│   └─ Returns: 4 available queries    │
│                                       │
│ Iteration 2:                         │
│   ├─ Calls get_query_schema()        │
│   │   for "revenue_by_region"        │
│   └─ Returns: columns, parameters    │
│                                       │
│ Iteration 3:                         │
│   ├─ Calls create_widget()           │
│   └─ Returns: validated widget JSON  │
└────────┬──────────────────────────────┘
         │ event: widget
         │ data: {...widget config...}
         ▼
┌──────────────────────────────┐
│ useAiChat.js                 │
│ - handleWidgetEvent()        │
│ - store.setPendingWidget()  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ DashboardRenderer.vue        │
│ Watch: pendingWidget         │
│ ├─ Add to widgets array      │
│ ├─ grid.makeWidget()         │
│ ├─ Add preview styling       │
│ └─ loadWidgetData()          │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Show Save Banner             │
│ [Save Widget] [Discard]      │
└────────┬─────────────────────┘
         │ User clicks Save
         ▼
┌──────────────────────────────┐
│ POST /api/dashboard/         │
│      {id}/widget             │
│ - Saves to JSON file         │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Widget Persisted             │
│ - Remove preview styling     │
│ - Clear pending widget       │
│ - Hide save banner           │
└──────────────────────────────┘
```

### 3. Data Query Flow (AI Analyst Mode)

```
User: "Show me top 5 products from Electronics"
        │
        ▼
┌──────────────────────────────┐
│ AI Extracts Parameters       │
│ - category = "Electronics"   │
│ - limit = 5                  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Calls execute_query_preview  │
│ Tool Call:                   │
│ {                            │
│   "query_id": "top_products",│
│   "parameters": {            │
│     "category": "Electronics"│
│   }                          │
│ }                            │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Backend Query Executor       │
│ 1. Load query YAML           │
│ 2. Resolve parameters        │
│ 3. Execute SQL               │
│ 4. Return first 5 rows       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ AI Formats Response          │
│ - Describes data             │
│ - Offers to create widget    │
└────────┬─────────────────────┘
         │ event: data
         │ data: {...results...}
         ▼
┌──────────────────────────────┐
│ DataPreviewCard.vue          │
│ - Shows table (5 rows)       │
│ - "Add as Widget" button     │
└──────────────────────────────┘
```

---

## State Management (Pinia)

### Dashboard Store Schema

```typescript
interface DashboardStore {
  // UI State
  chatPanelOpen: boolean
  currentDashboard: string | null
  
  // AI State
  pendingWidget: Widget | null
  previewData: QueryResult | null
  conversationHistory: Message[]
  isGeneratingWidget: boolean
  
  // Computed
  hasPendingWidget: boolean
  hasPreviewData: boolean
  conversationLength: number
  
  // Actions
  toggleChatPanel(): void
  setCurrentDashboard(id: string): void
  setPendingWidget(widget: Widget): void
  confirmPendingWidget(): void
  clearPendingWidget(): void
  setPreviewData(data: QueryResult): void
  addMessage(message: Message): void
  clearConversation(): void
}
```

---

## API Design

### REST Endpoints

#### Health & Info
```
GET  /                    # API info
GET  /api/health         # Health check
GET  /api/ai/status      # AI service status
```

#### Queries
```
GET  /api/query/list                        # List all queries
POST /api/query/execute                     # Execute query
     Body: { query_id, parameters }
```

#### Dashboards
```
GET    /api/dashboards                      # List dashboards
GET    /api/dashboards/{id}                 # Get dashboard config
POST   /api/dashboard/{id}/widget           # Add widget
DELETE /api/dashboard/{id}/widget/{widget_id}  # Delete widget
```

#### AI Chat (SSE)
```
POST /api/ai/chat                           # Chat with AI (streaming)
     Body: { message, dashboard_id, conversation_history }
     
     Response: Server-Sent Events
     event: text       data: "chunk"
     event: widget     data: {...config...}
     event: data       data: {...results...}
     event: error      data: {...error...}
     event: done       data: ""
```

---

## Database Schema

### Tables

```sql
-- Core Tables
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    region TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    unit_price REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE NOT NULL,
    amount REAL,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

---

## Configuration Files

### Dashboard JSON Structure

```json
{
  "id": "sales-dashboard",
  "title": "Sales Dashboard",
  "description": "Real-time sales metrics",
  "globalFilters": [
    {
      "id": "date_range",
      "type": "daterange",
      "label": "Date Range",
      "default": "2025-01-01",
      "applyTo": "*"
    }
  ],
  "widgets": [
    {
      "id": "widget-001",
      "type": "bar-chart",
      "title": "Revenue by Region",
      "queryId": "revenue_by_region",
      "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "dataMapping": {
        "x": "region",
        "y": "total_revenue"
      },
      "chartOptions": {
        "colors": ["#667eea", "#764ba2"]
      }
    }
  ]
}
```

### Query YAML Structure

```yaml
queries:
  revenue_by_region:
    description: "Revenue breakdown by geographic region"
    sql: |
      SELECT 
        c.region,
        SUM(o.amount) as total_revenue
      FROM orders o
      JOIN customers c ON o.customer_id = c.customer_id
      WHERE o.order_date >= :start_date 
        AND o.status = 'completed'
      GROUP BY c.region
      ORDER BY total_revenue DESC
    parameters:
      - name: start_date
        type: date
        default: "2025-11-01"
    cache_ttl: 600
```

---

## Security Architecture

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://xxx.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Dashboard Config
DASHBOARD_CONFIG_DIR=../frontend/src/config/dashboards
```

### Security Measures

1. **SQL Injection Prevention:** Parameterized queries only
2. **CORS:** Whitelist origins via environment variable
3. **API Keys:** Stored in .env, never committed
4. **Input Validation:** Pydantic models validate all inputs
5. **Error Handling:** No sensitive data in error messages

---

## Deployment Architecture

### Development Setup

```
┌─────────────────────────────────────┐
│  Developer Machine (Windows/Mac)    │
│  ├─ Backend: uvicorn (port 8000)   │
│  ├─ Frontend: vite (port 5173)     │
│  ├─ Database: SQLite file           │
│  └─ .env: Local credentials         │
└─────────────────────────────────────┘
```

### Production Options

#### Option 1: Single Server

```
┌──────────────────────────────┐
│  Production Server           │
│  ├─ Nginx (reverse proxy)    │
│  ├─ FastAPI (Gunicorn)       │
│  ├─ Vue (static files)       │
│  └─ SQLite                   │
└──────────────────────────────┘
```

#### Option 2: Docker Compose

```
┌─────────────────────────────────────┐
│  Docker Host                         │
│  ├─ Container: backend               │
│  │   └─ FastAPI + SQLite             │
│  ├─ Container: frontend              │
│  │   └─ Nginx + Vue static           │
│  └─ Volume: /app/dashboards          │
└─────────────────────────────────────┘
```

---

## Technology Decisions

### Why These Technologies?

| Technology | Reason |
|------------|--------|
| **Vue 3** | Lightweight, excellent composition API, great ecosystem |
| **FastAPI** | Modern Python async framework, auto OpenAPI docs, type safety |
| **Pinia** | Official Vue state management, simpler than Vuex |
| **GridStack** | Mature grid system, smooth drag-and-drop |
| **ECharts** | Feature-rich, performant, extensive chart types |
| **SQLite** | Zero-config, serverless, perfect for <10k rows |
| **Azure OpenAI** | Enterprise-ready, function calling support |
| **Pydantic** | Runtime validation, automatic API docs |
| **Axios** | Promise-based, interceptors, widely adopted |

### Alternatives Considered

| Choice | Alternative | Why Not? |
|--------|-------------|----------|
| Vue 3 | React | Over-engineered for this use case |
| FastAPI | Flask | Missing async, type safety |
| GridStack | React Grid Layout | Tied to React ecosystem |
| SQLite | PostgreSQL | Overkill for single-tenant |
| Azure OpenAI | OpenAI API | Need enterprise controls |

---

## Performance Considerations

### Frontend Optimizations
- Lazy loading for widgets
- Virtual scrolling for large datasets
- Debounced resize events
- Memoized computed properties
- Component-level code splitting

### Backend Optimizations
- Async/await throughout
- Query result caching
- Connection pooling
- Streaming responses (SSE)
- Indexed database queries

### Monitoring Points
- Widget load times
- Query execution duration
- AI response latency
- Memory usage (client & server)
- Database query performance

---

## Extensibility Points

### Easy to Extend

1. **New Widget Types:** Add component to `/components/Widgets/`
2. **New Queries:** Add YAML file to `/queries/`
3. **New AI Tools:** Add function to `ai_service.py`
4. **New Dashboards:** Add JSON to `/config/dashboards/`

### Requires Modification

1. **New Database:** Update `database.py` and connection strings
2. **Different LLM:** Replace Azure OpenAI client in `ai_service.py`
3. **Authentication:** Add middleware and user model
4. **Multi-tenancy:** Add user_id to all tables

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-22  
**Next Review:** Upon architecture changes
