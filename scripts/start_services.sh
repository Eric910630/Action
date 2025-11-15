#!/bin/bash

# 启动所有服务的脚本
# 用于真实环境人工测试

set -e

echo "=========================================="
echo "启动 Action 项目所有服务"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# 检查端口占用
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用，正在清理..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 清理端口
echo "检查端口占用..."
check_port 8001
check_port 3001
check_port 6379  # Redis
check_port 5672  # RabbitMQ (如果使用)

# 启动 Redis (如果需要)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "启动 Redis..."
    redis-server --daemonize yes 2>/dev/null || echo "Redis 可能已启动或未安装"
fi

# 启动 Celery Worker (后台)
echo "启动 Celery Worker..."
cd "$PROJECT_ROOT/backend"
if [ -f ".env" ]; then
    source .env 2>/dev/null || true
fi

# macOS 上使用 --pool=solo 避免 fork 问题
if [[ "$OSTYPE" == "darwin"* ]]; then
    CELERY_POOL="--pool=solo"
else
    CELERY_POOL=""
fi

# 启动 Celery Worker
cd "$PROJECT_ROOT/backend"
celery -A app.celery_app worker --loglevel=info $CELERY_POOL > "$PROJECT_ROOT/logs/celery.log" 2>&1 &
CELERY_PID=$!
echo "Celery Worker 已启动 (PID: $CELERY_PID, Pool: ${CELERY_POOL:-prefork})"
echo "$CELERY_PID" > "$PROJECT_ROOT/logs/celery.pid"

# 启动后端服务
echo "启动后端服务 (端口 8001)..."
cd "$PROJECT_ROOT/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "API文档: http://localhost:8001/docs"

# 等待后端启动
sleep 3

# 启动前端服务
echo "启动前端服务 (端口 3001)..."
cd "$PROJECT_ROOT/frontend"
npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "前端地址: http://localhost:3001"

# 保存PID到文件
echo "$BACKEND_PID" > "$PROJECT_ROOT/logs/backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/logs/frontend.pid"

echo ""
echo "=========================================="
echo "✅ 所有服务已启动"
echo "=========================================="
echo "后端 API: http://localhost:8001"
echo "API 文档: http://localhost:8001/docs"
echo "前端应用: http://localhost:3001"
echo ""
echo "日志文件:"
echo "  - 后端: logs/backend.log"
echo "  - 前端: logs/frontend.log"
echo ""
echo "停止服务: ./scripts/stop_services.sh"
echo "=========================================="

