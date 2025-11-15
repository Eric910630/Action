"""
拆解报告数据模型
"""
from sqlalchemy import Column, String, JSON, DateTime
from app.models.base import BaseModel


class AnalysisReport(BaseModel):
    """拆解报告表"""
    __tablename__ = "analysis_reports"
    
    video_url = Column(String(500), nullable=False, unique=True, index=True)
    video_info = Column(JSON, nullable=True)
    basic_info = Column(JSON, nullable=True)
    shot_table = Column(JSON, nullable=True)
    golden_3s = Column(JSON, nullable=True)
    highlights = Column(JSON, nullable=True)
    viral_formula = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    production_tips = Column(JSON, nullable=True)

