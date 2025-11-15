@echo off
chcp 65001 >nul
REM MBBuddy 快速重新部署腳本
REM 用於已完成初始設置的 MBBuddy 環境

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo      MBBuddy 快速重新部署
echo ==========================================
echo.

REM 獲取腳本目錄和專案根目錄
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM 切換到專案根目錄
cd /d "%PROJECT_ROOT%"

REM 檢查是否在正確的專案目錄
if not exist "package.json" goto :error_dir
if not exist "docker\docker-compose.yml" goto :error_dir

echo [INFO] 專案目錄確認完成
echo.

REM 檢查 Docker 狀態
echo [INFO] 檢查 Docker 狀態...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 服務未運行
    echo 請先啟動 Docker Desktop
    pause
    exit /b 1
)

echo [SUCCESS] Docker 檢查完成
echo.

REM 檢查 .env 檔案是否存在
if not exist ".env" (
    echo [WARNING] .env 檔案不存在
    echo 請確保已完成初始設置，或執行 one_click_install.bat
    pause
    exit /b 1
)

REM 讀取 .env 檔案中的 API 金鑰
for /f "tokens=2 delims==" %%a in ('findstr "ANYTHINGLLM_API_KEY" .env 2^>nul') do (
    set "ANYTHINGLLM_API_KEY=%%a"
)

if "!ANYTHINGLLM_API_KEY!"=="" (
    echo [WARNING] 無法從 .env 檔案讀取 API 金鑰
    echo 請檢查 .env 檔案配置
    pause
    exit /b 1
)

echo [INFO] 配置檔案檢查完成，API 金鑰: !ANYTHINGLLM_API_KEY!
echo.

REM 停止現有服務
echo [INFO] 停止現有服務...
docker-compose -f docker\docker-compose.yml down

REM 重新構建並啟動服務
echo [INFO] 重新構建並啟動服務...
docker-compose -f docker\docker-compose.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] 服務部署失敗
    pause
    exit /b 1
)

echo [SUCCESS] 服務重新部署完成！
echo.

REM 等待服務啟動
echo [INFO] 等待服務啟動...
timeout /t 10 /nobreak >nul

REM 顯示容器狀態
echo [容器狀態]
docker-compose -f docker\docker-compose.yml ps

echo.
echo [訪問地址]
echo   前端: http://localhost
echo   後端: http://localhost:8000
echo.

echo ==========================================
echo        重新部署完成！ 🎉
echo ==========================================

pause
exit /b 0

:error_dir
echo [ERROR] 無法找到專案目錄結構
echo 請確保您在 MBBuddy 專案根目錄中執行此腳本
pause
exit /b 1
