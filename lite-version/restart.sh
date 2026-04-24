#!/bin/bash
# 重启所有服务
# 用法: ./restart.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "重启所有服务..."

# 停止服务
if [ -f "$PROJECT_ROOT/.backend.pid" ] || [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    "$PROJECT_ROOT/stop.sh"
fi

# 等待端口释放
sleep 2

# 启动服务
"$PROJECT_ROOT/start.sh"

echo "所有服务已重启"
