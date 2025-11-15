#!/bin/bash
# MBBuddy 本地開發服務啟動腳本 (macOS/Linux)

set -e

# 獲取腳本所在目錄的父目錄（專案根目錄）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 啟動 MBBuddy 本地開發服務"
echo "================================"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 檢查是否在專案根目錄
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 錯誤：無法找到 MBBuddy 專案結構"
    echo "當前目錄：$(pwd)"
    exit 1
fi

# 檢查虛擬環境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 錯誤：找不到虛擬環境，請先執行 scripts/setup_dev.sh"
    exit 1
fi

echo "📡 啟動後端服務..."
# 在背景啟動後端服務
source .venv/bin/activate
nohup uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "  後端服務已啟動 (PID: $BACKEND_PID)"

echo "🎨 啟動前端服務..."
# 在背景啟動前端服務
cd frontend
nohup npm run dev -- --host > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo " 前端服務已啟動 (PID: $FRONTEND_PID)"

cd ..

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 檢查服務狀態
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ 後端服務運行正常"
else
    echo "❌ 後端服務啟動失敗，請檢查 backend.log"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ 前端服務運行正常"
else
    echo "❌ 前端服務啟動失敗，請檢查 frontend.log"
fi

echo ""
echo "📱 區域網路訪問："
echo "   請執行以下命令查詢您的 IP："
echo "   ifconfig | grep \"inet \" | grep -v 127.0.0.1"
echo "   然後訪問 http://[您的IP]:5173"
echo ""
echo "🔍 查看日誌："
echo "   後端日誌：tail -f backend.log"
echo "   前端日誌：tail -f frontend.log"
echo ""
echo "🛑 停止服務："
echo "   ./scripts/stop_dev.sh"
echo ""
