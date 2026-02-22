# Developer Guide

## Getting Started

This guide helps developers understand, modify, and extend the dashboard system.

---

## Project Structure

```
dashboard-system/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # App entry point
│   │   ├── core/              # Core business logic
│   │   │   ├── config.py      # Settings
│   │   │   ├── database.py    # DB connection
│   │   │   ├── query_executor.py  # Query engine
│   │   │   ├── ai_service.py      # AI integration
│   │   │   └── widget_validator.py  # Validation
│   │   ├── api/endpoints/     # API routes
│   │   │   ├── health.py
│   │   │   ├── query.py
│   │   │   ├── dashboards.py
│   │   │   └── ai.py
│   │   └── models/
│   │       └── database.py    # SQLAlchemy models
│   ├── queries/               # YAML query definitions
│   ├── .env                   # Environment config
│   └── requirements.txt       # Python deps
│
├── frontend/                  # Vue 3 frontend
│   ├── src/
│   │   ├── main.js           # App entry
│   │   ├── App.vue           # Root component
│   │   ├── router/           # Vue Router
│   │   ├── stores/           # Pinia stores
│   │   ├── composables/      # Reusable logic
│   │   ├── components/       # Vue components
│   │   │   ├── Dashboard/
│   │   │   ├── Chat/
│   │   │   └── Widgets/
│   │   ├── utils/            # Utilities
│   │   ├── plugins/          # Vue plugins
│   │   └── config/
│   │       └── dashboards/   # Dashboard JSONs
│   ├── package.json
│   └── vite.config.js
│
└── docs/                     # This documentation
```

---

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone repo
git clone https://github.com/your-org/dashboard-system.git
cd dashboard-system

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Azure credentials

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env

# Start both servers
# Terminal 1 (backend):
uvicorn app.main:app --reload

# Terminal 2 (frontend):
npm run dev
```

### 2. Making Changes

**Always:**
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test locally
4. Commit with clear message
5. Push and create PR

### 3. Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm run test
```

### 4. Code Quality

**Backend (Python):**
```bash
# Format with black
black app/

# Lint with flake8
flake8 app/

# Type check with mypy
mypy app/
```

**Frontend (JavaScript):**
```bash
# Lint
npm run lint

# Format
npm run format
```

---

## Adding New Features

### Add a New Widget Type

#### 1. Create Widget Component

**`frontend/src/components/Widgets/CustomWidget.vue`:**
```vue
<template>
  <div class="custom-widget">
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else>
      <!-- Your widget UI here -->
      <h3>{{ config.title }}</h3>
      <div>{{ data }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  config: { type: Object, required: true },
  data: { type: [Object, Array], default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null }
})
</script>

<style scoped>
.custom-widget {
  padding: 1rem;
}
</style>
```

#### 2. Register Widget

**`frontend/src/utils/widgetRegistry.js`:**
```javascript
import CustomWidget from '@/components/Widgets/CustomWidget.vue'

const widgetComponents = {
  'line-chart': LineChartWidget,
  'bar-chart': BarChartWidget,
  'pie-chart': PieChartWidget,
  'data-table': DataTableWidget,
  'metric-card': MetricCardWidget,
  'custom-widget': CustomWidget,  // Add here
}

export function getWidgetComponent(type) {
  return widgetComponents[type] || null
}
```

#### 3. Update AI Tool

**`backend/app/core/ai_service.py`:**

Add to `create_widget` tool description:
```python
- custom-widget: needs {displayField: field}
```

#### 4. Test

```javascript
// In dashboard JSON
{
  "id": "widget-custom",
  "type": "custom-widget",
  "title": "My Custom Widget",
  "queryId": "some_query",
  "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
  "dataMapping": {
    "displayField": "column_name"
  }
}
```

---

### Add a New Query

#### 1. Create YAML File

**`backend/queries/custom.yaml`:**
```yaml
queries:
  my_new_query:
    description: "Get custom data with filters"
    sql: |
      SELECT 
        id,
        name,
        value,
        created_at
      FROM custom_table
      WHERE status = :status
        AND created_at >= :start_date
      ORDER BY value DESC
      LIMIT :limit
    parameters:
      - name: status
        type: string
        default: "active"
      - name: start_date
        type: date
        default: "30_days_ago"
      - name: limit
        type: int
        default: 100
    cache_ttl: 300
```

#### 2. Test Query

```python
# In Python shell
from app.core.query_executor import query_executor
import asyncio

async def test():
    result = await query_executor.execute_query(
        "my_new_query",
        {"status": "active", "start_date": "2025-01-01"}
    )
    print(result)

asyncio.run(test())
```

#### 3. Use in Dashboard

AI will automatically discover new queries via `list_queries()` tool.

---

### Add a New AI Tool

#### 1. Define Tool Function

**`backend/app/core/ai_service.py`:**

```python
async def get_customer_details(customer_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a customer
    
    Args:
        customer_id: Customer ID to look up
        
    Returns:
        Customer details with order history
    """
    async with get_db_session() as db:
        # Query customer
        result = await db.execute(
            text("SELECT * FROM customers WHERE customer_id = :id"),
            {"id": customer_id}
        )
        customer = result.mappings().first()
        
        if not customer:
            return {"error": "Customer not found"}
        
        # Query orders
        result = await db.execute(
            text("""
                SELECT COUNT(*) as order_count, SUM(amount) as total_spent
                FROM orders WHERE customer_id = :id
            """),
            {"id": customer_id}
        )
        stats = result.mappings().first()
        
        return {
            "customer": dict(customer),
            "stats": dict(stats)
        }
```

#### 2. Add to Tools List

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": "Get detailed customer information including order history",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID to look up"
                    }
                },
                "required": ["customer_id"]
            }
        }
    },
    # ... other tools
]
```

#### 3. Handle Tool Call

```python
# In execute_tool_call function
if tool_name == "get_customer_details":
    args = json.loads(tool_call.function.arguments)
    result = await get_customer_details(args["customer_id"])
    return json.dumps(result)
```

#### 4. Update System Prompt

Add tool description so AI knows when to use it.

---

### Add Authentication

#### 1. Create User Model

**`backend/app/models/database.py`:**
```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 2. Add Auth Dependencies

**`backend/app/core/auth.py`:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 3. Protect Endpoints

```python
from app.core.auth import get_current_user

@router.get("/api/query/list")
async def list_queries(current_user: dict = Depends(get_current_user)):
    # Only authenticated users can access
    ...
```

#### 4. Frontend Login

**`frontend/src/stores/useAuthStore.js`:**
```javascript
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    user: null
  }),
  
  actions: {
    async login(email, password) {
      const response = await axios.post('/api/auth/login', { email, password })
      this.token = response.data.token
      localStorage.setItem('token', this.token)
    },
    
    logout() {
      this.token = null
      localStorage.removeItem('token')
    }
  }
})
```

---

## Code Style Guide

### Python (Backend)

**Follow PEP 8:**
```python
# Good
async def get_query_schema(query_id: str) -> Dict[str, Any]:
    """Get detailed schema for a query."""
    query_config = query_executor.get_query_config(query_id)
    return {
        "id": query_id,
        "description": query_config.get("description"),
        "parameters": query_config.get("parameters", [])
    }

# Bad
async def getQuerySchema(queryId):
    queryConfig=query_executor.get_query_config(queryId)
    return {"id":queryId,"description":queryConfig.get("description")}
```

**Docstrings:**
```python
def execute_query(query_id: str, params: dict) -> dict:
    """
    Execute a database query with parameters.
    
    Args:
        query_id: Query identifier from YAML
        params: Query parameters (uses defaults if None)
        
    Returns:
        Dictionary with query results and metadata
        
    Raises:
        ValueError: If query not found
        QueryExecutionError: If query fails
    """
    pass
```

### JavaScript (Frontend)

**Use Composition API:**
```javascript
// Good
<script setup>
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)

onMounted(() => {
  console.log('Component mounted')
})
</script>

// Avoid Options API for new components
```

**Naming Conventions:**
```javascript
// Components: PascalCase
import ChatPanel from '@/components/Chat/ChatPanel.vue'

// Composables: camelCase starting with 'use'
import { useQueryExecutor } from '@/composables/useQueryExecutor'

// Constants: SCREAMING_SNAKE_CASE
const API_BASE_URL = 'http://localhost:8000'

// Variables: camelCase
const widgetData = ref(null)
```

**Async/Await:**
```javascript
// Good
async function loadData() {
  try {
    const result = await executeQuery('sales_overview')
    data.value = result.data
  } catch (error) {
    console.error('Failed to load:', error)
  }
}

// Avoid .then() chains for new code
```

---

## Debugging

### Backend Debugging

**Add Logging:**
```python
import logging

logger = logging.getLogger(__name__)

async def some_function():
    logger.info("Starting function")
    logger.debug(f"Parameters: {params}")
    try:
        result = await do_something()
        logger.info("Function completed successfully")
        return result
    except Exception as e:
        logger.error(f"Function failed: {e}", exc_info=True)
        raise
```

**VS Code Debug Config:**

**`.vscode/launch.json`:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

Set breakpoints and press F5.

### Frontend Debugging

**Vue DevTools:**
1. Install Vue DevTools browser extension
2. Open browser DevTools (F12)
3. Click "Vue" tab
4. Inspect components, stores, router

**Console Logging:**
```javascript
console.log('Data loaded:', data.value)
console.table(results)  // Nice table format
console.group('API Call')
console.log('URL:', url)
console.log('Params:', params)
console.groupEnd()
```

**Network Tab:**
- Watch API calls
- Check request/response
- Verify SSE streams

---

## Testing

### Backend Tests

**`backend/tests/test_query_executor.py`:**
```python
import pytest
from app.core.query_executor import QueryExecutor

@pytest.fixture
async def query_executor():
    executor = QueryExecutor()
    yield executor

@pytest.mark.asyncio
async def test_list_queries(query_executor):
    queries = await query_executor.list_queries()
    assert len(queries) > 0
    assert "sales_overview" in [q["id"] for q in queries]

@pytest.mark.asyncio
async def test_execute_query(query_executor):
    result = await query_executor.execute_query(
        "simple_test",
        None
    )
    assert "data" in result
    assert "columns" in result
    assert len(result["data"]) > 0
```

**Run Tests:**
```bash
pytest tests/ -v --cov=app
```

### Frontend Tests

**`frontend/src/components/__tests__/ChatPanel.spec.js`:**
```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatPanel from '@/components/Chat/ChatPanel.vue'

describe('ChatPanel', () => {
  it('renders properly', () => {
    const wrapper = mount(ChatPanel)
    expect(wrapper.find('.chat-panel').exists()).toBe(true)
  })
  
  it('opens when FAB is clicked', async () => {
    const wrapper = mount(ChatPanel)
    await wrapper.find('.ai-fab').trigger('click')
    expect(wrapper.vm.isOpen).toBe(true)
  })
})
```

**Run Tests:**
```bash
npm run test
```

---

## Performance Best Practices

### Backend

**1. Use Async Everywhere:**
```python
# Good
async def get_data():
    async with get_db_session() as db:
        result = await db.execute(query)
        return result.all()

# Bad (blocks event loop)
def get_data():
    conn = sqlite3.connect('db.db')
    return conn.execute(query).fetchall()
```

**2. Cache Expensive Operations:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_query_config(query_id: str):
    # Expensive YAML parsing
    return parse_yaml(f"queries/{query_id}.yaml")
```

**3. Limit Query Results:**
```sql
-- Always use LIMIT for preview queries
SELECT * FROM large_table
ORDER BY created_at DESC
LIMIT 100
```

### Frontend

**1. Lazy Load Components:**
```javascript
// Good
const ChatPanel = defineAsyncComponent(() =>
  import('@/components/Chat/ChatPanel.vue')
)

// Loads component only when needed
```

**2. Debounce Expensive Operations:**
```javascript
import { debounce } from 'lodash-es'

const searchQuery = ref('')
const debouncedSearch = debounce(async () => {
  results.value = await search(searchQuery.value)
}, 300)

watch(searchQuery, debouncedSearch)
```

**3. Virtual Scrolling for Large Lists:**
```vue
<script setup>
import { useVirtualList } from '@vueuse/core'

const { list, containerProps, wrapperProps } = useVirtualList(
  items,
  { itemHeight: 50 }
)
</script>

<template>
  <div v-bind="containerProps">
    <div v-bind="wrapperProps">
      <div v-for="item in list" :key="item.index">
        {{ item.data }}
      </div>
    </div>
  </div>
</template>
```

---

## Common Patterns

### Error Handling

**Backend:**
```python
from fastapi import HTTPException

@router.get("/api/data")
async def get_data(id: int):
    try:
        data = await fetch_data(id)
        if not data:
            raise HTTPException(status_code=404, detail="Data not found")
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Frontend:**
```javascript
async function loadData() {
  loading.value = true
  error.value = null
  
  try {
    const result = await api.getData()
    data.value = result
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load data'
    console.error('Load error:', err)
  } finally {
    loading.value = false
  }
}
```

### Loading States

```vue
<template>
  <div>
    <div v-if="loading" class="spinner">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="!data" class="empty">No data available</div>
    <div v-else>
      <!-- Show data -->
    </div>
  </div>
</template>
```

---

## Useful Commands

### Backend
```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/

# Run tests
pytest

# Generate requirements
pip freeze > requirements.txt

# Check unused deps
pip-autoremove
```

### Frontend
```bash
# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Fix lint issues
npm run lint -- --fix

# Check bundle size
npm run build -- --report
```

---

## Resources

### Documentation
- **FastAPI:** https://fastapi.tiangolo.com/
- **Vue 3:** https://vuejs.org/
- **Pinia:** https://pinia.vuejs.org/
- **ECharts:** https://echarts.apache.org/
- **GridStack:** https://gridstackjs.com/

### Tools
- **VS Code Extensions:**
  - Python
  - Pylance
  - Vetur (Vue)
  - ESLint
  - Prettier

### Community
- **GitHub Discussions:** (your repo)
- **Stack Overflow:** Tag questions with `fastapi`, `vue3`

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-22  
**Maintained By:** Development Team
