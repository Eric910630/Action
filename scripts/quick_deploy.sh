#!/bin/bash

# 快速部署脚本
# 用于在云服务器上快速部署Action项目

set -e

echo "=========================================="
echo "Action 项目快速部署脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "📦 安装Docker..."
    curl -fsSL https://get.docker.com | sh
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 检查Git
if ! command -v git &> /dev/null; then
    echo "📦 安装Git..."
    apt update
    apt install -y git
fi

# 检查项目目录
if [ ! -d "/root/Action" ]; then
    echo "❌ 项目目录不存在，请先上传代码或克隆Git仓库"
    echo ""
    echo "方式1：克隆Git仓库"
    echo "  cd /root"
    echo "  git clone 你的Git仓库地址 Action"
    echo ""
    echo "方式2：使用SCP上传"
    echo "  # 在本地执行"
    echo "  scp -r ~/Desktop/Action root@服务器IP:/root/"
    exit 1
fi

cd /root/Action

# 检查.env文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到 backend/.env 文件"
    echo "请先配置环境变量："
    echo "  cd /root/Action/backend"
    echo "  nano .env"
    echo ""
    echo "必需配置："
    echo "  - DATABASE_URL (PolarDB连接信息)"
    echo "  - DEEPSEEK_API_KEY"
    echo "  - REDIS_HOST, REDIS_PORT"
    exit 1
fi

# 选择部署配置
echo ""
echo "选择部署配置："
echo "1. 使用PolarDB（推荐）"
echo "2. 使用Docker PostgreSQL"
read -p "请选择 (1/2): " choice

cd docker

if [ "$choice" == "1" ]; then
    echo "🚀 使用PolarDB配置部署..."
    docker-compose -f docker-compose.polardb.yml up -d
    COMPOSE_FILE="docker-compose.polardb.yml"
else
    echo "🚀 使用Docker PostgreSQL配置部署..."
    docker-compose up -d
    COMPOSE_FILE="docker-compose.yml"
fi

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 初始化数据库
echo ""
echo "📦 初始化数据库..."
docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head || echo "⚠️  数据库迁移可能已是最新版本"

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "服务地址："
echo "  - 前端: http://服务器IP:3001"
echo "  - 后端API: http://服务器IP:8001"
echo "  - API文档: http://服务器IP:8001/docs"
echo ""
echo "查看日志："
echo "  cd /root/Action/docker"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "停止服务："
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
echo "重启服务："
echo "  docker-compose -f $COMPOSE_FILE restart"
echo ""

