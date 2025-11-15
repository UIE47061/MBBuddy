@echo off
chcp 65001 >nul
REM MBBuddy Web Interface Launcher
REM This script allows users to select IP and open web interface

setlocal enabledelayedexpansion

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

echo.
echo =====================================
echo      MBBuddy Web Interface Launcher
echo =====================================
echo.

REM Check if services are running
docker-compose -f docker/docker-compose.yml ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [WARNING] MBBuddy services are not running!
    echo.
    echo Would you like to start them first? (Y/N)
    set /p start_choice="Enter your choice: "
    if /i "!start_choice!"=="Y" (
        echo [INFO] Starting services...
        docker-compose -f docker/docker-compose.yml up -d
        echo [INFO] Waiting for services to start...
        timeout /t 8 /nobreak >nul
    ) else (
        echo [INFO] Exiting...
        timeout /t 2 /nobreak >nul
        exit /b 0
    )
)

echo.
echo Collecting available IP addresses...
echo.

REM Collect IP addresses
set ip_count=0
set "ip_list="

REM Add localhost option
set /a ip_count+=1
set "ip[!ip_count!]=localhost"
set "ip_list=!ip_list! !ip_count!"

REM Get network IP addresses
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "current_ip=%%b"
        set "current_ip=!current_ip: =!"
        if not "!current_ip!"=="127.0.0.1" (
            set /a ip_count+=1
            set "ip[!ip_count!]=!current_ip!"
            set "ip_list=!ip_list! !ip_count!"
        )
    )
)

if !ip_count! equ 0 (
    echo [ERROR] No IP addresses found!
    pause
    exit /b 1
)

echo =====================================
echo        Available IP Addresses
echo =====================================
echo.
for %%i in (!ip_list!) do (
    if "!ip[%%i]!"=="localhost" (
        echo   %%i. !ip[%%i]! (Local access only)
    ) else (
        echo   %%i. !ip[%%i]! (Network accessible)
    )
)
echo.
set /a max_choice=!ip_count!+1
echo   !max_choice!. Exit
echo.
echo =====================================

set /p ip_choice="Please select an IP address (1-!max_choice!): "

REM Validate choice
if !ip_choice! lss 1 goto :invalid_ip_choice
if !ip_choice! gtr !max_choice! goto :invalid_ip_choice
if !ip_choice! equ !max_choice! exit /b 0

REM Get selected IP
set "selected_ip=!ip[%ip_choice%]!"

echo.
echo =====================================
echo Selected IP: !selected_ip!
echo =====================================
echo.
echo Choose service to open:
echo.
echo   1. 🌐 Frontend (Main Interface)
echo   2. 🔧 Backend API Documentation  
echo   3. 🚀 Both Frontend and Backend
echo   4. 📋 Show URLs only (don't open)
echo   5. ❌ Cancel
echo.

set /p service_choice="Please select service (1-5): "

if "%service_choice%"=="1" goto :open_frontend
if "%service_choice%"=="2" goto :open_backend
if "%service_choice%"=="3" goto :open_both
if "%service_choice%"=="4" goto :show_urls
if "%service_choice%"=="5" exit /b 0
goto :invalid_service_choice

:open_frontend
echo.
echo [INFO] Opening Frontend at http://!selected_ip!
echo Browser should open automatically...
start http://!selected_ip!
echo.
echo =====================================
echo   Frontend URL: http://!selected_ip!
echo =====================================
echo.
echo You can share this URL with others on the same network!
pause
exit /b 0

:open_backend
echo.
echo [INFO] Opening Backend API at http://!selected_ip!:8000
echo Browser should open automatically...
start http://!selected_ip!:8000
echo.
echo =====================================
echo   Backend URL: http://!selected_ip!:8000
echo =====================================
echo.
echo This opens the API documentation and endpoints.
pause
exit /b 0

:open_both
echo.
echo [INFO] Opening both Frontend and Backend...
echo Opening Frontend...
start http://!selected_ip!
timeout /t 2 /nobreak >nul
echo Opening Backend API...
start http://!selected_ip!:8000
echo.
echo =====================================
echo   Frontend URL: http://!selected_ip!
echo   Backend URL:  http://!selected_ip!:8000
echo =====================================
echo.
echo Both services opened in your default browser!
echo You can share these URLs with others on the same network!
pause
exit /b 0

:show_urls
echo.
echo =====================================
echo         Access URLs
echo =====================================
echo.
echo   Frontend: http://!selected_ip!
echo   Backend:  http://!selected_ip!:8000
echo.
echo Copy these URLs to access MBBuddy from any browser.
echo You can share these URLs with others on the same network!
echo.
pause
exit /b 0

:invalid_ip_choice
echo.
echo [ERROR] Invalid IP choice. Please enter a number between 1 and !max_choice!
timeout /t 2 /nobreak >nul
goto :main_choice

:invalid_service_choice
echo.
echo [ERROR] Invalid service choice. Please enter a number between 1 and 5
timeout /t 2 /nobreak >nul
goto :service_choice

:main_choice
echo.
echo Please select an IP address (1-!max_choice!): 
set /p ip_choice=""
goto :validate_ip

:service_choice
echo.
echo Please select service (1-5): 
set /p service_choice=""
goto :validate_service

:validate_ip
if !ip_choice! lss 1 goto :invalid_ip_choice
if !ip_choice! gtr !max_choice! goto :invalid_ip_choice
if !ip_choice! equ !max_choice! exit /b 0
set "selected_ip=!ip[%ip_choice%]!"
goto :service_menu

:service_menu
echo.
echo Selected IP: !selected_ip!
echo.
echo Choose service to open:
echo   1. Frontend, 2. Backend, 3. Both, 4. Show URLs, 5. Cancel
echo.
goto :service_choice

:validate_service
if "%service_choice%"=="1" goto :open_frontend
if "%service_choice%"=="2" goto :open_backend  
if "%service_choice%"=="3" goto :open_both
if "%service_choice%"=="4" goto :show_urls
if "%service_choice%"=="5" exit /b 0
goto :invalid_service_choice
