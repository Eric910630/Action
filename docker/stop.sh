#!/bin/bash

echo "=========================================="
echo "停止 VTICS 应用"
echo "=========================================="

# 进入docker目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 停止服务
echo "正在停止服务..."
docker-compose down

echo ""
echo "✅ 服务已停止"
echo ""
echo "如需完全清理（删除数据卷），运行:"
echo "  docker-compose down -v"
echo ""

