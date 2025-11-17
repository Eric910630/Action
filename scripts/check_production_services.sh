#!/bin/bash

# 生产服务器服务状态检查脚本

echo "=========================================="
echo "Action 生产环境服务状态"
echo "=========================================="
echo ""

# 检查服务状态
check_service() {
    local service=$1
    local name=$2
    if systemctl is-active --quiet $service; then
        local status=$(systemctl is-active $service)
        echo "✅ $name: $status"
        # 显示最近一条日志
        local recent_log=$(journalctl -u $service -n 1 --no-pager 2>/dev/null | tail -1)
        if [ ! -z "$recent_log" ]; then
            echo "   最近日志: ${recent_log:0:80}..."
        fi
    else
        echo "❌ $name: 未运行"
    fi
}

check_service redis-server "Redis"
check_service action-backend "后端服务 (8001)"
check_service action-celery-worker "Celery Worker"
check_service action-celery-beat "Celery Beat"
check_service nginx "Nginx (80)"

echo ""
echo "=========================================="
echo "端口监听检查"
echo "=========================================="

check_port() {
    local port=$1
    local name=$2
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "✅ $name (端口 $port): 监听中"
    else
        echo "❌ $name (端口 $port): 未监听"
    fi
}

check_port 6379 "Redis"
check_port 8001 "后端 API"
check_port 80 "Nginx"

echo ""
echo "=========================================="
echo "服务连接测试"
echo "=========================================="

# 测试 Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: 连接正常"
else
    echo "❌ Redis: 连接失败"
fi

# 测试后端 API
if response=$(curl -s http://localhost:8001/health 2>/dev/null); then
    if echo "$response" | grep -q "healthy\|running"; then
        echo "✅ 后端 API: 响应正常"
        echo "$response" | head -3
    else
        echo "⚠️  后端 API: 响应异常"
        echo "$response" | head -3
    fi
else
    echo "❌ 后端 API: 无响应"
fi

# 测试前端
if response=$(curl -s -I http://localhost/ 2>/dev/null); then
    if echo "$response" | grep -q "200\|301\|302"; then
        echo "✅ 前端页面: 可访问"
    else
        echo "⚠️  前端页面: 响应异常"
        echo "$response" | head -3
    fi
else
    echo "❌ 前端页面: 无响应"
fi

echo ""
echo "=========================================="
echo "进程检查"
echo "=========================================="

if pgrep -f "uvicorn.*8001" > /dev/null; then
    echo "✅ 后端进程: 运行中"
else
    echo "❌ 后端进程: 未运行"
fi

if pgrep -f "celery.*worker" > /dev/null; then
    echo "✅ Celery Worker 进程: 运行中"
else
    echo "❌ Celery Worker 进程: 未运行"
fi

if pgrep -f "celery.*beat" > /dev/null; then
    echo "✅ Celery Beat 进程: 运行中"
else
    echo "❌ Celery Beat 进程: 未运行"
fi

echo ""

