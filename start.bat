@echo off
REM Start Dashboard Application (SQLite version)
REM This script starts both backend and frontend

echo ========================================
echo Starting Dashboard Application
echo ========================================
echo.

REM Check if database exists
if not exist "backend\dashboard.db" (
    echo WARNING: Database not found!
    echo Running setup first...
    call setup.bat
)

echo Starting Backend...
start "Dashboard Backend" cmd /k "cd backend && uvicorn app.main:app --reload"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Dashboard Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Application Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Kill the processes
taskkill /FI "WindowTitle eq Dashboard Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Dashboard Frontend*" /F >nul 2>&1

echo.
echo All services stopped.
