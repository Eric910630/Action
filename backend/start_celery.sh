#!/bin/bash
# 启动Celery Worker

echo "启动Celery Worker..."

# 激活虚拟环境
source venv/bin/activate

# 启动Celery Worker
# macOS 上使用 --pool=solo 避免 fork 问题
# 在 macOS 上，fork() 与 Objective-C 运行时冲突会导致 SIGABRT
if [[ "$OSTYPE" == "darwin"* ]]; then
    celery -A app.celery_app worker --loglevel=info --pool=solo
else
    celery -A app.celery_app worker --loglevel=info
fi

