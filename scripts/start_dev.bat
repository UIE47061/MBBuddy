@echo off
chcp 65001 >nul
REM MBBuddy Local Development Services Start Script (Windows)

setlocal enabledelayedexpansion

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo.
echo =====================================
echo   Start MBBuddy Local Development
echo =====================================
echo.

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

REM Check if in project root directory
if not exist "package.json" goto :error_dir
if not exist "backend" goto :error_dir
if not exist "frontend" goto :error_dir

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found, please run setup_dev.bat first
    pause
    exit /b 1
)

echo [INFO] Starting backend service...
REM Start backend service in background
call .venv\Scripts\activate.bat
start /b cmd /c "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001 > backend.log 2>&1"
echo   Backend service started

echo [INFO] Starting frontend service...
REM Start frontend service in background
cd frontend
start /b cmd /c "npm run dev -- --host > ..\frontend.log 2>&1"
echo   Frontend service started
cd ..

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo [SUCCESS] Services started!
echo.
echo [INFO] Network Access:
echo    Run this command to find your IP:
echo    ipconfig ^| findstr "IPv4"
echo    Then access: http://[Your-IP]:5173
echo.
echo [INFO] View logs:
echo    Backend log: type backend.log
echo    Frontend log: type frontend.log
echo.
echo [INFO] Stop services:
echo    stop_dev.bat
echo.
pause
exit /b 0

:error_dir
echo [ERROR] Please run this script from the MBBuddy project root directory
pause
exit /b 1
