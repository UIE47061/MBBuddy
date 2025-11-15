@echo off
chcp 65001 >nul
REM MBBuddy One-Click Installation Script for Windows
REM This script will automatically:
REM 1. Clone the repository (if needed)
REM 2. Download AI model
REM 3. Install Docker (if needed)
REM 4. Deploy with Docker
REM 5. Show IP addresses
REM 6. Provide control commands

setlocal enabledelayedexpansion

echo.
echo =====================================
echo    MBBuddy One-Click Installation
echo =====================================
echo.
echo This script will:
echo 1. Clone project repository (if needed)
echo 2. Install Docker (if needed)
echo 3. Docker deployment
echo 4. Query and display IP addresses
echo 5. Provide meeting room control commands
echo.
pause

REM =====================================
REM 1. Git Clone Repository
REM =====================================
echo.
echo [Step 1/6] Checking project repository...

set "REPO_URL=https://github.com/UIE47061/MBBuddy.git"
set "PROJECT_NAME=MBBuddy"

REM Check if we're already in MBBuddy directory
if exist "package.json" if exist "backend" if exist "frontend" (
    echo [SUCCESS] Already in MBBuddy project directory
    set "PROJECT_ROOT=%CD%"
    goto :check_git
)

REM Check if MBBuddy directory exists in current location
if exist "%PROJECT_NAME%" (
    echo [INFO] Found existing MBBuddy directory
    cd /d "%PROJECT_NAME%"
    set "PROJECT_ROOT=%CD%"
    goto :check_git
)

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git not found, please install Git first:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [INFO] Cloning MBBuddy repository...
git clone %REPO_URL%
if %errorlevel% neq 0 (
    echo [ERROR] Repository clone failed
    pause
    exit /b 1
)

cd /d "%PROJECT_NAME%"
set "PROJECT_ROOT=%CD%"

:check_git
echo [SUCCESS] Project repository ready

REM =====================================
REM 2. Check/Install Docker
REM =====================================
echo.
echo [Step 2/5] Checking Docker installation...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker not installed
    echo [INFO] Attempting to install Docker automatically...
    echo.
    
    call "%SCRIPT_DIR%install_docker.bat"
    if %errorlevel% neq 0 (
        echo [ERROR] Docker installation failed
        echo Please install Docker manually and restart this script
        pause
        exit /b 1
    )
    
    echo [INFO] Docker installation completed
    echo [INFO] Please restart your computer and run this script again
    pause
    exit /b 0
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Compose not installed
    echo Docker Compose is usually installed with Docker Desktop
    echo Please ensure Docker Desktop is properly installed
    pause
    exit /b 1
)

echo [SUCCESS] Docker installed and available

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker service not running
    echo Please start Docker Desktop and restart this script
    pause
    exit /b 1
)

echo [SUCCESS] Docker service is running

REM =====================================
REM 3. Docker Deployment
REM =====================================
echo.
echo [Step 3/5] Docker deployment...

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker/docker-compose.yml down 2>nul

REM Build and start services
echo [INFO] Building and starting services...
echo This may take several minutes to download images and build containers...
docker-compose -f docker/docker-compose.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Docker deployment failed
    echo Please check error messages and retry
    pause
    exit /b 1
)

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if containers are running
docker-compose -f docker/docker-compose.yml ps
echo [SUCCESS] Docker deployment completed

REM =====================================
REM 4. Show IP Addresses
REM =====================================
echo.
echo [Step 4/5] Querying IP addresses...

echo.
echo =====================================
echo        Available Access URLs
echo =====================================

REM Get local IP addresses
echo [Local IP Addresses]
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

echo [Container Status]
docker-compose -f docker/docker-compose.yml ps

echo.
echo =====================================
echo         Installation Complete!
echo =====================================

REM =====================================
REM 5. Control Commands
REM =====================================
echo.
echo [Step 5/5] Setting up control commands...

echo.
echo =====================================
echo       Meeting Room Controls
echo =====================================
echo.

REM Create control scripts
echo [INFO] Creating control scripts...

REM Create start script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Starting MBBuddy meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml up -d
echo echo Services started!
echo echo Frontend: http://localhost
echo echo Backend:  http://localhost:8000
echo pause
) > "%PROJECT_ROOT%\start_meeting.bat"

REM Create stop script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Stopping MBBuddy meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml down
echo echo Services stopped!
echo pause
) > "%PROJECT_ROOT%\stop_meeting.bat"

REM Create status script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo MBBuddy meeting room service status:
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml ps
echo echo.
echo echo Service logs:
echo docker-compose -f docker/docker-compose.yml logs --tail=20
echo pause
) > "%PROJECT_ROOT%\status_meeting.bat"

REM Create restart script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Restarting MBBuddy meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml restart
echo echo Services restarted!
echo echo Frontend: http://localhost
echo echo Backend:  http://localhost:8000
echo pause
) > "%PROJECT_ROOT%\restart_meeting.bat"

echo Created the following control scripts:
echo.
echo   📂 start_meeting.bat    - Start meeting room services
echo   📂 stop_meeting.bat     - Stop meeting room services
echo   📂 status_meeting.bat   - View service status
echo   📂 restart_meeting.bat  - Restart meeting room services
echo.

echo =====================================
echo          Usage Instructions
echo =====================================
echo.
echo 🚀 Quick Start:
echo   Double-click start_meeting.bat to start services
echo   Open browser to http://localhost
echo.
echo 🛑 Stop Services:
echo   Double-click stop_meeting.bat
echo.
echo 📊 Check Status:
echo   Double-click status_meeting.bat
echo.
echo 🔄 Restart Services:
echo   Double-click restart_meeting.bat
echo.
echo 💡 Tips:
echo   - First startup may take longer time
echo   - Keep Docker Desktop running
echo   - Share IP addresses for device access
echo.

echo =====================================
echo      Installation Successful! 🎉
echo =====================================
echo.
echo Press any key to exit installation...
pause >nul

exit /b 0

REM Error handling
:error_dir
echo [ERROR] Cannot find project directory structure
echo Please ensure you are running this script in the correct directory
pause
exit /b 1
