"""
Celery应用配置
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "vtics",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.hotspot.tasks",
        "app.services.analysis.tasks",
        "app.services.script.tasks",
        "app.services.data.tasks",
    ]
)

# Celery配置
import sys
import platform

# macOS 上使用 solo pool 避免 fork 问题
# 在 macOS 上，fork() 与 Objective-C 运行时冲突会导致 SIGABRT
if platform.system() == "Darwin":  # macOS
    worker_pool = "solo"
else:
    worker_pool = "prefork"  # Linux/其他系统使用 prefork

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟
    # macOS 上使用 solo pool
    worker_pool=worker_pool,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    "fetch-daily-hotspots": {
        "task": "app.services.hotspot.tasks.fetch_daily_hotspots",
        "schedule": crontab(hour=8, minute=0),  # 每日8:00
    },
    "push-hotspots-to-feishu": {
        "task": "app.services.hotspot.tasks.push_hotspots_to_feishu",
        "schedule": crontab(hour=9, minute=0),  # 每日9:00
    },
    "cleanup-old-data": {
        "task": "app.services.data.tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),  # 每日2:00
    },
}

