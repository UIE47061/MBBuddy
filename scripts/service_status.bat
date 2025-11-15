@echo off
chcp 65001 >nul
REM MBBuddy 服務狀態檢查和控制腳本
REM 用於已完成安裝的 MBBuddy 環境

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo      MBBuddy 服務狀態檢查
echo ==========================================
echo.

REM 獲取腳本目錄和專案根目錄
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM 切換到專案根目錄
cd /d "%PROJECT_ROOT%"

REM 檢查 Docker 狀態
echo [INFO] 檢查 Docker 狀態...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 服務未運行，請先啟動 Docker Desktop
    pause
    exit /b 1
)

echo [SUCCESS] Docker 檢查完成
echo.

REM 檢查 MBBuddy 容器狀態
echo [INFO] 檢查 MBBuddy 服務狀態...
docker ps --filter "name=mbbuddy" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr "mbbuddy" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] MBBuddy 服務正在運行
    echo.
    echo [容器狀態]
    docker ps --filter "name=mbbuddy" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    goto :show_access_info
) else (
    echo [INFO] MBBuddy 服務未運行
    echo.
    echo 選擇操作：
    echo   1. 啟動 MBBuddy 服務
    echo   2. 重新部署 MBBuddy 服務
    echo   3. 只顯示訪問資訊
    echo   4. 退出
    echo.
    set /p user_choice="請選擇 (1-4): "
    
    if "!user_choice!"=="1" goto :start_services
    if "!user_choice!"=="2" goto :redeploy_services
    if "!user_choice!"=="3" goto :show_access_info
    if "!user_choice!"=="4" exit /b 0
    
    echo [ERROR] 無效選擇
    pause
    exit /b 1
)

:start_services
echo.
echo [INFO] 啟動 MBBuddy 服務...

REM 讀取環境變數
if exist ".env" (
    for /f "tokens=2 delims==" %%a in ('findstr "ANYTHINGLLM_API_KEY" .env 2^>nul') do (
        set "ANYTHINGLLM_API_KEY=%%a"
    )
)

if exist "docker\docker-compose.yml" (
    docker-compose -f docker\docker-compose.yml up -d
) else (
    echo [ERROR] 找不到 docker-compose.yml 檔案
    pause
    exit /b 1
)

if %errorlevel% equ 0 (
    echo [SUCCESS] 服務啟動完成
    timeout /t 5 /nobreak >nul
    goto :show_access_info
) else (
    echo [ERROR] 服務啟動失敗
    pause
    exit /b 1
)

:redeploy_services
echo.
echo [INFO] 重新部署 MBBuddy 服務...

REM 讀取環境變數
if exist ".env" (
    for /f "tokens=2 delims==" %%a in ('findstr "ANYTHINGLLM_API_KEY" .env 2^>nul') do (
        set "ANYTHINGLLM_API_KEY=%%a"
    )
)

if exist "docker\docker-compose.yml" (
    docker-compose -f docker\docker-compose.yml down
    docker-compose -f docker\docker-compose.yml up -d --build
) else (
    echo [ERROR] 找不到 docker-compose.yml 檔案
    pause
    exit /b 1
)

if %errorlevel% equ 0 (
    echo [SUCCESS] 重新部署完成
    timeout /t 10 /nobreak >nul
    goto :show_access_info
) else (
    echo [ERROR] 重新部署失敗
    pause
    exit /b 1
)

:show_access_info
echo.
echo ==========================================
echo           🎉 MBBuddy 服務資訊 🎉
echo ==========================================
echo.

REM 顯示容器最終狀態
echo [容器狀態]
docker ps --filter "name=MBBuddy" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>nul

echo.
echo [訪問地址]

REM 獲取本機 IP 地址
echo 本機訪問：
echo   前端: http://localhost
echo   後端: http://localhost:8000
echo.

echo 區域網訪問：
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "ip=%%b"
        set "ip=!ip: =!"
        if not "!ip!"=="127.0.0.1" (
            echo   前端: http://!ip!
            echo   後端: http://!ip!:8000
            echo.
        )
    )
)

echo [AnythingLLM 狀態]
echo   地址: http://localhost:3001
if exist ".env" (
    for /f "tokens=2 delims==" %%a in ('findstr "ANYTHINGLLM_API_KEY" .env 2^>nul') do (
        set "api_key=%%a"
        echo   API 金鑰: !api_key!
    )
) else (
    echo   API 金鑰: 請檢查 .env 檔案
)
echo.

echo [快速控制指令]
echo   啟動服務: docker-compose -f docker\docker-compose.yml up -d
echo   停止服務: docker-compose -f docker\docker-compose.yml down
echo   重啟服務: docker-compose -f docker\docker-compose.yml restart
echo   查看日誌: docker-compose -f docker\docker-compose.yml logs -f
echo   查看狀態: docker-compose -f docker\docker-compose.yml ps
echo.

echo [快捷腳本]
echo   服務狀態: scripts\service_status.bat
echo   重新部署: scripts\redeploy.bat
echo   一鍵安裝: scripts\one_click_install.bat
echo.

REM 提供快捷操作
set /p open_browser="是否現在打開 MBBuddy 前端? (Y/N): "
if /i "!open_browser!"=="Y" (
    start http://localhost
)

echo.
echo ==========================================
echo        MBBuddy 服務檢查完成！ 🚀
echo ==========================================

pause
exit /b 0
