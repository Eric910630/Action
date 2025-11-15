#!/bin/bash
# 启动Celery Beat

echo "启动Celery Beat..."

# 激活虚拟环境
source venv/bin/activate

# 启动Celery Beat
celery -A app.celery_app beat --loglevel=info

