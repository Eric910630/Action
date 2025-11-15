#!/bin/bash

echo "=========================================="
echo "启动 VTICS 应用"
echo "=========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker Desktop"
    echo "   下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

# 进入docker目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查.env文件
if [ ! -f "../backend/.env" ]; then
    echo "⚠️  未找到 backend/.env 文件"
    echo "   正在创建默认配置文件..."
    cat > ../backend/.env << EOF
# 数据库配置（Docker会自动配置）
DATABASE_URL=postgresql+psycopg2://vtics:vtics123@postgres:5432/vtics

# Redis配置（Docker会自动配置）
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# DeepSeek API配置（需要在设置中配置）
DEEPSEEK_API_KEY=
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 其他配置
TRENDRADAR_USE_DIRECT_CRAWLER=true
FIRECRAWL_ENABLED=false
VIDEO_ANALYZER_USE_LOCAL=true
EOF
    echo "✅ 已创建默认配置文件"
    echo "   请在应用启动后，通过设置页面配置DeepSeek API Key"
fi

# 构建并启动
echo ""
echo "📦 构建镜像（首次运行可能需要几分钟）..."
docker-compose build

echo ""
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动（约30秒）..."
sleep 30

# 检查服务状态
echo ""
echo "检查服务状态..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ 服务已启动！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  🌐 前端页面: http://localhost:3001"
echo "  📚 API文档: http://localhost:8001/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
echo "⚠️  首次使用请："
echo "  1. 访问 http://localhost:3001"
echo "  2. 点击右上角设置图标"
echo "  3. 进入'系统设置'标签"
echo "  4. 配置DeepSeek API Key"
echo ""

