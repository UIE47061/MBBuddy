@echo off
chcp 65001 >nul
REM MBBuddy Control Panel for Windows

setlocal enabledelayedexpansion

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

:menu
cls
echo.
echo =====================================
echo      MBBuddy Meeting Room Control
echo =====================================
echo.
echo Please select an operation:
echo.
echo   1. 🚀 Start Meeting Services
echo   2. 🛑 Stop Meeting Services
echo   3. 🔄 Restart Meeting Services
echo   4. 📊 View Service Status
echo   5. 📋 View Service Logs
echo   6. 🌐 Show Access URLs
echo   7. 🌍 Open Web Interface
echo   8. 🔧 One-Click Install & Deploy
echo   9. ❌ Exit
echo.
echo =====================================

set /p choice="Please enter option (1-9): "

if "%choice%"=="1" goto :start_service
if "%choice%"=="2" goto :stop_service
if "%choice%"=="3" goto :restart_service
if "%choice%"=="4" goto :status_service
if "%choice%"=="5" goto :logs_service
if "%choice%"=="6" goto :show_addresses
if "%choice%"=="7" goto :open_web
if "%choice%"=="8" goto :install_deploy
if "%choice%"=="9" goto :exit
goto :invalid_choice

:start_service
echo.
echo [INFO] Starting MBBuddy meeting room services...
docker-compose -f docker/docker-compose.yml up -d
if %errorlevel% equ 0 (
    echo [SUCCESS] Services started successfully!
    echo.
    echo Services are now available. Would you like to open the web interface? (Y/N)
    set /p open_choice="Enter your choice: "
    if /i "!open_choice!"=="Y" (
        call "%SCRIPT_DIR%open_web.bat"
    )
) else (
    echo [ERROR] Failed to start services
)
echo.
pause
goto :menu

:stop_service
echo.
echo [INFO] Stopping MBBuddy meeting room services...
docker-compose -f docker/docker-compose.yml down
if %errorlevel% equ 0 (
    echo [SUCCESS] Services stopped
) else (
    echo [ERROR] Error occurred while stopping services
)
echo.
pause
goto :menu

:restart_service
echo.
echo [INFO] Restarting MBBuddy meeting room services...
docker-compose -f docker/docker-compose.yml restart
if %errorlevel% equ 0 (
    echo [SUCCESS] Services restarted successfully!
    echo.
    echo Services are now available. Would you like to open the web interface? (Y/N)
    set /p open_choice="Enter your choice: "
    if /i "!open_choice!"=="Y" (
        call "%SCRIPT_DIR%open_web.bat"
    )
) else (
    echo [ERROR] Failed to restart services
)
echo.
pause
goto :menu

:status_service
echo.
echo [INFO] MBBuddy meeting room service status:
echo.
docker-compose -f docker/docker-compose.yml ps
echo.
pause
goto :menu

:logs_service
echo.
echo [INFO] MBBuddy meeting room service logs (Press Ctrl+C to exit):
echo.
docker-compose -f docker/docker-compose.yml logs -f
goto :menu

:show_addresses
echo.
echo =====================================
echo        Available Access URLs
echo =====================================
echo.

REM Check if services are running
docker-compose -f docker/docker-compose.yml ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [WARNING] MBBuddy services are not currently running!
    echo Please start the services first (Option 1)
    echo.
)

echo [Local Access]
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8000
echo.

REM Get local IP addresses
echo [Network Access URLs]
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

echo [Container Status]
docker-compose -f docker/docker-compose.yml ps
echo.
echo TIP: Use option 7 to automatically open web interface with IP selection
echo.
pause
goto :menu

:open_web
echo.
echo [INFO] Launching web interface selector...
call "%SCRIPT_DIR%open_web.bat"
echo.
echo Press any key to return to main menu...
pause >nul
goto :menu

:install_deploy
echo.
echo [INFO] Running one-click install & deploy...
call "%SCRIPT_DIR%quick_deploy.bat"
pause
goto :menu

:invalid_choice
echo.
echo [ERROR] Invalid option, please select again
echo.
pause
goto :menu

:exit
echo.
echo Thank you for using MBBuddy Control Panel!
echo.
exit /b 0
