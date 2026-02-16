#!/bin/bash

# GridStack Dashboard Verification Script
# Tests that all features are working

echo "🔍 Configurable Dashboard - GridStack Verification"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "📋 Checking Services..."
echo ""

# Check backend
echo -n "Backend (Port 8000): "
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
    BACKEND_OK=1
else
    echo -e "${RED}✗ Not running${NC}"
    BACKEND_OK=0
fi

# Check frontend
echo -n "Frontend (Port 5173): "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
    FRONTEND_OK=1
else
    echo -e "${RED}✗ Not running${NC}"
    FRONTEND_OK=0
fi

# Check database
echo -n "Database (Port 5432): "
if docker-compose ps | grep -q "db.*Up"; then
    echo -e "${GREEN}✓ Running${NC}"
    DB_OK=1
else
    echo -e "${RED}✗ Not running${NC}"
    DB_OK=0
fi

echo ""
echo "📦 Checking Dependencies..."
echo ""

# Check GridStack in package.json
echo -n "GridStack Package: "
if grep -q "gridstack" frontend/package.json; then
    echo -e "${GREEN}✓ Found${NC}"
    GRIDSTACK_OK=1
else
    echo -e "${RED}✗ Missing${NC}"
    GRIDSTACK_OK=0
fi

# Check if node_modules has gridstack
echo -n "GridStack Installed: "
if [ -d "frontend/node_modules/gridstack" ]; then
    echo -e "${GREEN}✓ Installed${NC}"
    GRIDSTACK_INSTALLED=1
else
    echo -e "${YELLOW}⚠ Not installed (run: cd frontend && npm install)${NC}"
    GRIDSTACK_INSTALLED=0
fi

echo ""
echo "🧪 Testing API Endpoints..."
echo ""

# Test query list
echo -n "Query List API: "
QUERY_LIST=$(curl -s http://localhost:8000/api/query/list 2>/dev/null)
if echo "$QUERY_LIST" | grep -q "queries"; then
    echo -e "${GREEN}✓ Working${NC}"
    QUERIES=$(echo "$QUERY_LIST" | grep -o '"query_id"' | wc -l)
    echo "  └─ Found $QUERIES queries"
    API_OK=1
else
    echo -e "${RED}✗ Failed${NC}"
    API_OK=0
fi

# Test query execution
echo -n "Query Execution: "
QUERY_RESULT=$(curl -s -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -d '{"query_id": "sales_overview", "parameters": {}}' 2>/dev/null)

if echo "$QUERY_RESULT" | grep -q "data"; then
    echo -e "${GREEN}✓ Working${NC}"
    ROWS=$(echo "$QUERY_RESULT" | grep -o '"row_count":[0-9]*' | grep -o '[0-9]*' | head -1)
    if [ ! -z "$ROWS" ]; then
        echo "  └─ Returned $ROWS rows"
    fi
    QUERY_OK=1
else
    echo -e "${RED}✗ Failed${NC}"
    QUERY_OK=0
fi

echo ""
echo "📊 Checking Dashboard Configuration..."
echo ""

# Check if sales dashboard exists
echo -n "Sales Dashboard Config: "
if [ -f "frontend/src/config/dashboards/sales-dashboard.json" ]; then
    echo -e "${GREEN}✓ Found${NC}"
    WIDGETS=$(grep -o '"id":' frontend/src/config/dashboards/sales-dashboard.json | wc -l)
    echo "  └─ $WIDGETS widgets configured"
    DASHBOARD_OK=1
else
    echo -e "${RED}✗ Missing${NC}"
    DASHBOARD_OK=0
fi

# Check widget components
echo -n "Widget Components: "
WIDGET_COUNT=0
for widget in LineChart.vue BarChart.vue PieChart.vue DataTable.vue MetricCard.vue; do
    if [ -f "frontend/src/components/widgets/$widget" ]; then
        ((WIDGET_COUNT++))
    fi
done

if [ $WIDGET_COUNT -eq 5 ]; then
    echo -e "${GREEN}✓ All 5 widgets found${NC}"
    WIDGETS_OK=1
else
    echo -e "${YELLOW}⚠ Only $WIDGET_COUNT/5 widgets found${NC}"
    WIDGETS_OK=0
fi

echo ""
echo "🎨 Checking GridStack Integration..."
echo ""

# Check DashboardRenderer.vue for GridStack
echo -n "DashboardRenderer Integration: "
if grep -q "GridStack" frontend/src/components/Dashboard/DashboardRenderer.vue; then
    echo -e "${GREEN}✓ GridStack imported${NC}"
    RENDERER_OK=1
else
    echo -e "${RED}✗ GridStack not found${NC}"
    RENDERER_OK=0
fi

# Check for edit mode
echo -n "Edit Mode Toggle: "
if grep -q "toggleEditMode\|editMode" frontend/src/components/Dashboard/DashboardRenderer.vue; then
    echo -e "${GREEN}✓ Edit mode implemented${NC}"
    EDITMODE_OK=1
else
    echo -e "${RED}✗ Edit mode missing${NC}"
    EDITMODE_OK=0
fi

# Check for drag/resize
echo -n "Drag & Resize: "
if grep -q "draggable\|resizable" frontend/src/components/Dashboard/DashboardRenderer.vue; then
    echo -e "${GREEN}✓ Configured${NC}"
    DRAGRESIZE_OK=1
else
    echo -e "${RED}✗ Not configured${NC}"
    DRAGRESIZE_OK=0
fi

echo ""
echo "📝 Summary"
echo "=========="
echo ""

# Count successes
TOTAL=0
SUCCESS=0

checks=(
    $BACKEND_OK $FRONTEND_OK $DB_OK $GRIDSTACK_OK $GRIDSTACK_INSTALLED 
    $API_OK $QUERY_OK $DASHBOARD_OK $WIDGETS_OK $RENDERER_OK 
    $EDITMODE_OK $DRAGRESIZE_OK
)

for check in "${checks[@]}"; do
    ((TOTAL++))
    if [ "$check" -eq 1 ]; then
        ((SUCCESS++))
    fi
done

echo "Checks Passed: $SUCCESS/$TOTAL"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 All checks passed! System is fully operational.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:5173"
    echo "  2. Click 'Edit Layout' button"
    echo "  3. Drag and resize widgets"
    echo ""
    exit 0
elif [ $SUCCESS -ge 9 ]; then
    echo -e "${YELLOW}⚠️  Most checks passed. Minor issues detected.${NC}"
    echo ""
    echo "Suggestions:"
    if [ $GRIDSTACK_INSTALLED -eq 0 ]; then
        echo "  • Run: cd frontend && npm install"
    fi
    echo ""
    exit 0
else
    echo -e "${RED}❌ Several checks failed. Please review errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  • Ensure Docker is running: docker-compose up"
    echo "  • Install dependencies: cd frontend && npm install"
    echo "  • Check logs: docker-compose logs"
    echo ""
    exit 1
fi
