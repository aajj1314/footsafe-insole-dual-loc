#!/bin/bash
# 生产环境部署脚本
# 用法: ./deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "  生产环境部署"
echo "=========================================="

# 环境检查
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
    echo "警告: .env.production 文件不存在，复制模板..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env.production"
    echo "请编辑 .env.production 文件配置生产环境参数"
fi

# 停止旧服务
echo "[1/4] 停止旧服务..."
if [ -f "$PROJECT_ROOT/.backend.pid" ] || [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    "$PROJECT_ROOT/stop.sh"
    sleep 2
fi

# 前端构建
echo "[2/4] 构建前端..."
cd "$PROJECT_ROOT/web"
npm install --production
npm run build

# 后端依赖检查
echo "[3/4] 检查后端依赖..."
cd "$PROJECT_ROOT"
source venv/bin/activate
pip install -r requirements.txt -q

# 启动服务
echo "[4/4] 启动服务..."
cd "$PROJECT_ROOT"
source venv/bin/activate
python3 -m app.main > logs/server.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"

cd "$PROJECT_ROOT/web"
# 使用 nginx 或静态文件服务，这里简化为后台运行 preview
npm run preview > /dev/null 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

echo ""
echo "=========================================="
echo "  部署完成!"
echo "  - HTTP API: http://localhost:8090"
echo "  - 前端:     http://localhost:4173 (生产构建)"
echo "  - UDP:      0.0.0.0:8888"
echo "  - TCP:      0.0.0.0:8889"
echo "  - 日志:     $PROJECT_ROOT/logs/server.log"
echo "=========================================="
