#!/bin/bash

# 停止所有服务的脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "停止 Action 项目所有服务"
echo "=========================================="

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        rm logs/backend.pid
    fi
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        rm logs/frontend.pid
    fi
fi

# 停止 Celery Worker
if [ -f "logs/celery.pid" ]; then
    CELERY_PID=$(cat logs/celery.pid)
    if ps -p $CELERY_PID > /dev/null 2>&1; then
        echo "停止 Celery Worker (PID: $CELERY_PID)..."
        kill $CELERY_PID 2>/dev/null || true
        rm logs/celery.pid
    fi
fi

# 清理端口占用
echo "清理端口占用..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

echo "✅ 所有服务已停止"
echo "=========================================="

