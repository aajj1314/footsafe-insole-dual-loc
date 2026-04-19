#!/bin/bash
# 仅启动后端服务
# 用法: ./start-backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "启动后端服务..."

cd "$PROJECT_ROOT"

# 使用venv中的Python直接运行，避免source激活问题
nohup ./venv/bin/python3 -c "import uvicorn; from app.api import app; uvicorn.run(app, host='0.0.0.0', port=8090)" > backend.log 2>&1 &
BACKEND_PID=$!

echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"

sleep 3

if curl -s http://localhost:8090/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功!"
    echo "  - HTTP API: http://localhost:8090"
else
    echo "❌ 后端服务启动失败，请检查 backend.log"
    tail -5 backend.log 2>/dev/null || echo "无日志"
fi
