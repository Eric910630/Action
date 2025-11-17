#!/bin/bash

# Action 本地开发环境完整启动脚本
# 启动：后端、前端、Celery Worker、Celery Beat

set -e

echo "=========================================="
echo "启动 Action 本地开发环境"
echo "=========================================="

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 确保 logs 目录存在
mkdir -p logs

# 检查端口占用并清理
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用，正在清理..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

echo ""
echo "检查端口占用..."
check_port 8000  # 后端
check_port 3000  # 前端
check_port 6379  # Redis（如果本地运行）

# 检查环境
echo ""
echo "检查环境..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 检查后端虚拟环境
cd backend
if [ ! -d "venv" ]; then
    echo "📦 创建后端虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，请先配置环境变量"
    echo "   参考: backend/.env.example"
fi

# 检查 Redis（可选，如果使用本地 Redis）
if ! pgrep -x "redis-server" > /dev/null 2>&1; then
    echo "⚠️  Redis 未运行（如果使用本地 Redis，请先启动）"
fi

# 启动 Celery Worker
echo ""
echo "🚀 启动 Celery Worker..."
# macOS 上使用 --pool=solo 避免 fork 问题
if [[ "$OSTYPE" == "darwin"* ]]; then
    CELERY_POOL="--pool=solo"
else
    CELERY_POOL=""
fi

celery -A app.celery_app worker --loglevel=info $CELERY_POOL > ../logs/celery-worker.log 2>&1 &
CELERY_WORKER_PID=$!
echo "   Celery Worker 已启动 (PID: $CELERY_WORKER_PID)"
echo "$CELERY_WORKER_PID" > ../logs/celery-worker.pid

# 启动 Celery Beat
echo ""
echo "🚀 启动 Celery Beat..."
celery -A app.celery_app beat --loglevel=info > ../logs/celery-beat.log 2>&1 &
CELERY_BEAT_PID=$!
echo "   Celery Beat 已启动 (PID: $CELERY_BEAT_PID)"
echo "$CELERY_BEAT_PID" > ../logs/celery-beat.pid

# 启动后端服务
echo ""
echo "🚀 启动后端服务 (端口 8000)..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端服务已启动 (PID: $BACKEND_PID)"
echo "$BACKEND_PID" > ../logs/backend.pid

# 等待后端启动
sleep 3

# 启动前端服务
echo ""
echo "🚀 启动前端服务 (端口 3000)..."
cd ../frontend

# 检查前端依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端服务已启动 (PID: $FRONTEND_PID)"
echo "$FRONTEND_PID" > ../logs/frontend.pid

# 等待前端启动
sleep 2

echo ""
echo "=========================================="
echo "✅ 所有服务已启动"
echo "=========================================="
echo ""
echo "服务地址:"
echo "  后端 API:     http://localhost:8000"
echo "  API 文档:     http://localhost:8000/docs"
echo "  前端应用:     http://localhost:3000"
echo ""
echo "进程 PID:"
echo "  后端:         $BACKEND_PID"
echo "  前端:         $FRONTEND_PID"
echo "  Celery Worker: $CELERY_WORKER_PID"
echo "  Celery Beat:   $CELERY_BEAT_PID"
echo ""
echo "查看日志:"
echo "  后端:         tail -f logs/backend.log"
echo "  前端:         tail -f logs/frontend.log"
echo "  Celery Worker: tail -f logs/celery-worker.log"
echo "  Celery Beat:   tail -f logs/celery-beat.log"
echo ""
echo "停止服务:       ./stop_local_dev.sh"
echo "=========================================="
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID $CELERY_WORKER_PID $CELERY_BEAT_PID 2>/dev/null; rm -f logs/*.pid; echo '✅ 所有服务已停止'; exit" INT TERM

wait

