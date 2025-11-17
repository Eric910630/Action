#!/bin/bash

# 本地开发数据库设置脚本
# 使用Docker运行PostgreSQL，用于本地开发测试

set -e

echo "=========================================="
echo "设置本地开发数据库（PostgreSQL）"
echo "=========================================="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 数据库配置
DB_NAME="action_script_db"
DB_USER="action_scripter"
DB_PASSWORD="local_dev_password"
DB_PORT="5433"  # 使用5433避免与系统PostgreSQL冲突

# 检查容器是否已存在
if docker ps -a | grep -q "action-local-postgres"; then
    echo ""
    echo "发现已存在的PostgreSQL容器"
    read -p "是否删除并重新创建？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止并删除旧容器..."
        docker stop action-local-postgres > /dev/null 2>&1 || true
        docker rm action-local-postgres > /dev/null 2>&1 || true
    else
        echo "使用现有容器..."
        docker start action-local-postgres > /dev/null 2>&1
        echo "✅ 数据库容器已启动"
        exit 0
    fi
fi

# 启动PostgreSQL容器
echo ""
echo "启动PostgreSQL容器..."
docker run -d \
    --name action-local-postgres \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -e POSTGRES_DB=$DB_NAME \
    -p $DB_PORT:5432 \
    -v action_local_postgres_data:/var/lib/postgresql/data \
    postgres:15-alpine

echo "等待数据库启动..."
sleep 5

# 测试连接
echo ""
echo "测试数据库连接..."
for i in {1..30}; do
    if docker exec action-local-postgres pg_isready -U $DB_USER > /dev/null 2>&1; then
        echo "✅ 数据库连接成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 数据库启动超时"
        exit 1
    fi
    sleep 1
done

# 显示连接信息
echo ""
echo "=========================================="
echo "✅ 本地数据库已启动"
echo "=========================================="
echo ""
echo "数据库连接信息:"
echo "  主机: localhost"
echo "  端口: $DB_PORT"
echo "  数据库: $DB_NAME"
echo "  用户名: $DB_USER"
echo "  密码: $DB_PASSWORD"
echo ""
echo "连接URL:"
echo "  postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:$DB_PORT/$DB_NAME"
echo ""
echo "下一步:"
echo "  1. 更新 backend/.env 文件，使用上述连接信息"
echo "  2. 运行数据库迁移: cd backend && alembic upgrade head"
echo "  3. 初始化种子数据: python3 -m app.services.data.seed"
echo ""

