@echo off
chcp 65001 >nul
REM MBBuddy Quick Setup Script for Windows (For existing project)
REM Use this script when you already have the MBBuddy project

setlocal enabledelayedexpansion

echo.
echo =====================================
echo      MBBuddy Quick Deployment
echo =====================================
echo.
echo This script is for existing project directories
echo.

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

REM Check if in project root directory
if not exist "package.json" goto :error_dir
if not exist "backend" goto :error_dir
if not exist "frontend" goto :error_dir

echo [SUCCESS] Project directory confirmed

REM =====================================
REM Check Docker
REM =====================================
echo.
echo [INFO] Checking Docker...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker not installed
    echo [INFO] Attempting to install Docker automatically...
    call "%SCRIPT_DIR%install_docker.bat"
    if %errorlevel% neq 0 (
        echo [ERROR] Docker installation failed, please install Docker Desktop first
        pause
        exit /b 1
    )
    echo [INFO] Please restart your computer and run this script again
    pause
    exit /b 0
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker service not running, please start Docker Desktop
    pause
    exit /b 1
)

echo [SUCCESS] Docker check completed

REM =====================================
REM Deploy with Docker
REM =====================================
echo.
echo [INFO] Starting Docker deployment...

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker/docker-compose.yml down 2>nul

REM Build and start services
echo [INFO] Building and starting services...
docker-compose -f docker/docker-compose.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Docker deployment failed
    pause
    exit /b 1
)

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

echo [SUCCESS] Deployment completed!

REM =====================================
REM Show Access Information
REM =====================================
echo.
echo =====================================
echo        Access Information
echo =====================================

REM Get local IP addresses
echo [Available Access URLs]
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "ip=%%b"
        set "ip=!ip: =!"
        if not "!ip!"=="127.0.0.1" (
            echo   Frontend: http://!ip!
            echo   Backend:  http://!ip!:8000
            echo.
        )
    )
)

echo [Local Access]
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8000
echo.

REM Show container status
echo [Container Status]
docker-compose -f docker/docker-compose.yml ps

echo.
echo =====================================
echo      Control Commands
echo =====================================
echo.
echo Start Services: start_dev.bat
echo Stop Services:  stop_dev.bat
echo Restart:        docker-compose -f docker/docker-compose.yml restart
echo View Logs:      docker-compose -f docker/docker-compose.yml logs -f
echo Check Status:   docker-compose -f docker/docker-compose.yml ps
echo.

echo =====================================
echo      Quick Deployment Complete! 🎉
echo =====================================
echo.
pause

exit /b 0

:error_dir
echo [ERROR] Cannot find project directory structure
echo Please ensure you are running this script in the MBBuddy project root directory
pause
exit /b 1
