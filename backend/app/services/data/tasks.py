"""
数据管理定时任务
"""
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.hotspot import Hotspot
from loguru import logger
from datetime import datetime, timedelta


@celery_app.task
def cleanup_old_data():
    """清理7天前的热点数据"""
    logger.info("开始清理过期数据")
    
    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=7)
        
        try:
            # 删除7天前的热点数据
            deleted_count = db.query(Hotspot).filter(
                Hotspot.created_at < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"成功清理 {deleted_count} 条过期热点数据")
            
            return {
                "status": "success",
                "message": "数据清理任务已完成",
                "deleted_count": deleted_count
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据清理失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

