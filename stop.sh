#!/bin/bash
# 停止所有服务
# 用法: ./stop.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "停止所有服务..."

# 停止后端服务
if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        echo "后端服务已停止 (PID: $BACKEND_PID)"
    fi
    rm -f "$PROJECT_ROOT/.backend.pid"
fi

# 停止前端服务
if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        echo "前端服务已停止 (PID: $FRONTEND_PID)"
    fi
    rm -f "$PROJECT_ROOT/.frontend.pid"
fi

# 清理残留进程
pkill -f "uvicorn.*8090" 2>/dev/null || true
pkill -f "python3 -m app.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "所有服务已停止"
