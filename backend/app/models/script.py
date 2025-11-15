"""
脚本数据模型
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from app.models.base import BaseModel


class Script(BaseModel):
    """脚本表"""
    __tablename__ = "scripts"
    
    hotspot_id = Column(String(64), ForeignKey("hotspots.id"), nullable=True)
    product_id = Column(String(64), ForeignKey("products.id"), nullable=False, index=True)
    analysis_report_id = Column(String(64), ForeignKey("analysis_reports.id"), nullable=True)
    video_info = Column(JSON, nullable=True)
    script_content = Column(Text, nullable=True)
    shot_list = Column(JSON, nullable=True)
    production_notes = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    status = Column(String(20), nullable=True, index=True)  # draft/reviewed/approved

