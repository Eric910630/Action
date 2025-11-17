"""
用户反馈API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.feedback import Feedback
from loguru import logger

router = APIRouter()


class FeedbackCreate(BaseModel):
    """创建反馈请求"""
    user_name: Optional[str] = None
    content: str
    feedback_type: Optional[str] = "general"  # general, bug, suggestion, praise
    tags: Optional[List[str]] = None


class FeedbackUpdate(BaseModel):
    """更新反馈请求"""
    status: Optional[str] = None  # new, reviewed, resolved
    response: Optional[str] = None  # 管理员回复


@router.get("/")
async def get_feedbacks(
    status: Optional[str] = None,
    feedback_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取反馈列表"""
    query = db.query(Feedback)
    
    if status:
        query = query.filter(Feedback.status == status)
    
    if feedback_type:
        query = query.filter(Feedback.feedback_type == feedback_type)
    
    total = query.count()
    feedbacks = query.order_by(
        Feedback.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": f.id,
                "user_name": f.user_name,
                "content": f.content,
                "feedback_type": f.feedback_type,
                "tags": f.tags or [],
                "status": f.status,
                "response": f.response,
                "created_at": f.created_at.isoformat(),
                "updated_at": f.updated_at.isoformat()
            }
            for f in feedbacks
        ],
        "limit": limit,
        "offset": offset
    }


@router.post("/")
async def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """创建反馈"""
    import uuid
    
    new_feedback = Feedback(
        id=str(uuid.uuid4()),
        user_name=feedback.user_name,
        content=feedback.content,
        feedback_type=feedback.feedback_type or "general",
        tags=feedback.tags or [],
        status="new",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    logger.info(f"新反馈已创建: {new_feedback.id} (类型: {new_feedback.feedback_type})")
    
    return {
        "id": new_feedback.id,
        "message": "反馈已提交",
        "feedback": {
            "id": new_feedback.id,
            "user_name": new_feedback.user_name,
            "content": new_feedback.content,
            "feedback_type": new_feedback.feedback_type,
            "status": new_feedback.status,
            "created_at": new_feedback.created_at.isoformat()
        }
    }


@router.put("/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    feedback_update: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    """更新反馈（管理员操作）"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    if feedback_update.status:
        feedback.status = feedback_update.status
    
    if feedback_update.response:
        feedback.response = feedback_update.response
    
    feedback.updated_at = datetime.now()
    
    db.commit()
    db.refresh(feedback)
    
    logger.info(f"反馈已更新: {feedback_id} (状态: {feedback.status})")
    
    return {
        "id": feedback.id,
        "message": "反馈已更新",
        "feedback": {
            "id": feedback.id,
            "status": feedback.status,
            "response": feedback.response,
            "updated_at": feedback.updated_at.isoformat()
        }
    }


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """删除反馈"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    db.delete(feedback)
    db.commit()
    
    logger.info(f"反馈已删除: {feedback_id}")
    
    return {
        "id": feedback_id,
        "message": "反馈已删除"
    }

