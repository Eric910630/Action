"""
商品数据模型
"""
from sqlalchemy import Column, String, Float, Date, JSON, Text, ForeignKey
from app.models.base import BaseModel


class Product(BaseModel):
    """商品表"""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    live_room_id = Column(String(64), ForeignKey("live_rooms.id"), nullable=True, index=True)
    product_link = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    selling_points = Column(JSON, nullable=True)
    price = Column(Float, nullable=True)
    hand_card = Column(Text, nullable=True)
    live_date = Column(Date, nullable=True, index=True)


class LiveRoom(BaseModel):
    """直播间表"""
    __tablename__ = "live_rooms"
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    keywords = Column(JSON, nullable=True)
    ip_character = Column(String(100), nullable=True)
    style = Column(String(100), nullable=True)

