"""
热点数据模型
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from app.models.base import BaseModel
from datetime import datetime


class Hotspot(BaseModel):
    """热点表"""
    __tablename__ = "hotspots"
    
    title = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True)
    platform = Column(String(50), nullable=False, index=True)
    tags = Column(JSON, nullable=True)
    heat_score = Column(Integer, nullable=True)
    heat_growth_rate = Column(Float, nullable=True)  # 热度增长速率
    publish_time = Column(DateTime, nullable=True)
    video_info = Column(JSON, nullable=True)
    match_score = Column(Float, nullable=True, index=True)  # 与主推商品的匹配度
    
    # 新增字段：内容Compact相关
    content_compact = Column(Text, nullable=True)  # 内容摘要
    video_structure = Column(JSON, nullable=True)  # 视频结构化信息
    content_analysis = Column(JSON, nullable=True)  # 内容分析结果（包括电商适配性）

