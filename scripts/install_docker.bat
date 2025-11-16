@echo off
chcp 65001 >nul
REM Docker Auto-Installer for Windows
REM This script attempts to automatically install Docker Desktop

setlocal enabledelayedexpansion

echo.
echo =====================================
echo      Docker Auto-Installer
echo =====================================
echo.

REM Check if Docker is already installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker is already installed
    docker --version
    
    REM Check if Docker service is running
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker service is running
        exit /b 0
    ) else (
        echo [WARNING] Docker service is not running
        echo Please start Docker Desktop and try again
        pause
        exit /b 1
    )
)

echo [INFO] Docker not found, attempting automatic installation...
echo.

REM Check Windows version using wmic (more reliable)
echo [INFO] Detecting Windows version...
for /f "tokens=2 delims==" %%i in ('wmic os get Caption /value 2^>nul') do set "os_caption=%%i"

REM If wmic fails, try ver command
if not defined os_caption (
    for /f "tokens=4,5,6 delims=[.] " %%a in ('ver') do (
        set "win_major=%%a"
        set "win_minor=%%b"
    )
    if "!win_major!" geq "10" (
        set "os_caption=Windows 10 or higher"
    )
)

REM Check if it's Windows 10 or 11
echo !os_caption! | findstr /i "Windows" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Could not detect Windows version, attempting installation anyway...
) else (
    echo [INFO] Detected: !os_caption!
    echo !os_caption! | findstr /i "Windows 10\|Windows 11\|Windows Server 2019\|Windows Server 2022" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Docker Desktop is officially supported on Windows 10/11
        echo Your system: !os_caption!
        echo.
        set /p continue_install="Do you want to continue installation anyway? (y/n): "
        if /i not "!continue_install!"=="Y" (
            echo [INFO] Installation cancelled
            pause
            exit /b 1
        )
    )
)

REM Check if running as administrator
echo [INFO] Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as administrator
    echo.
    echo [INFO] Some installation methods require administrator privileges
    echo [INFO] Winget installation can work without administrator rights
    echo.
    set /p admin_choice="Continue installation? (y/n): "
    if /i not "!admin_choice!"=="Y" (
        echo [INFO] Installation cancelled
        echo [INFO] Tip: Right-click the script and select "Run as administrator"
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Running with administrator privileges
)

echo.

echo [INFO] Trying multiple installation methods...
echo.

REM Method 1: Try winget (Windows Package Manager - Recommended)
echo [Method 1] Checking for winget...
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Winget found, installing Docker Desktop...
    echo [INFO] This may take a few minutes, please wait...
    winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker Desktop installed successfully via winget!
        goto :installation_complete
    ) else (
        echo [WARNING] Winget installation failed, trying next method...
    )
) else (
    echo [INFO] Winget not found, trying next method...
)

REM Method 2: Try Chocolatey
echo.
echo [Method 2] Checking for Chocolatey...
choco --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Chocolatey found, installing Docker Desktop...
    choco install docker-desktop -y --ignore-checksums
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker Desktop installed successfully via Chocolatey!
        goto :installation_complete
    ) else (
        echo [WARNING] Chocolatey installation failed, trying next method...
    )
) else (
    echo [INFO] Chocolatey not found, trying next method...
)

REM Method 3: Direct download and install
echo.
echo [Method 3] Direct download installation...
echo [INFO] Downloading Docker Desktop installer...

set "DOCKER_INSTALLER=%TEMP%\DockerDesktopInstaller.exe"
set "DOCKER_URL=https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe"

REM Try curl first
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Using curl to download...
    curl -L --progress-bar -o "%DOCKER_INSTALLER%" "%DOCKER_URL%"
    set download_result=%errorlevel%
) else (
    echo [INFO] Using PowerShell to download...
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOCKER_URL%' -OutFile '%DOCKER_INSTALLER%'; exit $LASTEXITCODE}"
    set download_result=%errorlevel%
)

if !download_result! neq 0 (
    echo [ERROR] Failed to download Docker Desktop installer
    goto :manual_installation
)

if not exist "%DOCKER_INSTALLER%" (
    echo [ERROR] Installer file not found after download
    goto :manual_installation
)

echo [INFO] Download completed successfully
echo [INFO] Running Docker Desktop installer...
echo.
echo NOTE: Please follow the installation wizard:
echo 1. Accept the license agreement
echo 2. Choose installation options (default recommended)
echo 3. Allow restart when prompted
echo 4. Run this script again after restart
echo.

start /wait "%DOCKER_INSTALLER%" install --quiet --accept-license
set install_result=%errorlevel%

REM Clean up installer
if exist "%DOCKER_INSTALLER%" del /f "%DOCKER_INSTALLER%"

if !install_result! equ 0 (
    echo [SUCCESS] Docker Desktop installation completed!
    goto :installation_complete
) else (
    echo [WARNING] Installation may have issues, checking status...
    
    REM Wait a moment and check if Docker was installed
    timeout /t 5 /nobreak >nul
    docker --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker appears to be installed despite warnings
        goto :installation_complete
    ) else (
        echo [ERROR] Docker installation failed
        goto :manual_installation
    )
)

:installation_complete
echo.
echo =====================================
echo    Docker Installation Complete!
echo =====================================
echo.
echo [INFO] Docker Desktop has been installed successfully
echo [INFO] You may need to:
echo   1. Restart your computer
echo   2. Start Docker Desktop manually
echo   3. Accept any license agreements
echo   4. Complete the initial setup
echo.
echo [INFO] After restart, Docker will be available for use
echo.
pause
exit /b 0

:manual_installation
echo.
echo =====================================
echo      Manual Installation Required
echo =====================================
echo.
echo [ERROR] Automatic installation failed
echo.
echo Please manually install Docker Desktop:
echo 1. Visit: https://docs.docker.com/desktop/install/windows-install/
echo 2. Download Docker Desktop for Windows
echo 3. Run the installer as administrator
echo 4. Restart your computer when prompted
echo 5. Run this installation script again
echo.
echo System Requirements:
echo - Windows 10 64-bit or Windows 11
echo - WSL 2 feature enabled
echo - Virtualization enabled in BIOS
echo - At least 4GB RAM (8GB recommended)
echo.
pause
exit /b 1
