#!/bin/bash

# Action 本地开发环境停止脚本
# 停止：后端、前端、Celery Worker、Celery Beat

echo "=========================================="
echo "停止 Action 本地开发环境"
echo "=========================================="

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        rm logs/backend.pid
    fi
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        rm logs/frontend.pid
    fi
fi

# 停止 Celery Worker
if [ -f "logs/celery-worker.pid" ]; then
    CELERY_WORKER_PID=$(cat logs/celery-worker.pid)
    if ps -p $CELERY_WORKER_PID > /dev/null 2>&1; then
        echo "🛑 停止 Celery Worker (PID: $CELERY_WORKER_PID)..."
        kill $CELERY_WORKER_PID 2>/dev/null || true
        rm logs/celery-worker.pid
    fi
fi

# 停止 Celery Beat
if [ -f "logs/celery-beat.pid" ]; then
    CELERY_BEAT_PID=$(cat logs/celery-beat.pid)
    if ps -p $CELERY_BEAT_PID > /dev/null 2>&1; then
        echo "🛑 停止 Celery Beat (PID: $CELERY_BEAT_PID)..."
        kill $CELERY_BEAT_PID 2>/dev/null || true
        rm logs/celery-beat.pid
    fi
fi

# 清理进程（备用方案）
echo "清理残留进程..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "celery.*beat" 2>/dev/null || true

# 清理端口占用
echo "清理端口占用..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo ""
echo "✅ 所有服务已停止"
echo "=========================================="

