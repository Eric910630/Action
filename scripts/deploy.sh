#!/bin/bash
# Action项目云端部署脚本
# 使用方法：在服务器上执行此脚本

set -e

echo "=========================================="
echo "Action 项目云端部署脚本"
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
    curl -fsSL https://get.docker.com | bash
    systemctl start docker
    systemctl enable docker
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装Docker Compose..."
    apt-get update
    apt-get install docker-compose -y
fi

# 检查Nginx
if ! command -v nginx &> /dev/null; then
    echo "📦 安装Nginx..."
    apt-get install nginx -y
    systemctl start nginx
    systemctl enable nginx
fi

# 检查Certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 安装Certbot..."
    apt-get install certbot python3-certbot-nginx -y
fi

# 获取项目路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查.env文件
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    echo "⚠️  未找到 .env 文件"
    echo "正在创建默认配置文件..."
    cat > "$PROJECT_DIR/backend/.env" << EOF
# 数据库配置（Docker会自动配置）
DATABASE_URL=postgresql+psycopg2://vtics:vtics123@postgres:5432/vtics

# Redis配置（Docker会自动配置）
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# DeepSeek API配置（必须配置！）
DEEPSEEK_API_KEY=
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 其他配置
TRENDRADAR_USE_DIRECT_CRAWLER=true
FIRECRAWL_ENABLED=false
VIDEO_ANALYZER_USE_LOCAL=true

# 生产环境配置
ENVIRONMENT=production
DEBUG=false
EOF
    echo "✅ 已创建默认配置文件"
    echo "⚠️  请编辑 $PROJECT_DIR/backend/.env 并配置 DEEPSEEK_API_KEY"
    echo ""
    read -p "按Enter继续（配置完成后）..."
fi

# 进入docker目录
cd "$PROJECT_DIR/docker"

# 构建镜像
echo ""
echo "📦 构建Docker镜像（可能需要几分钟）..."
docker-compose build

# 启动服务
echo ""
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo ""
echo "检查服务状态..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 配置Nginx反向代理（参考部署指南）"
echo "2. 配置SSL证书：certbot --nginx -d 你的域名.com"
echo "3. 访问 http://你的服务器IP:3001 测试"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo ""

