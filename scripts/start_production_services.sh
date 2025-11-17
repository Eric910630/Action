#!/bin/bash

# 生产服务器启动所有服务脚本
# 使用方法: bash start_production_services.sh

set -e

echo "=========================================="
echo "启动 Action 生产环境所有服务"
echo "=========================================="

cd /root/Action/backend
source venv/bin/activate

# 1. 启动 Redis（如果未运行）
echo ""
echo "1. 检查 Redis 服务..."
if ! systemctl is-active --quiet redis-server; then
    echo "   启动 Redis..."
    systemctl start redis-server
    systemctl enable redis-server
else
    echo "   ✅ Redis 已运行"
fi

# 2. 启动后端服务（使用 systemd）
echo ""
echo "2. 启动后端服务..."
if systemctl is-active --quiet action-backend; then
    echo "   ✅ 后端服务已运行，重启中..."
    systemctl restart action-backend
else
    echo "   启动后端服务..."
    systemctl start action-backend
    systemctl enable action-backend
fi

# 等待后端启动
sleep 3

# 3. 启动 Celery Worker
echo ""
echo "3. 启动 Celery Worker..."
if systemctl is-active --quiet action-celery-worker; then
    echo "   ✅ Celery Worker 已运行，重启中..."
    systemctl restart action-celery-worker
else
    echo "   启动 Celery Worker..."
    systemctl start action-celery-worker
    systemctl enable action-celery-worker
fi

# 4. 启动 Celery Beat
echo ""
echo "4. 启动 Celery Beat..."
if systemctl is-active --quiet action-celery-beat; then
    echo "   ✅ Celery Beat 已运行，重启中..."
    systemctl restart action-celery-beat
else
    echo "   启动 Celery Beat..."
    systemctl start action-celery-beat
    systemctl enable action-celery-beat
fi

# 5. 启动 Nginx
echo ""
echo "5. 检查 Nginx 服务..."
if ! systemctl is-active --quiet nginx; then
    echo "   启动 Nginx..."
    systemctl start nginx
    systemctl enable nginx
else
    echo "   ✅ Nginx 已运行"
fi

# 等待所有服务启动
sleep 2

# 6. 检查所有服务状态
echo ""
echo "=========================================="
echo "服务状态检查"
echo "=========================================="

check_service() {
    local service=$1
    local name=$2
    if systemctl is-active --quiet $service; then
        echo "✅ $name: 运行中"
    else
        echo "❌ $name: 未运行"
        systemctl status $service --no-pager -l | head -5
    fi
}

check_service redis-server "Redis"
check_service action-backend "后端服务"
check_service action-celery-worker "Celery Worker"
check_service action-celery-beat "Celery Beat"
check_service nginx "Nginx"

# 7. 测试服务连接
echo ""
echo "=========================================="
echo "服务连接测试"
echo "=========================================="

# 测试 Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 连接正常"
else
    echo "❌ Redis 连接失败"
fi

# 测试后端 API
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ 后端 API 响应正常"
    curl -s http://localhost:8001/health | head -1
else
    echo "❌ 后端 API 无响应"
fi

# 测试 Nginx
if curl -s -I http://localhost/ | grep -q "200\|301\|302"; then
    echo "✅ Nginx 前端服务正常"
else
    echo "⚠️  Nginx 响应异常（可能是前端文件问题）"
fi

echo ""
echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo ""
echo "查看服务日志:"
echo "  后端: journalctl -u action-backend -f"
echo "  Celery Worker: journalctl -u action-celery-worker -f"
echo "  Celery Beat: journalctl -u action-celery-beat -f"
echo "  Nginx: tail -f /var/log/nginx/error.log"
echo ""
echo "查看服务状态:"
echo "  systemctl status action-backend"
echo "  systemctl status action-celery-worker"
echo "  systemctl status action-celery-beat"
echo ""

