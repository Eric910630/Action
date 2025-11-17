"""
数据库工具
供Agents使用的数据库查询工具
"""
from typing import Dict, Any, Optional
from loguru import logger
from app.core.database import SessionLocal


def get_hotspot_info(hotspot_id: str) -> Dict[str, Any]:
    """
    获取热点信息
    
    Args:
        hotspot_id: 热点ID
    
    Returns:
        热点信息字典
    """
    from app.models.hotspot import Hotspot
    
    db = SessionLocal()
    try:
        hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
        if not hotspot:
            return {"error": "热点不存在"}
        
        return {
            "id": hotspot.id,
            "title": hotspot.title,
            "url": hotspot.url,
            "platform": hotspot.platform,
            "tags": hotspot.tags or [],
            "heat_score": hotspot.heat_score,
            "heat_growth_rate": hotspot.heat_growth_rate,
            "match_score": hotspot.match_score,
            # 关键：添加ContentAnalysisAgent和RelevanceAnalysisAgent的分析结果
            "content_analysis": hotspot.content_analysis,  # ContentAnalysisAgent的分析结果（包含电商适配性、适用类目等）
            "video_structure": hotspot.video_structure,  # 视频结构化信息（包含脚本结构、hook、body、cta等）
            "content_compact": hotspot.content_compact  # 内容摘要
        }
    except Exception as e:
        logger.error(f"获取热点信息失败: {e}")
        return {"error": str(e)}
    finally:
        db.close()


def get_product_info(product_id: str) -> Dict[str, Any]:
    """
    获取商品信息
    
    Args:
        product_id: 商品ID
    
    Returns:
        商品信息字典
    """
    from app.models.product import Product
    
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "商品不存在"}
        
        return {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "selling_points": product.selling_points or [],
            "price": product.price,
            "description": product.description,
            "hand_card": product.hand_card
        }
    except Exception as e:
        logger.error(f"获取商品信息失败: {e}")
        return {"error": str(e)}
    finally:
        db.close()


def get_analysis_report_info(report_id: str) -> Optional[Dict[str, Any]]:
    """
    获取拆解报告信息
    
    Args:
        report_id: 报告ID
    
    Returns:
        报告信息字典，如果不存在返回None
    """
    from app.models.analysis import AnalysisReport
    
    db = SessionLocal()
    try:
        report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
        if not report:
            return None
        
        return {
            "id": report.id,
            "video_url": report.video_url,
            "viral_formula": report.viral_formula or {},
            "production_tips": report.production_tips or {},
            "golden_3s": report.golden_3s or {},
            "shot_table": report.shot_table or []
        }
    except Exception as e:
        logger.error(f"获取拆解报告失败: {e}")
        return None
    finally:
        db.close()

