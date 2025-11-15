"""
脚本生成异步任务
"""
import asyncio
import os
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.script.service import ScriptGeneratorService
from app.models.hotspot import Hotspot
from app.models.product import Product
from app.models.analysis import AnalysisReport
from loguru import logger

# 在测试环境中，使用测试数据库
# 如果设置了USE_TEST_DB=true，确保使用相同的数据库连接
if os.getenv("USE_TEST_DB") == "true":
    # 在测试环境中，SessionLocal应该已经指向测试数据库
    # 这里不需要修改，因为SessionLocal使用的是settings.database_url
    # 而测试环境会设置正确的数据库URL
    pass


@celery_app.task
def generate_script_async(
    hotspot_id: str,
    product_id: str,
    analysis_report_id: str = None,
    duration: int = 10,
    adjustment_feedback: str = None,
    script_count: int = 5  # 新增：生成脚本数量，默认5个
):
    """异步生成脚本（默认生成5个不同的脚本）"""
    logger.info(f"开始生成脚本: hotspot_id={hotspot_id}, product_id={product_id}, script_count={script_count}, adjustment_feedback={'有' if adjustment_feedback else '无'}")
    
    try:
        service = ScriptGeneratorService()
        db = SessionLocal()
        
        try:
            # 获取相关数据
            hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
            if not hotspot:
                raise ValueError(f"热点不存在: {hotspot_id}")
            
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"商品不存在: {product_id}")
            
            analysis_report = None
            if analysis_report_id:
                analysis_report = db.query(AnalysisReport).filter(
                    AnalysisReport.id == analysis_report_id
                ).first()
            
            # 生成多个脚本
            script_ids = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for i in range(script_count):
                    logger.info(f"正在生成第 {i+1}/{script_count} 个脚本...")
                    
                    # 生成脚本（传入脚本序号，用于生成不同的脚本）
                    script_data = loop.run_until_complete(
                        service.generate_script(
                            hotspot, 
                            product, 
                            analysis_report, 
                            duration, 
                            adjustment_feedback,
                            script_index=i + 1,  # 传入脚本序号
                            total_scripts=script_count  # 传入总数量
                        )
                    )
                    
                    # 生成分镜列表
                    shot_list = service.generate_shot_list(script_data)
                    script_data["shot_list"] = shot_list
                    
                    # 保存脚本
                    script = service.save_script(
                        db,
                        hotspot_id,
                        product_id,
                        analysis_report_id,
                        script_data,
                        status="draft"
                    )
                    
                    script_ids.append(script.id)
                    logger.info(f"第 {i+1} 个脚本生成完成: {script.id}")
                    
            finally:
                loop.close()
            
            logger.info(f"所有脚本生成完成，共 {len(script_ids)} 个脚本")
            return {
                "status": "success",
                "script_ids": script_ids,
                "script_count": len(script_ids),
                "message": f"成功生成 {len(script_ids)} 个脚本"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"脚本生成失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

