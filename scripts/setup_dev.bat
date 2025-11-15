@echo off
chcp 65001 >nul
REM MBBuddy Local Development Environment Setup Script (Windows)

setlocal enabledelayedexpansion

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo.
echo =====================================
echo   MBBuddy Local Development Setup
echo =====================================
echo.

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

REM Check if in project root directory
if not exist "package.json" goto :error_dir
if not exist "backend" goto :error_dir
if not exist "frontend" goto :error_dir

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found, please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Setting up backend environment...

REM Create virtual environment
if not exist ".venv" (
    echo   Creating virtual environment...
    python -m venv .venv
) else (
    echo   Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo   Installing backend dependencies...
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt

echo [INFO] Setting up frontend environment...

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm not found, please install Node.js
    pause
    exit /b 1
)

REM Install frontend dependencies
cd frontend
echo   Installing frontend dependencies...
npm install
cd ..

echo.
echo [SUCCESS] Environment setup completed!
echo.
echo [INFO] Now you can start services:
echo    scripts/start_dev.bat         # Start development services
echo    scripts/stop_dev.bat          # Stop development services
echo.
pause
exit /b 0

:error_dir
echo [ERROR] Please run this script from the MBBuddy project root directory
pause
exit /b 1
