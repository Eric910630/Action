#!/bin/bash

# 本地PostgreSQL数据库设置脚本（不使用Docker）

set -e

echo "=========================================="
echo "设置本地PostgreSQL数据库"
echo "=========================================="

# 数据库配置
DB_NAME="action_script_db"
DB_USER="action_scripter"
DB_PASSWORD="local_dev_password"

# 检查PostgreSQL是否运行
echo ""
echo "检查PostgreSQL服务..."
if ! psql -U $(whoami) -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "PostgreSQL未运行，尝试启动..."
    brew services start postgresql@14 2>/dev/null || {
        echo "❌ 无法启动PostgreSQL，请手动启动："
        echo "   brew services start postgresql@14"
        exit 1
    }
    echo "等待PostgreSQL启动..."
    sleep 3
fi

# 检查数据库是否已存在
echo ""
echo "检查数据库..."
if psql -U $(whoami) -d postgres -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "数据库 $DB_NAME 已存在"
    read -p "是否删除并重新创建？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧数据库..."
        psql -U $(whoami) -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
        psql -U $(whoami) -d postgres -c "DROP USER IF EXISTS $DB_USER;"
    else
        echo "使用现有数据库"
        exit 0
    fi
fi

# 创建用户和数据库
echo ""
echo "创建数据库用户和数据库..."
psql -U $(whoami) -d postgres <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

echo "✅ 数据库和用户创建成功"
echo ""
echo "=========================================="
echo "数据库连接信息"
echo "=========================================="
echo "主机: localhost"
echo "端口: 5432"
echo "数据库: $DB_NAME"
echo "用户名: $DB_USER"
echo "密码: $DB_PASSWORD"
echo ""
echo "连接URL:"
echo "  postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "下一步:"
echo "  1. 更新 backend/.env 文件，使用上述连接信息"
echo "  2. 运行数据库迁移: cd backend && alembic upgrade head"
echo "  3. 初始化种子数据: python3 -m app.services.data.seed"
echo ""

