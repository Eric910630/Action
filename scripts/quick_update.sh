#!/bin/bash

# 快速更新脚本 - 在服务器上直接运行
# 使用方法：在服务器上执行：bash /root/Action/scripts/quick_update.sh

set -e

echo "=========================================="
echo "🚀 Action 快速更新"
echo "=========================================="
echo ""

# 进入项目目录
cd /root/Action || { echo "❌ 错误：无法进入 /root/Action 目录"; exit 1; }

# 1. 拉取最新代码
echo "📥 步骤1: 拉取最新代码..."
git pull origin main || { echo "❌ Git pull 失败"; exit 1; }
echo "✅ 代码拉取完成"
echo ""

# 2. 检查是否有部署脚本
if [ -f "scripts/deploy_to_production.sh" ]; then
    echo "📦 步骤2: 运行部署脚本..."
    bash scripts/deploy_to_production.sh
else
    echo "⚠️  未找到部署脚本，使用手动更新..."
    
    # 手动更新流程
    echo "📦 步骤2: 更新后端依赖..."
    cd backend
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        pip install -q -r requirements.txt
    fi
    
    # 检查数据库迁移
    if [ -f "migrations/versions" ]; then
        echo "🗄️  步骤3: 运行数据库迁移..."
        alembic upgrade head
    fi
    
    cd /root/Action
    
    # 重启服务
    echo "🔄 步骤4: 重启服务..."
    if systemctl list-units --type=service | grep -q "action-backend"; then
        sudo systemctl restart action-backend action-celery-worker action-celery-beat
        echo "✅ 服务重启完成"
    else
        echo "⚠️  未找到systemd服务，请手动重启"
    fi
    
    # 更新前端
    echo "🎨 步骤5: 更新前端..."
    cd frontend
    npm install --silent
    npm run build
    sudo cp -r dist/* /var/www/action-script/
    sudo chown -R www-data:www-data /var/www/action-script
    echo "✅ 前端更新完成"
fi

echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo ""
echo "🔍 验证步骤："
echo "  1. 检查服务状态: systemctl status action-backend"
echo "  2. 测试API: curl http://localhost:8001/health"
echo "  3. 访问前端: http://39.102.60.67"
echo ""

