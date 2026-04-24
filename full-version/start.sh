#!/bin/bash
# 一键启动所有服务（后端 + 前端）
# 用法: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "  足安智能防走失系统 - 启动服务"
echo "=========================================="

# 清理旧进程
echo "清理旧进程..."
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# 前端服务
echo "[1/2] 启动前端服务 (端口: 8000)..."
cd "$PROJECT_ROOT/web"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  前端服务已启动 (PID: $FRONTEND_PID)"

# 后端服务 - 使用venv中的Python直接运行
echo "[2/2] 启动后端服务 (端口: 8090, 8888 UDP, 8889 TCP)..."
cd "$PROJECT_ROOT"
nohup ./venv/bin/python3 -c "import uvicorn; from app.api import app; uvicorn.run(app, host='0.0.0.0', port=8090)" > backend.log 2>&1 &
BACKEND_PID=$!
echo "  后端服务已启动 (PID: $BACKEND_PID)"

# 保存 PIDs
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

# 等待服务启动
sleep 4

# 检查服务状态
if curl -s http://localhost:8090/api/health > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "  ✅ 所有服务已成功启动!"
    echo "  - 前端:      http://localhost:8000"
    echo "  - 后端API:   http://localhost:8090"
    echo "  - UDP:       0.0.0.0:8888"
    echo "  - TCP:       0.0.0.0:8889"
    echo "=========================================="
    echo ""
    echo "演示账号: admin / admin"
else
    echo ""
    echo "❌ 后端服务启动失败，请检查 backend.log"
    echo ""
    echo "最近错误日志:"
    tail -10 backend.log 2>/dev/null || echo "无日志"
fi
