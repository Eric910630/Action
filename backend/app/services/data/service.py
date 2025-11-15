"""
数据管理服务
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger

from app.models.product import Product, LiveRoom


class DataService:
    """数据管理服务"""
    
    # ========== 商品管理 ==========
    
    def create_product(
        self,
        db: Session,
        product_data: Dict[str, Any]
    ) -> Product:
        """创建商品"""
        product = Product(
            id=str(uuid.uuid4()),
            name=product_data["name"],
            brand=product_data.get("brand"),
            category=product_data.get("category"),
            live_room_id=product_data.get("live_room_id"),
            product_link=product_data.get("product_link"),
            description=product_data.get("description"),
            selling_points=product_data.get("selling_points", []),
            price=product_data.get("price"),
            hand_card=product_data.get("hand_card"),
            live_date=product_data.get("live_date"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"创建商品: {product.name}")
        return product
    
    def get_product(self, db: Session, product_id: str) -> Optional[Product]:
        """获取商品"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    def get_products(
        self,
        db: Session,
        live_room_id: Optional[str] = None,
        live_date: Optional[date] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Product], int]:
        """获取商品列表"""
        query = db.query(Product)
        
        if live_room_id:
            query = query.filter(Product.live_room_id == live_room_id)
        
        if live_date:
            query = query.filter(Product.live_date == live_date)
        
        total = query.count()
        products = query.order_by(
            Product.live_date.desc(),
            Product.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return products, total
    
    def update_product(
        self,
        db: Session,
        product_id: str,
        product_data: Dict[str, Any]
    ) -> Optional[Product]:
        """更新商品"""
        product = self.get_product(db, product_id)
        if not product:
            return None
        
        # 更新字段
        if "name" in product_data:
            product.name = product_data["name"]
        if "brand" in product_data:
            product.brand = product_data["brand"]
        if "category" in product_data:
            product.category = product_data["category"]
        if "live_room_id" in product_data:
            product.live_room_id = product_data["live_room_id"]
        if "product_link" in product_data:
            product.product_link = product_data["product_link"]
        if "description" in product_data:
            product.description = product_data["description"]
        if "selling_points" in product_data:
            product.selling_points = product_data["selling_points"]
        if "price" in product_data:
            product.price = product_data["price"]
        if "hand_card" in product_data:
            product.hand_card = product_data["hand_card"]
        if "live_date" in product_data:
            product.live_date = product_data["live_date"]
        
        product.updated_at = datetime.now()
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"更新商品: {product.name}")
        return product
    
    def delete_product(self, db: Session, product_id: str) -> bool:
        """删除商品"""
        product = self.get_product(db, product_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        
        logger.info(f"删除商品: {product.name}")
        return True
    
    # ========== 直播间管理 ==========
    
    def create_live_room(
        self,
        db: Session,
        room_data: Dict[str, Any]
    ) -> LiveRoom:
        """创建直播间"""
        room = LiveRoom(
            id=str(uuid.uuid4()),
            name=room_data["name"],
            category=room_data["category"],
            keywords=room_data.get("keywords", []),
            ip_character=room_data.get("ip_character"),
            style=room_data.get("style"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        logger.info(f"创建直播间: {room.name}")
        return room
    
    def get_live_room(self, db: Session, room_id: str) -> Optional[LiveRoom]:
        """获取直播间"""
        return db.query(LiveRoom).filter(LiveRoom.id == room_id).first()
    
    def get_live_rooms(
        self,
        db: Session,
        category: Optional[str] = None
    ) -> List[LiveRoom]:
        """获取直播间列表"""
        query = db.query(LiveRoom)
        
        if category:
            query = query.filter(LiveRoom.category == category)
        
        return query.order_by(LiveRoom.created_at).all()
    
    def update_live_room(
        self,
        db: Session,
        room_id: str,
        room_data: Dict[str, Any]
    ) -> Optional[LiveRoom]:
        """更新直播间"""
        room = self.get_live_room(db, room_id)
        if not room:
            return None
        
        if "name" in room_data:
            room.name = room_data["name"]
        if "category" in room_data:
            room.category = room_data["category"]
        if "keywords" in room_data:
            room.keywords = room_data["keywords"]
        if "ip_character" in room_data:
            room.ip_character = room_data["ip_character"]
        if "style" in room_data:
            room.style = room_data["style"]
        
        room.updated_at = datetime.now()
        
        db.commit()
        db.refresh(room)
        
        logger.info(f"更新直播间: {room.name}")
        return room
    
    def delete_live_room(self, db: Session, room_id: str) -> bool:
        """删除直播间"""
        room = self.get_live_room(db, room_id)
        if not room:
            return False
        
        db.delete(room)
        db.commit()
        
        logger.info(f"删除直播间: {room.name}")
        return True

