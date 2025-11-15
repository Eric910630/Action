"""
脚本生成API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.script import Script
from app.services.script.service import ScriptGeneratorService
from app.services.script.tasks import generate_script_async

router = APIRouter()


class GenerateScriptRequest(BaseModel):
    """生成脚本请求"""
    hotspot_id: str
    product_id: str
    analysis_report_id: Optional[str] = None
    duration: int = 10  # 视频时长（秒）
    adjustment_feedback: Optional[str] = None  # 调整意见（用于重新生成）
    script_count: int = 5  # 生成脚本数量，默认5个


class ScriptUpdate(BaseModel):
    """更新脚本请求"""
    script_content: Optional[str] = None
    shot_list: Optional[list] = None
    production_notes: Optional[dict] = None
    tags: Optional[dict] = None
    status: Optional[str] = None


class ReviewRequest(BaseModel):
    """审核请求"""
    action: str  # approve/reject
    comment: Optional[str] = None


@router.post("/generate")
async def generate_script(request: GenerateScriptRequest):
    """生成脚本"""
    # 验证duration范围
    if request.duration < 5 or request.duration > 15:
        raise HTTPException(
            status_code=400,
            detail="视频时长必须在5-15秒之间"
        )
    
    # 验证script_count范围
    if request.script_count < 1 or request.script_count > 10:
        raise HTTPException(
            status_code=400,
            detail="脚本数量必须在1-10之间"
        )
    
    # 异步触发Celery任务
    task = generate_script_async.delay(
        request.hotspot_id,
        request.product_id,
        request.analysis_report_id,
        request.duration,
        request.adjustment_feedback,
        request.script_count  # 传入脚本数量
    )
    
    return {
        "status": "success",
        "task_id": task.id,
        "message": f"脚本生成任务已启动，将生成 {request.script_count} 个不同的脚本"
    }


@router.get("/")
async def get_scripts(
    product_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取脚本列表"""
    query = db.query(Script)
    
    if product_id:
        query = query.filter(Script.product_id == product_id)
    
    if status:
        query = query.filter(Script.status == status)
    
    total = query.count()
    scripts = query.order_by(
        Script.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": s.id,
                "hotspot_id": s.hotspot_id,
                "product_id": s.product_id,
                "analysis_report_id": s.analysis_report_id,
                "video_info": s.video_info,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat()
            }
            for s in scripts
        ],
        "limit": limit,
        "offset": offset
    }


@router.get("/{script_id}")
async def get_script_detail(
    script_id: str,
    db: Session = Depends(get_db)
):
    """获取脚本详情"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    return {
        "id": script.id,
        "hotspot_id": script.hotspot_id,
        "product_id": script.product_id,
        "analysis_report_id": script.analysis_report_id,
        "video_info": script.video_info,
        "script_content": script.script_content,
        "shot_list": script.shot_list,
        "production_notes": script.production_notes,
        "tags": script.tags,
        "status": script.status,
        "created_at": script.created_at.isoformat(),
        "updated_at": script.updated_at.isoformat()
    }


@router.put("/{script_id}")
async def update_script(
    script_id: str,
    script_update: ScriptUpdate,
    db: Session = Depends(get_db)
):
    """更新脚本"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    update_data = script_update.dict(exclude_unset=True)
    
    if "script_content" in update_data:
        script.script_content = update_data["script_content"]
    if "shot_list" in update_data:
        script.shot_list = update_data["shot_list"]
    if "production_notes" in update_data:
        script.production_notes = update_data["production_notes"]
    if "tags" in update_data:
        script.tags = update_data["tags"]
    if "status" in update_data:
        script.status = update_data["status"]
    
    from datetime import datetime
    script.updated_at = datetime.now()
    
    db.commit()
    db.refresh(script)
    
    return {
        "id": script.id,
        "message": "脚本已更新",
        "script": {
            "id": script.id,
            "status": script.status
        }
    }


@router.post("/{script_id}/review")
async def review_script(
    script_id: str,
    review: ReviewRequest,
    db: Session = Depends(get_db)
):
    """审核脚本"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    if review.action == "approve":
        script.status = "approved"
    elif review.action == "reject":
        script.status = "rejected"
    else:
        raise HTTPException(
            status_code=400,
            detail="action必须是approve或reject"
        )
    
    from datetime import datetime
    script.updated_at = datetime.now()
    
    # 这里可以保存审核意见到数据库（需要扩展模型）
    # 暂时只更新状态
    
    db.commit()
    db.refresh(script)
    
    return {
        "id": script.id,
        "action": review.action,
        "status": script.status,
        "message": "审核完成"
    }


@router.post("/{script_id}/optimize")
async def optimize_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """获取脚本优化建议"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    service = ScriptGeneratorService()
    suggestions = await service.get_optimization_suggestions(script)
    
    return {
        "id": script_id,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


class RegenerateScriptRequest(BaseModel):
    """重新生成脚本请求"""
    adjustment_feedback: str  # 调整意见（必填）


@router.post("/{script_id}/regenerate")
async def regenerate_script(
    script_id: str,
    request: RegenerateScriptRequest,
    db: Session = Depends(get_db)
):
    """重新生成脚本（基于现有脚本，根据调整意见生成新脚本）"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 验证调整意见不为空
    if not request.adjustment_feedback or not request.adjustment_feedback.strip():
        raise HTTPException(
            status_code=400,
            detail="调整意见不能为空"
        )
    
    # 获取原脚本的相关信息
    hotspot_id = script.hotspot_id
    product_id = script.product_id
    analysis_report_id = script.analysis_report_id
    duration = script.video_info.get("duration", 10) if script.video_info else 10
    
    # 验证duration范围
    if duration < 5 or duration > 15:
        duration = 10  # 默认值
    
    # 异步触发Celery任务（重新生成时只生成1个脚本）
    task = generate_script_async.delay(
        hotspot_id,
        product_id,
        analysis_report_id,
        duration,
        request.adjustment_feedback.strip(),
        1  # 重新生成时只生成1个脚本
    )
    
    return {
        "status": "success",
        "task_id": task.id,
        "message": "脚本重新生成任务已启动"
    }

