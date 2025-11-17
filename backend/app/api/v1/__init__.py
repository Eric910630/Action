"""
API v1 路由
"""
from fastapi import APIRouter

from app.api.v1.endpoints import hotspots, analysis, scripts, products, live_rooms, tasks, settings, feedback

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(hotspots.router, prefix="/hotspots", tags=["热点监控"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["视频拆解"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["脚本生成"])
api_router.include_router(products.router, prefix="/products", tags=["商品管理"])
api_router.include_router(live_rooms.router, prefix="/live-rooms", tags=["直播间管理"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务状态"])
api_router.include_router(settings.router, prefix="/settings", tags=["系统设置"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["用户反馈"])

