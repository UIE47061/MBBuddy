@echo off
chcp 65001 >nul
REM MBBuddy 一鍵安裝腳本
REM 此腳本將自動完成以下步驟：
REM 1. 安裝 Docker Desktop
REM 2. 引導用戶下載並設置 AnythingLLM
REM 3. 獲取 API 金鑰並設置環境變數
REM 4. 更新 docker-compose.yml 配置
REM 5. 部署正式環境
REM 6. 啟用服務

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo     MBBuddy 一鍵安裝腳本 v1.0
echo ==========================================
echo.
echo 此腳本將引導您完成完整的 MBBuddy 安裝和設置
echo.
echo 安裝步驟：
echo   1. 檢查並安裝 Docker Desktop
echo   2. 引導下載和設置 AnythingLLM
echo   3. 獲取 API 金鑰
echo   4. 配置環境變數
echo   5. 部署 MBBuddy 服務
echo   6. 完成設置
echo.
pause

REM 獲取腳本目錄和專案根目錄
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM 切換到專案根目錄
cd /d "%PROJECT_ROOT%"

REM 檢查是否在正確的專案目錄
if not exist "backend" goto :error_dir
if not exist "frontend" goto :error_dir
if not exist "docker\docker-compose.yml" goto :error_dir

echo [SUCCESS] 專案目錄確認完成
echo.

REM 快速檢查是否已有運行的 MBBuddy 服務
echo [INFO] 檢查現有 MBBuddy 服務...

REM 先檢查 Docker 是否可用
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Docker 未安裝或未運行，將進行完整安裝流程
    echo.
    goto :install_docker
)

REM Docker 可用，檢查是否有運行中的 MBBuddy 服務
docker ps --filter "name=mbbuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}" 2>nul | findstr "mbbuddy" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] 發現正在運行的 MBBuddy 服務：
    docker ps --filter "name=mbbuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}" 2>nul
    echo.
    set /p skip_setup="檢測到 MBBuddy 已在運行，是否跳過安裝直接顯示訪問資訊? (y/n): "
    if /i "!skip_setup!"=="Y" (
        goto :show_access_info
    )
    echo [INFO] 將重新安裝和配置 MBBuddy...
    echo [INFO] 停止現有服務...
    docker-compose -f docker\docker-compose.yml down >nul 2>&1
    echo.
) else (
    echo [INFO] 未發現運行中的 MBBuddy 服務
    echo.
)

:install_docker

REM =====================================
REM 步驟 1: 安裝 Docker Desktop
REM =====================================
echo ==========================================
echo 步驟 1/6: 檢查並安裝 Docker Desktop
echo ==========================================
echo.

REM 首先檢查 Docker 是否已安裝
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker 已安裝
    docker --version
    echo.
    goto :docker_installed
)

REM Docker 未安裝,開始安裝流程
echo [INFO] Docker 未安裝，開始自動安裝...
echo.
call "%SCRIPT_DIR%install_docker.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Docker 安裝失敗
    echo 請手動安裝 Docker Desktop 後重新執行此腳本
    echo 下載地址: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Docker 安裝完成!
echo.
echo [重要提示]
echo Docker Desktop 已安裝,但需要完成以下步驟:
echo 1. 重新啟動電腦 (建議)
echo 2. 或手動啟動 Docker Desktop 應用程式
echo 3. 完成 Docker Desktop 的初始設定
echo 4. 確保 Docker Desktop 正在運行
echo 5. 重新執行此腳本以繼續 MBBuddy 安裝
echo.
set /p restart_now="是否現在重新啟動電腦? (y/n): "
if /i "!restart_now!"=="Y" (
    echo [INFO] 即將重新啟動電腦...
    shutdown /r /t 10 /c "重新啟動以完成 Docker 安裝"
    echo 10 秒後將重新啟動,按任意鍵取消...
    pause
    shutdown /a
)
echo [INFO] 請在重新啟動並啟動 Docker Desktop 後重新執行此腳本
pause
exit /b 0

:docker_installed

REM 檢查 Docker 服務是否正在執行
echo [INFO] 檢查 Docker 服務狀態...

REM 先嘗試簡單的 Docker 命令
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker 服務運行正常
    goto :docker_ready
)

REM 如果失敗，嘗試更詳細的檢測
docker version --format "{{{{.Server.Version}}}}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker 服務運行正常
    goto :docker_ready
)

REM Docker 服務未運行的處理
echo [WARNING] Docker 服務未運行
echo [INFO] 正在嘗試啟動 Docker Desktop...

REM 檢查 Docker Desktop 是否已經在運行
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>nul | find /I /N "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo [INFO] 已啟動 Docker Desktop...
) else (
    echo [INFO] Docker Desktop 已在運行，等待服務就緒...
)

echo [INFO] 等待 Docker 服務啟動...
set retry_count=0
:wait_docker
timeout /t 3 /nobreak >nul
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker 服務已啟動
    goto :docker_ready
)

set /a retry_count+=1
if !retry_count! lss 20 (
    echo [INFO] 等待中... (!retry_count!/20)
    goto :wait_docker
)

echo [ERROR] Docker 服務啟動超時
echo.
echo 可能的解決方案：
echo 1. 手動啟動 Docker Desktop
echo 2. 重新啟動 Docker Desktop
echo 3. 檢查 WSL2 是否正常運行 (wsl --status)
echo 4. 重新啟動電腦
echo.
set /p continue_anyway="Docker 服務可能未完全就緒，是否仍要繼續? (y/n): "
if /i "!continue_anyway!"=="Y" (
    echo [WARNING] 繼續執行，但可能會遇到 Docker 相關錯誤
    goto :docker_ready
)
echo [INFO] 請解決 Docker 問題後重新執行此腳本
pause
exit /b 1

:docker_ready
echo [SUCCESS] Docker 檢查完成
echo.

REM =====================================
REM 步驟 2: AnythingLLM 下載和設置指南
REM =====================================
echo ==========================================
echo 步驟 2/6: AnythingLLM 下載和設置
echo ==========================================
echo.
echo AnythingLLM 是 MBBuddy 的核心 AI 引擎，需要單獨下載和設置
echo.
echo [重要] 請按照以下步驟操作：
echo.
echo 1. 下載 AnythingLLM Desktop 版本
echo    下載地址: https://anythingllm.com/download
echo    選擇 "Desktop" 版本並下載適合您系統的版本
echo.
echo 2. 安裝並啟動 AnythingLLM
echo    - 執行下載的安裝程式
echo    - 完成安裝並啟動 AnythingLLM
echo    - 安裝時選擇 AnythingLLM NPU，模型請選擇自己喜歡的
echo    - 完成初始設定後 進入設定-系統管理-一般設定 開啟 `Enable network discovery`
echo.
echo 3. 確保 AnythingLLM 在 localhost:3001 運行
echo    (這是預設埠號，如果不同請記錄下來)
echo.

set /p llm_ready="完成 AnythingLLM 安裝並確認正在運行後，請輸入 y 繼續: "
if /i not "!llm_ready!"=="Y" (
    echo  [INFO] 請完成 AnythingLLM 設置後重新執行此腳本
    pause
    exit /b 0
)

REM 檢查 AnythingLLM 是否可訪問
echo [INFO] 檢查 AnythingLLM 連線...
curl -s http://localhost:3001 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 無法連接到 AnythingLLM (localhost:3001)
    echo.
    echo 請確認：
    echo 1. AnythingLLM 已正確安裝並啟動
    echo 2. 服務運行在 localhost:3001 (預設埠號)
    echo 3. 防火牆未阻止連線
    echo.
    set /p continue_anyway="是否仍要繼續? (y/n): "
    if /i not "!continue_anyway!"=="Y" (
        echo [INFO] 請檢查 AnythingLLM 設置後重新執行此腳本
        pause
        exit /b 0
    )
) else (
    echo [SUCCESS] AnythingLLM 連線檢查完成
)

echo.

REM =====================================
REM 步驟 3: 獲取 API 金鑰
REM =====================================
echo ==========================================
echo 步驟 3/6: 獲取 AnythingLLM API 金鑰
echo ==========================================
echo.
echo 現在需要獲取 AnythingLLM 的 API 金鑰
echo.
echo [重要] 請按照以下步驟獲取 API 金鑰：
echo.
echo 1. 打開 AnythingLLM 介面
echo.
echo 2. 導航到設置頁面
echo    通常在側邊欄或右上角的設置選單中
echo.
echo 3. 尋找 "API Keys" 或 "API 金鑰" 頁面
echo.
echo 4. 創建一個新的 API 金鑰
echo    - 點擊 "Create new API Key" 或類似按鈕
echo    - 複製生成的 API 金鑰
echo.
echo 5. API 金鑰格式通常類似: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
echo.

echo.
echo 請在上述獲取 API 金鑰後回到此處
echo.

:input_api_key
set "api_key="
set /p api_key="請輸入您的 AnythingLLM API 金鑰: "

if "!api_key!"=="" (
    echo [ERROR] API 金鑰不能為空，請重新輸入
    goto :input_api_key
)

REM 簡單驗證 API 金鑰格式
echo !api_key! | findstr /r "^[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}-[A-Z0-9]\{3,\}$" >nul
if %errorlevel% neq 0 (
    echo [WARNING] API 金鑰格式可能不正確
    echo 預期格式: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
    echo 您輸入的: !api_key!
    echo.
    set /p confirm_key="是否確認使用此金鑰? (y/n): "
    if /i not "!confirm_key!"=="Y" (
        goto :input_api_key
    )
)

echo [SUCCESS] API 金鑰已接收: !api_key!
echo.

REM =====================================
REM 步驟 4: 設置環境變數並更新配置
REM =====================================
echo ==========================================
echo 步驟 4/6: 設置環境變數並更新配置
echo ==========================================
echo.

REM 設置環境變數
echo [INFO] 設置系統環境變數 ANYTHINGLLM_API_KEY...
setx ANYTHINGLLM_API_KEY "!api_key!" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] 環境變數設置成功
) else (
    echo [WARNING] 環境變數設置可能失敗，將直接更新配置檔案
)

REM 設置本次會話的環境變數
set ANYTHINGLLM_API_KEY=!api_key!

REM 更新配置檔案...

REM 創建 .env 檔案
echo [INFO] 創建環境變數檔案 (.env)...
(
echo # MBBuddy 環境變數配置
echo # 此檔案由一鍵安裝腳本自動生成
echo.
echo # AnythingLLM 配置
echo ANYTHINGLLM_BASE_URL=http://host.docker.internal:3001
echo ANYTHINGLLM_API_KEY=!api_key!
echo ANYTHINGLLM_WORKSPACE_SLUG=MBBuddy
echo ANYTHINGLLM_DEBUG_THINKING=false
echo.
echo # 服務配置
echo PYTHONPATH=/app
) > ".env"

if %errorlevel% equ 0 (
    echo [SUCCESS] .env 檔案創建完成
    echo [INFO] docker-compose.yml 將從 .env 檔案讀取環境變數
) else (
    echo [ERROR] .env 檔案創建失敗
    pause
    exit /b 1
)

echo.

REM =====================================
REM 步驟 5: 部署正式環境
REM =====================================
echo ==========================================
echo 步驟 5/6: 部署 MBBuddy 正式環境
echo ==========================================
echo.

echo [INFO] 正在停止現有容器 (如果有的話)...
docker-compose -f docker\docker-compose.yml down >nul 2>&1

echo [INFO] 構建並啟動 MBBuddy 服務...
echo 這可能需要幾分鐘時間，請耐心等待...
echo.

REM 設置當前會話的環境變數以確保 docker-compose 能正確讀取
set ANYTHINGLLM_API_KEY=!api_key!

docker-compose -f docker\docker-compose.yml up -d --build
if %errorlevel% neq 0 (
    echo [ERROR] MBBuddy 服務部署失敗
    echo.
    echo 可能的解決方案：
    echo 1. 檢查 Docker Desktop 是否正常運行
    echo 2. 檢查防火牆設置
    echo 3. 檢查磁碟空間是否充足
    echo 4. 重新啟動 Docker Desktop
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] MBBuddy 服務部署完成！
echo.

REM 等待服務啟動
echo [INFO] 等待服務完全啟動...
timeout /t 15 /nobreak >nul

REM =====================================
REM 步驟 6: 驗證安裝並顯示訪問資訊
REM =====================================
:show_access_info
echo ==========================================
echo 步驟 6/6: 驗證安裝並顯示訪問資訊
echo ==========================================
echo.

REM 檢查容器狀態
echo [容器狀態]
docker ps --filter "name=MBBuddy" --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}" 2>nul
if %errorlevel% neq 0 (
    echo 無法檢查容器狀態，請確認 Docker 服務正常運行
)

echo.

REM 顯示訪問資訊
echo ==========================================
echo           🎉 安裝完成！🎉
echo ==========================================
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
echo   API 金鑰: !api_key!
echo.

echo [控制指令]
echo   啟動服務: docker-compose -f docker\docker-compose.yml up -d
echo   停止服務: docker-compose -f docker\docker-compose.yml down
echo   重啟服務: docker-compose -f docker\docker-compose.yml restart
echo   查看日誌: docker-compose -f docker\docker-compose.yml logs -f
echo   查看狀態: docker-compose -f docker\docker-compose.yml ps
echo.

echo [使用說明]
echo 1. 在瀏覽器中打開前端地址開始使用 MBBuddy
echo 2. 確保 AnythingLLM 保持運行狀態
echo 3. 如需停止服務，使用上述停止指令
echo 4. 重新啟動電腦後，可能需要手動啟動 Docker Desktop 和 AnythingLLM
echo.

echo [後續維護]
echo - 如需更新 API 金鑰，請重新執行此腳本
echo - 如需重新部署，請使用控制指令
echo - 技術支援請查看專案文檔
echo.

REM 提供快捷操作
set /p open_browser="是否現在打開 MBBuddy 前端? (y/n): "
if /i "!open_browser!"=="Y" (
    start http://localhost
)

echo.
echo ==========================================
echo        MBBuddy 一鍵安裝完成！ 🚀
echo ==========================================
echo.
echo 感謝使用 MBBuddy！
echo.
pause

exit /b 0

REM =====================================
REM 錯誤處理
REM =====================================
:error_dir
echo [ERROR] 無法找到專案目錄結構
echo 請確保您在 MBBuddy 專案根目錄中執行此腳本
echo.
echo 預期的目錄結構：
echo - package.json
echo - backend/
echo - frontend/
echo - docker/docker-compose.yml
echo.
pause
exit /b 1
