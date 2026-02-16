# Configurable Dashboard System - SQLite Version

**Branch: `sqlite`**

This branch uses SQLite instead of PostgreSQL for simpler setup and deployment.

## 🆕 What's Different (SQLite Branch)

### ✅ **Simplified Setup**
- ✅ No PostgreSQL server needed
- ✅ Single database file (`backend/dashboard.db`)
- ✅ Works natively on Windows
- ✅ No Docker required for development
- ✅ Easier backup (just copy the .db file)

### 🔄 **Technical Changes**
- Database: PostgreSQL → SQLite
- Driver: `asyncpg` → `aiosqlite`
- SQL syntax updated for SQLite compatibility
- Docker Compose simplified (no DB service)

## 🚀 **Quick Start**

### **Windows (Native)**
```cmd
# 1. Clone this branch
git clone -b sqlite https://github.com/pratikgr/configurable-dashboard-system.git
cd configurable-dashboard-system

# 2. Run setup
setup.bat

# 3. Start application
start.bat

# 4. Open browser
http://localhost:5173
```

### **Linux/Mac**
```bash
# Backend
cd backend
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### **Docker**
```bash
docker-compose up
```

## 📊 **Features (All Working)**

- ✅ **Drag & Drop** - GridStack integration
- ✅ **Resize Widgets** - From all edges/corners
- ✅ **5 Widget Types** - Line, Bar, Pie, Table, Metrics
- ✅ **Global Filters** - Date range and dropdowns
- ✅ **Auto-Save Layouts** - To localStorage
- ✅ **Sample Dashboard** - With real data
- ✅ **Configuration-Driven** - JSON + YAML only

## 🗄️ **Database**

SQLite creates a single file:
```
backend/dashboard.db
```

**Initialize/Reset:**
```bash
cd backend
python init_db.py
```

**Backup:**
```bash
cp backend/dashboard.db backup.db
```

## 📝 **Environment Variables**

### **Backend (.env)**
```bash
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
```

### **Frontend (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🔄 **Switching Between Branches**

### **To PostgreSQL (main branch):**
```bash
git checkout main
cd backend
pip install -r requirements.txt
# Setup PostgreSQL...
```

### **To SQLite (this branch):**
```bash
git checkout sqlite
cd backend
pip install -r requirements.txt
python init_db.py
```

## 📦 **Dependencies**

### **Backend**
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- **aiosqlite 0.19.0** ← SQLite driver
- Pydantic 2.5.3
- PyYAML 6.0.1

### **Frontend**
- Vue 3.4.15
- GridStack 10.1.2
- ECharts 5.4.3
- Tailwind CSS 3.4.1

## 📚 **Documentation**

All documentation from main branch applies, except:
- No PostgreSQL setup needed
- Use `init_db.py` instead of `init.sql`
- Database is single file instead of server

## 🐛 **Troubleshooting**

### **Database locked**
```bash
# Close all connections and restart
rm backend/dashboard.db
python backend/init_db.py
```

### **Module not found: aiosqlite**
```bash
pip install aiosqlite
```

### **No such table**
```bash
python backend/init_db.py
```

## 🎯 **When to Use This Branch**

### **Use SQLite (this branch) if:**
- ✅ Development/testing
- ✅ Small to medium datasets (< 1M rows)
- ✅ Single server deployment
- ✅ Windows development environment
- ✅ Simple backup needs

### **Use PostgreSQL (main branch) if:**
- ⚠️ Production with high traffic
- ⚠️ Large datasets (> 1M rows)
- ⚠️ Multiple concurrent users
- ⚠️ Need advanced features
- ⚠️ Horizontal scaling

## 🔍 **SQL Differences**

### **Date Functions**
```sql
-- PostgreSQL (main):
DATE_TRUNC('month', order_date)
CURRENT_DATE - INTERVAL '30 days'

-- SQLite (this branch):
STRFTIME('%Y-%m', order_date)
DATE('now', '-30 days')
```

### **Data Types**
```sql
-- PostgreSQL:
customer_id SERIAL PRIMARY KEY
amount DECIMAL(10,2)
name VARCHAR(200)

-- SQLite:
customer_id INTEGER PRIMARY KEY AUTOINCREMENT
amount REAL
name TEXT
```

## 📈 **Performance**

| Metric | PostgreSQL | SQLite |
|--------|-----------|--------|
| **Setup Time** | 5-10 min | 2 min |
| **Query Speed** | Excellent | Good |
| **Concurrent Writes** | High | Medium |
| **File Size** | Multiple | Single |
| **Backup** | pg_dump | Copy file |

## 🤝 **Contributing**

When contributing to this branch:
1. Keep SQL queries SQLite-compatible
2. Test with `backend/dashboard.db`
3. Don't use PostgreSQL-specific features
4. Update documentation if needed

## 📄 **License**

MIT License (same as main branch)

---

**Ready to go!** This branch is production-ready for small to medium deployments. 🚀
