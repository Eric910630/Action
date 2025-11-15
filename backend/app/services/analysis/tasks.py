"""
视频拆解异步任务
"""
import asyncio
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.analysis.service import VideoAnalysisService
from loguru import logger


@celery_app.task(bind=True)
def analyze_video_async(self, video_url: str, options: dict = None):
    """异步拆解视频"""
    logger.info(f"开始分析视频: {video_url}")
    
    try:
        # 更新任务状态：开始
        self.update_state(
            state='PROGRESS',
            meta={'status': '开始拆解视频...', 'video_url': video_url}
        )
        
        service = VideoAnalysisService()
        db = SessionLocal()
        
        try:
            # 更新任务状态：正在分析
            self.update_state(
                state='PROGRESS',
                meta={'status': '正在分析视频内容...', 'video_url': video_url}
            )
            
            # 异步分析并保存
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            report = loop.run_until_complete(
                service.analyze_and_save(db, video_url, options)
            )
            loop.close()
            
            logger.info(f"视频分析完成: {video_url}, 报告ID: {report.id}")
            
            # 更新任务状态：完成
            return {
                "status": "success",
                "video_url": video_url,
                "report_id": report.id,
                "message": "视频拆解完成"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"视频分析失败: {e}")
        return {
            "status": "error",
            "video_url": video_url,
            "message": str(e)
        }

