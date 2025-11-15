"""
商品管理API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from datetime import date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.data.service import DataService

router = APIRouter()
service = DataService()


class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str
    brand: Optional[str] = None
    category: str
    live_room_id: str
    product_link: Optional[str] = None
    description: Optional[str] = None
    selling_points: list = []
    price: float
    hand_card: Optional[str] = None
    live_date: str


class ProductUpdate(BaseModel):
    """更新商品请求"""
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    live_room_id: Optional[str] = None
    product_link: Optional[str] = None
    description: Optional[str] = None
    selling_points: Optional[list] = None
    price: Optional[float] = None
    hand_card: Optional[str] = None
    live_date: Optional[str] = None


@router.get("/")
async def get_products(
    live_room_id: Optional[str] = None,
    live_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    live_date_obj = None
    if live_date:
        try:
            live_date_obj = date.fromisoformat(live_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    products, total = service.get_products(
        db, live_room_id, live_date_obj, limit, offset
    )
    
    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "live_room_id": p.live_room_id,
                "product_link": p.product_link,
                "description": p.description,
                "selling_points": p.selling_points,
                "price": p.price,
                "hand_card": p.hand_card,
                "live_date": p.live_date.isoformat() if p.live_date else None,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in products
        ],
        "limit": limit,
        "offset": offset
    }


@router.post("/")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """创建商品"""
    try:
        live_date_obj = date.fromisoformat(product.live_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    product_data = product.dict()
    product_data["live_date"] = live_date_obj
    
    new_product = service.create_product(db, product_data)
    
    return {
        "id": new_product.id,
        "message": "商品已创建",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "category": new_product.category
        }
    }


@router.get("/{product_id}")
async def get_product_detail(
    product_id: str,
    db: Session = Depends(get_db)
):
    """获取商品详情"""
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "live_room_id": product.live_room_id,
        "product_link": product.product_link,
        "description": product.description,
        "selling_points": product.selling_points,
        "price": product.price,
        "hand_card": product.hand_card,
        "live_date": product.live_date.isoformat() if product.live_date else None,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat()
    }


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """更新商品"""
    product_data = product.dict(exclude_unset=True)
    
    if "live_date" in product_data and product_data["live_date"]:
        try:
            product_data["live_date"] = date.fromisoformat(product_data["live_date"])
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    updated_product = service.update_product(db, product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return {
        "id": updated_product.id,
        "message": "商品已更新",
        "product": {
            "id": updated_product.id,
            "name": updated_product.name
        }
    }

