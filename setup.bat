@echo off
REM SQLite Setup Script for Windows
REM Run this from the project root directory

echo ========================================
echo SQLite Dashboard Setup for Windows
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: backend folder not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend folder not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

echo Step 1: Setting up Backend...
echo ================================
cd backend

REM Copy .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
) else (
    echo .env file already exists, skipping...
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)

echo.
echo Initializing SQLite database...
python init_db.py

if errorlevel 1 (
    echo ERROR: Failed to initialize database!
    pause
    exit /b 1
)

echo.
echo Backend setup complete!
echo.

cd ..

echo Step 2: Setting up Frontend...
echo ================================
cd frontend

REM Copy .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
) else (
    echo .env file already exists, skipping...
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo Installing Node dependencies...
call npm install

if errorlevel 1 (
    echo ERROR: Failed to install Node dependencies!
    pause
    exit /b 1
)

echo.
echo Frontend setup complete!
echo.

cd ..

echo.
echo ========================================
echo Setup Complete! 
echo ========================================
echo.
echo Database file created at: backend\dashboard.db
echo.
echo To start the application:
echo.
echo   Backend:  cd backend && uvicorn app.main:app --reload
echo   Frontend: cd frontend && npm run dev
echo.
echo Or use: start.bat
echo.
echo Then open: http://localhost:5173
echo.
pause
