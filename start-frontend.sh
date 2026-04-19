#!/bin/bash
# 仅启动前端服务
# 用法: ./start-frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "启动前端服务 (端口: 5173)..."

cd "$PROJECT_ROOT/web"
npm run dev &
FRONTEND_PID=$!

echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "  - 前端: http://localhost:5173"
