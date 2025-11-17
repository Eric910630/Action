"""
直播间管理API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.data.service import DataService

router = APIRouter()
service = DataService()


class LiveRoomCreate(BaseModel):
    """创建直播间请求"""
    name: str
    category: str
    keywords: List[str] = []
    ip_character: Optional[str] = None
    style: Optional[str] = None


class LiveRoomUpdate(BaseModel):
    """更新直播间请求"""
    name: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None
    ip_character: Optional[str] = None
    style: Optional[str] = None


@router.get("/")
async def get_live_rooms(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取直播间列表"""
    try:
        rooms = service.get_live_rooms(db, category)
        
        return {
            "items": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "keywords": r.keywords,
                    "ip_character": r.ip_character,
                    "style": r.style,
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat()
                }
                for r in rooms
            ]
        }
    except Exception as e:
        # 数据库连接失败时返回空列表，避免前端报错
        # 这在本地开发时很有用，当无法连接到生产数据库时
        from loguru import logger
        logger.warning(f"数据库连接失败，返回空列表: {e}")
        return {
            "items": []
        }


@router.post("/")
async def create_live_room(
    room: LiveRoomCreate,
    db: Session = Depends(get_db)
):
    """创建直播间"""
    room_data = room.dict()
    new_room = service.create_live_room(db, room_data)
    
    return {
        "id": new_room.id,
        "message": "直播间已创建",
        "room": {
            "id": new_room.id,
            "name": new_room.name,
            "category": new_room.category
        }
    }


@router.get("/{room_id}")
async def get_live_room_detail(
    room_id: str,
    db: Session = Depends(get_db)
):
    """获取直播间详情"""
    room = service.get_live_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="直播间不存在")
    
    return {
        "id": room.id,
        "name": room.name,
        "category": room.category,
        "keywords": room.keywords,
        "ip_character": room.ip_character,
        "style": room.style,
        "created_at": room.created_at.isoformat(),
        "updated_at": room.updated_at.isoformat()
    }


@router.put("/{room_id}")
async def update_live_room(
    room_id: str,
    room: LiveRoomUpdate,
    db: Session = Depends(get_db)
):
    """更新直播间"""
    room_data = room.dict(exclude_unset=True)
    updated_room = service.update_live_room(db, room_id, room_data)
    
    if not updated_room:
        raise HTTPException(status_code=404, detail="直播间不存在")
    
    return {
        "id": updated_room.id,
        "message": "直播间已更新",
        "room": {
            "id": updated_room.id,
            "name": updated_room.name
        }
    }


@router.delete("/{room_id}")
async def delete_live_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """删除直播间"""
    result = service.delete_live_room(db, room_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="直播间不存在")
    
    return {
        "id": room_id,
        "message": "直播间已删除"
    }

