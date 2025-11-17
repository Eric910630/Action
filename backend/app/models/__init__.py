"""
数据模型
"""
from app.models.base import Base, BaseModel
from app.models.hotspot import Hotspot
from app.models.product import Product, LiveRoom
from app.models.analysis import AnalysisReport
from app.models.script import Script
from app.models.feedback import Feedback

__all__ = [
    "Base",
    "BaseModel",
    "Hotspot",
    "Product",
    "LiveRoom",
    "AnalysisReport",
    "Script",
    "Feedback",
]
