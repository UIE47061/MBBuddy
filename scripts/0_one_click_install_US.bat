@echo off
chcp 65001 >nul
REM MBBuddy One-Click Install Script
REM This script will automatically perform the following steps:
REM 1. Install Docker Desktop
REM 2. Guide you to download and set up AnythingLLM
REM 3. Obtain an API key and set environment variables
REM 4. Update docker-compose.yml configuration
REM 5. Deploy the production environment
REM 6. Start services

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo     MBBuddy One-Click Install Script v1.0
echo ==========================================
echo.
echo This script will guide you through the full MBBuddy installation and setup
echo.
echo Installation steps:
echo   1. Check and install Docker Desktop
echo   2. Guide to download and set up AnythingLLM
echo   3. Obtain API key
echo   4. Configure environment variables
echo   5. Deploy MBBuddy services
echo   6. Complete setup
echo.
pause

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Switch to project root directory
cd /d "%PROJECT_ROOT%"

REM Verify correct project directory
if not exist "backend" goto :error_dir
if not exist "frontend" goto :error_dir
if not exist "docker\docker-compose.yml" goto :error_dir

echo [SUCCESS] Project directory confirmed
echo.

REM Quick check for running MBBuddy services
echo [INFO] Checking existing MBBuddy services...

REM First check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Docker not installed or not running, proceeding with full installation
    echo.
    goto :install_docker
)

REM Docker is available, check for running MBBuddy services
docker ps --filter "name=mbbuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}" 2>nul | findstr "mbbuddy" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Found running MBBuddy services:
    docker ps --filter "name=mbbuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}" 2>nul
    echo.
    set /p skip_setup="MBBuddy is already running. Skip installation and show access info? (y/n): "
    if /i "!skip_setup!"=="Y" (
        goto :show_access_info
    )
    echo [INFO] Reinstalling and reconfiguring MBBuddy...
    echo [INFO] Stopping existing services...
    docker-compose -f docker\docker-compose.yml down >nul 2>&1
    echo.
) else (
    echo [INFO] No running MBBuddy services found
    echo.
)

:install_docker

REM =====================================
REM Step 1: Install Docker Desktop
REM =====================================
echo ==========================================
echo Step 1/6: Check and install Docker Desktop
echo ==========================================
echo.

REM First check if Docker is already installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker is installed
    docker --version
    echo.
    goto :docker_installed
)

REM Docker not installed, begin installation
echo [INFO] Docker is not installed; starting automatic installation...
echo.
call "%SCRIPT_DIR%install_docker.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Docker installation failed
    echo Please install Docker Desktop manually and rerun this script
    echo Download: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Docker installation completed!
echo.
echo [IMPORTANT]
echo Docker Desktop has been installed, but you need to:
echo 1. Restart your computer (recommended)
echo 2. Or manually start Docker Desktop application
echo 3. Complete Docker Desktop initial setup
echo 4. Ensure Docker Desktop is running
echo 5. Rerun this script to continue MBBuddy installation
echo.
set /p restart_now="Restart computer now? (y/n): "
if /i "!restart_now!"=="Y" (
    echo [INFO] Computer will restart in 10 seconds...
    shutdown /r /t 10 /c "Restarting to complete Docker installation"
    echo Press any key to cancel...
    pause
    shutdown /a
)
echo [INFO] Please restart and start Docker Desktop, then rerun this script
pause
exit /b 0

:docker_installed

REM Check whether Docker service is running
echo [INFO] Checking Docker service status...

REM Try a simple Docker command first
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker service is running
    goto :docker_ready
)

REM If that fails, try a more detailed check
docker version --format "{{{{.Server.Version}}}}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker service is running
    goto :docker_ready
)

REM Handling when Docker service is not running
echo [WARNING] Docker service is not running
echo [INFO] Trying to start Docker Desktop...

REM Check if Docker Desktop is already running
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>nul | find /I /N "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo [INFO] Started Docker Desktop...
) else (
    echo [INFO] Docker Desktop is already running; waiting for service readiness...
)

echo [INFO] Waiting for Docker service to start...
set retry_count=0
:wait_docker
timeout /t 3 /nobreak >nul
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker service started
    goto :docker_ready
)

set /a retry_count+=1
if !retry_count! lss 20 (
    echo [INFO] Waiting... (!retry_count!/20)
    goto :wait_docker
)

echo [ERROR] Docker service startup timed out
echo.
echo Possible fixes:
echo 1. Start Docker Desktop manually
echo 2. Restart Docker Desktop
echo 3. Check WSL2 status (wsl --status)
echo 4. Reboot your computer
echo.
set /p continue_anyway="Docker service may not be fully ready. Continue anyway? (y/n): "
if /i "!continue_anyway!"=="Y" (
    echo [WARNING] Continuing, but Docker-related errors may occur
    goto :docker_ready
)
echo [INFO] Please resolve Docker issues and rerun this script
pause
exit /b 1

:docker_ready
echo [SUCCESS] Docker check complete
echo.

REM =====================================
REM Step 2: AnythingLLM download and setup guide
REM =====================================
echo ==========================================
echo Step 2/6: AnythingLLM download and setup
echo ==========================================
echo.
echo AnythingLLM is the core AI engine for MBBuddy; it must be downloaded and set up separately
echo.
echo [Important] Please follow the steps below:
echo.
echo 1. Download the AnythingLLM Desktop edition
echo    Download: https://anythingllm.com/download
echo    Choose the "Desktop" edition for your operating system
echo.
echo 2. Install and launch AnythingLLM
echo    - Run the downloaded installer
echo    - Finish installation and launch AnythingLLM
echo    - During installation choose AnythingLLM NPU; select any model you prefer
echo    - After initial setup, go to Settings > System Admin > General and enable `Enable network discovery`
echo.
echo 3. Ensure AnythingLLM is running at localhost:3001
echo    (This is the default port; note it if different)
echo.

set /p llm_ready="After installing AnythingLLM and confirming it is running, enter y to continue: "
if /i not "!llm_ready!"=="Y" (
    echo  [INFO] Please complete the AnythingLLM setup and rerun this script
    pause
    exit /b 0
)

REM Check if AnythingLLM is reachable
echo [INFO] Checking AnythingLLM connectivity...
curl -s http://localhost:3001 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Unable to connect to AnythingLLM (localhost:3001)
    echo.
    echo Please confirm:
    echo 1. AnythingLLM is installed and running
    echo 2. The service runs on localhost:3001 (default port)
    echo 3. The firewall is not blocking the connection
    echo.
    set /p continue_anyway="Continue anyway? (y/n): "
    if /i not "!continue_anyway!"=="Y" (
        echo [INFO] Please check your AnythingLLM setup and rerun this script
        pause
        exit /b 0
    )
) else (
    echo [SUCCESS] AnythingLLM connectivity check passed
)

echo.

REM =====================================
REM Step 3: Obtain API key
REM =====================================
echo ==========================================
echo Step 3/6: Get the AnythingLLM API key
echo ==========================================
echo.
echo Now we need to obtain the AnythingLLM API key
echo.
echo [Important] Follow these steps to get your API key:
echo.
echo 1. Open the AnythingLLM interface
echo.
echo 2. Navigate to the Settings page
echo    Typically in the sidebar or the top-right menu
echo.
echo 3. Find the "API Keys" page
echo.
echo 4. Create a new API key
echo    - Click "Create new API Key"
echo    - Copy the generated API key
echo.
echo 5. The API key format typically looks like: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
echo.

echo.
echo After obtaining the API key, come back here
echo.

:input_api_key
set "api_key="
set /p api_key="Enter your AnythingLLM API key: "

if "!api_key!"=="" (
    echo [ERROR] API key cannot be empty; please try again
    goto :input_api_key
)

REM Simple validation of API key format
echo !api_key! | findstr /r "^[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}$" >nul
if %errorlevel% neq 0 (
    echo [WARNING] The API key format may be incorrect
    echo Expected format: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
    echo Your input: !api_key!
    echo.
    set /p confirm_key="Confirm using this key? (y/n): "
    if /i not "!confirm_key!"=="Y" (
        goto :input_api_key
    )
)

echo [SUCCESS] API key received: !api_key!
echo.

REM =====================================
REM Step 4: Set environment variables and update configuration
REM =====================================
echo ==========================================
echo Step 4/6: Set environment variables and update configuration
echo ==========================================
echo.

REM Set environment variables
echo [INFO] Setting system environment variable ANYTHINGLLM_API_KEY...
setx ANYTHINGLLM_API_KEY "!api_key!" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Environment variable set successfully
) else (
    echo [WARNING] Setting the environment variable may have failed; will update config file directly
)

REM Set the environment variable for this session
set ANYTHINGLLM_API_KEY=!api_key!

REM Update configuration files...

REM Create .env file
echo [INFO] Creating environment file (.env)...
(
echo # MBBuddy environment variables
echo # This file is auto-generated by the one-click installer
echo.
echo # AnythingLLM configuration
echo ANYTHINGLLM_BASE_URL=http://host.docker.internal:3001
echo ANYTHINGLLM_API_KEY=!api_key!
echo ANYTHINGLLM_WORKSPACE_SLUG=MBBuddy
echo ANYTHINGLLM_DEBUG_THINKING=false
echo.
echo # Service configuration
echo PYTHONPATH=/app
) > ".env"

if %errorlevel% equ 0 (
    echo [SUCCESS] .env file created
    echo [INFO] docker-compose.yml will read environment variables from .env
) else (
    echo [ERROR] Failed to create .env file
    pause
    exit /b 1
)

echo.

REM =====================================
REM Step 5: Deploy production environment
REM =====================================
echo ==========================================
echo Step 5/6: Deploy MBBuddy production environment
echo ==========================================
echo.

echo [INFO] Stopping existing containers (if any)...
docker-compose -f docker\docker-compose.yml down >nul 2>&1

echo [INFO] Building and starting MBBuddy services...
echo This may take a few minutes; please wait...
echo.

REM Ensure docker-compose reads the env var in this session
set ANYTHINGLLM_API_KEY=!api_key!

docker-compose -f docker\docker-compose.yml up -d --build
if %errorlevel% neq 0 (
    echo [ERROR] MBBuddy service deployment failed
    echo.
    echo Possible fixes:
    echo 1. Verify Docker Desktop is running
    echo 2. Check firewall settings
    echo 3. Ensure sufficient disk space
    echo 4. Restart Docker Desktop
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] MBBuddy services deployed!
echo.

REM Wait for services to start
echo [INFO] Waiting for services to fully start...
timeout /t 15 /nobreak >nul

REM =====================================
REM Step 6: Verify installation and show access info
REM =====================================
:show_access_info
echo ==========================================
echo Step 6/6: Verify installation and show access info
echo ==========================================
echo.

REM Check container status
echo [Container Status]
docker ps --filter "name=MBBuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}" 2>nul
if %errorlevel% neq 0 (
    echo Unable to check container status; please ensure Docker is running
)

echo.

REM Show access information
echo ==========================================
echo           🎉 Installation complete! 🎉
echo ==========================================
echo.
echo [Access URLs]

REM Local access
echo Local access:
echo   Frontend: http://localhost
echo   Backend: http://localhost:8000
echo.

echo LAN access:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "ip=%%b"
        set "ip=!ip: =!"
        if not "!ip!"=="127.0.0.1" (
            echo   Frontend: http://!ip!
            echo   Backend: http://!ip!:8000
            echo.
        )
    )
)

echo [AnythingLLM status]
echo   URL: http://localhost:3001
echo   API key: !api_key!
echo.

echo [Control commands]
echo   Start services: docker-compose -f docker\docker-compose.yml up -d
echo   Stop services: docker-compose -f docker\docker-compose.yml down
echo   Restart services: docker-compose -f docker\docker-compose.yml restart
echo   View logs: docker-compose -f docker\docker-compose.yml logs -f
echo   View status: docker-compose -f docker\docker-compose.yml ps
echo.

echo [Usage]
echo 1. Open the frontend URL in your browser to start using MBBuddy
echo 2. Keep AnythingLLM running
echo 3. To stop services, use the stop command above
echo 4. After a reboot, you may need to start Docker Desktop and AnythingLLM manually
echo.

echo [Maintenance]
echo - To update the API key, rerun this script
echo - To redeploy, use the control commands
echo - For technical support, see the project documentation
echo.

REM Provide a quick action
set /p open_browser="Open the MBBuddy frontend now? (y/n): "
if /i "!open_browser!"=="Y" (
    start http://localhost
)

echo.
echo ==========================================
echo        MBBuddy one-click installation complete! 🚀
echo ==========================================
echo.
echo Thanks for using MBBuddy!
echo.
pause

exit /b 0

REM =====================================
REM Error handling
REM =====================================
:error_dir
echo [ERROR] Cannot find the expected project structure
echo Make sure you are running this script in the MBBuddy project root
echo.
echo Expected structure:
echo - package.json
echo - backend/
echo - frontend/
echo - docker/docker-compose.yml
echo.
pause
exit /b 1
