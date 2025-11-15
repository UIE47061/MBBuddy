#!/bin/bash
# MBBuddy 本地開發服務停止腳本 (macOS/Linux)

# 獲取腳本所在目錄的父目錄（專案根目錄）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛑 停止 MBBuddy 本地開發服務"
echo "================================"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 停止後端服務
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止後端服務 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
        echo "✅ 後端服務已停止"
    else
        echo "ℹ️  後端服務未運行"
        rm -f backend.pid
    fi
else
    echo "ℹ️  找不到後端服務 PID 文件"
fi

# 停止前端服務
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 停止前端服務 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm frontend.pid
        echo "✅ 前端服務已停止"
    else
        echo "ℹ️  前端服務未運行"
        rm -f frontend.pid
    fi
else
    echo "ℹ️  找不到前端服務 PID 文件"
fi

# 清理日誌文件（可選）
read -p "🗑️  是否清理日誌文件？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f backend.log frontend.log
    echo "✅ 日誌文件已清理"
fi

echo ""
echo "✅ 所有服務已停止"
echo ""
