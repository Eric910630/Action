"""
用户反馈数据模型
"""
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.models.base import BaseModel


class Feedback(BaseModel):
    """用户反馈表"""
    __tablename__ = "feedbacks"
    
    user_name = Column(String(100), nullable=True)  # 用户名（可选）
    content = Column(Text, nullable=False)  # 反馈内容
    feedback_type = Column(String(20), nullable=True, default="general")  # 反馈类型：general(一般), bug(问题), suggestion(建议), praise(表扬)
    tags = Column(JSON, nullable=True)  # 标签（如：["UI", "匹配算法", "脚本质量"]）
    status = Column(String(20), nullable=True, default="new")  # 状态：new(新), reviewed(已查看), resolved(已解决)
    response = Column(Text, nullable=True)  # 回复内容（管理员回复）

