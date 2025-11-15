#!/bin/bash
# MBBuddy 本地開發環境設置腳本 (macOS/Linux)

set -e  # 遇到錯誤時停止執行

# 獲取腳本所在目錄的父目錄（專案根目錄）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 MBBuddy 本地開發環境設置"
echo "================================"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 檢查是否在專案根目錄
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 錯誤：無法找到 MBBuddy 專案結構"
    echo "當前目錄：$(pwd)"
    exit 1
fi

# 檢查 Python 是否安裝
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "❌ 錯誤：未找到 Python，請先安裝 Python 3.8+"
    exit 1
fi

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "📦 設置後端環境..."

# 創建虛擬環境
if [ ! -d ".venv" ]; then
    echo "  創建虛擬環境..."
    $PYTHON_CMD -m venv .venv
else
    echo "  虛擬環境已存在"
fi

# 啟動虛擬環境並安裝依賴
echo " 安裝後端依賴套件..."
source .venv/bin/activate
pip install -r backend/requirements.txt

echo "🎨 設置前端環境..."

# 檢查 Node.js 和 npm
if ! command -v npm >/dev/null 2>&1; then
    echo "❌ 錯誤：未找到 npm，請先安裝 Node.js"
    exit 1
fi

# 進入前端目錄並安裝依賴
cd frontend
echo "  安裝前端依賴套件..."
npm install

echo ""
echo "✅ 環境設置完成！"
echo ""
echo "🚀 現在可以啟動服務："
echo "   scripts/start_dev.sh        # 啟動開發服務"
echo "   scripts/stop_dev.sh         # 停止開發服務"
echo ""
