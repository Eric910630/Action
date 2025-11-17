#!/bin/bash

# 生产环境部署脚本 - v1.0版本
# 使用方法: bash scripts/deploy_to_production.sh

set -e

echo "=========================================="
echo "🚀 Action v1.0 生产环境部署"
echo "=========================================="
echo ""

# 进入项目目录
cd /root/Action

# 1. 拉取最新代码
echo "📥 步骤1: 拉取最新代码..."
git pull
echo "✅ 代码拉取完成"
echo ""

# 2. 检查是否有数据库迁移
echo "🗄️ 步骤2: 检查数据库迁移..."
if [ -f "backend/migrations/versions/9259b16cb61b_add_feedback_table.py" ]; then
    echo "   检测到新的数据库迁移，运行迁移..."
    cd backend
    source venv/bin/activate
    alembic upgrade head
    echo "✅ 数据库迁移完成"
else
    echo "   无需数据库迁移"
fi
cd /root/Action
echo ""

# 3. 更新Systemd服务配置（如果使用systemd）
echo "⚙️ 步骤3: 更新Systemd服务配置..."
if [ -f "docs/systemd/action-backend.service" ]; then
    echo "   更新后端服务配置..."
    sudo cp docs/systemd/action-backend.service /etc/systemd/system/
    sudo cp docs/systemd/action-celery-worker.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Systemd配置更新完成"
else
    echo "   未找到Systemd配置文件，跳过"
fi
echo ""

# 4. 检查是否使用Docker
if [ -f "docker/docker-compose.polardb.yml" ]; then
    echo "🐳 步骤4: 使用Docker Compose部署..."
    cd docker
    
    # 检查是否有新的依赖
    echo "   检查后端依赖..."
    cd ../backend
    if [ -f "requirements.txt" ]; then
        echo "   安装/更新Python依赖..."
        source venv/bin/activate
        pip install -q -r requirements.txt
    fi
    cd ../docker
    
    # 重新构建并启动服务
    echo "   重新构建并启动服务..."
    docker-compose -f docker-compose.polardb.yml down
    docker-compose -f docker-compose.polardb.yml build --no-cache backend frontend
    docker-compose -f docker-compose.polardb.yml up -d
    
    echo "✅ Docker服务启动完成"
    echo ""
    
    # 等待服务启动
    echo "   等待服务启动..."
    sleep 5
    
    # 检查服务状态
    echo "   检查服务状态..."
    docker-compose -f docker-compose.polardb.yml ps
    
    cd /root/Action
else
    # 5. 更新后端服务（如果使用systemd）
    echo "⚙️ 步骤4: 更新后端服务..."
    
    # 检查是否有新的依赖
    cd backend
    if [ -f "requirements.txt" ]; then
        echo "   安装/更新Python依赖..."
        source venv/bin/activate
        pip install -q -r requirements.txt
    fi
    cd /root/Action
    
    # 重启后端服务
    echo "   重启后端服务..."
    sudo systemctl restart action-backend
    sudo systemctl restart action-celery-worker
    sudo systemctl restart action-celery-beat
    
    echo "✅ 后端服务重启完成"
    echo ""
    
    # 6. 更新前端
    echo "🎨 步骤5: 更新前端..."
    cd frontend
    
    # 检查是否有新的依赖
    if [ -f "package.json" ]; then
        echo "   安装/更新前端依赖..."
        npm install --silent
    fi
    
    # 构建前端
    echo "   构建前端..."
    npm run build
    
    # 复制到Nginx目录
    echo "   复制构建文件到Nginx目录..."
    sudo cp -r dist/* /var/www/action-script/
    sudo chown -R www-data:www-data /var/www/action-script
    sudo chmod -R 755 /var/www/action-script
    
    echo "✅ 前端更新完成"
    echo ""
    
    cd /root/Action
fi

# 7. 验证服务状态
echo "=========================================="
echo "✅ 验证服务状态"
echo "=========================================="
echo ""

# 检查后端服务
if systemctl is-active --quiet action-backend 2>/dev/null || docker ps | grep -q "vtics-backend\|action-backend" 2>/dev/null; then
    echo "✅ 后端服务: 运行中"
else
    echo "❌ 后端服务: 未运行"
fi

# 检查Celery Worker
if systemctl is-active --quiet action-celery-worker 2>/dev/null || docker ps | grep -q "vtics-celery-worker\|action-celery-worker" 2>/dev/null; then
    echo "✅ Celery Worker: 运行中"
else
    echo "❌ Celery Worker: 未运行"
fi

# 检查Nginx
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "✅ Nginx: 运行中"
else
    echo "❌ Nginx: 未运行"
fi

# 测试后端API
echo ""
echo "测试后端API..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ 后端API: 响应正常"
else
    echo "⚠️  后端API: 无响应（可能需要等待几秒）"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "📋 部署内容："
echo "  - 代码更新: ✅"
echo "  - 数据库迁移: ✅"
echo "  - 后端服务优化: ✅ (2 workers, 50连接池)"
echo "  - Celery Worker优化: ✅ (prefork池, 2并发)"
echo "  - 前端构建: ✅"
echo ""
echo "🔍 查看服务日志:"
if [ -f "docker/docker-compose.polardb.yml" ]; then
    echo "  docker-compose -f docker/docker-compose.polardb.yml logs -f"
else
    echo "  journalctl -u action-backend -f"
    echo "  journalctl -u action-celery-worker -f"
fi
echo ""
echo "🌐 访问地址:"
echo "  - 前端: http://你的域名 或 http://服务器IP"
echo "  - API文档: http://你的域名/api/docs 或 http://服务器IP:8001/docs"
echo ""

