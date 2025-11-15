#!/bin/bash

# VTICS 开发环境启动脚本

echo "=========================================="
echo "VTICS 开发环境启动"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python 3.10+"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js 16+"
    exit 1
fi

# 检查数据库迁移
echo ""
echo "📦 检查数据库迁移..."
cd backend
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，请先配置环境变量"
    echo "   参考: backend/.env.example"
fi

# 检查后端依赖
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 安装后端依赖..."
    pip install -r requirements.txt
fi

# 检查前端依赖
echo ""
echo "📦 检查前端依赖..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动服务
echo ""
echo "=========================================="
echo "启动服务"
echo "=========================================="
echo ""
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "前端页面: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 启动后端（后台运行）
echo "🚀 启动后端API..."
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端..."
cd ../frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# 保存PID到文件
echo $BACKEND_PID > ../logs/backend.pid
echo $FRONTEND_PID > ../logs/frontend.pid

echo ""
echo "✅ 服务已启动！"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务: ./stop_dev.sh"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f ../logs/*.pid; echo '服务已停止'; exit" INT TERM

wait

