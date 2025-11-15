"""
视频拆解API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import AnalysisReport
from app.services.analysis.service import VideoAnalysisService
from app.services.analysis.tasks import analyze_video_async

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """拆解请求"""
    video_url: str
    options: Optional[dict] = None


@router.post("/analyze")
async def analyze_video(request: AnalyzeRequest):
    """分析视频"""
    # 异步触发Celery任务
    task = analyze_video_async.delay(request.video_url, request.options)
    return {
        "status": "success",
        "task_id": task.id,
        "video_url": request.video_url,
        "message": "视频分析任务已启动"
    }


@router.get("/reports")
async def get_reports(
    limit: int = 20,
    offset: int = 0,
    video_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取拆解报告列表"""
    query = db.query(AnalysisReport)
    
    if video_url:
        query = query.filter(AnalysisReport.video_url == video_url)
    
    total = query.count()
    reports = query.order_by(
        AnalysisReport.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": r.id,
                "video_url": r.video_url,
                "video_info": r.video_info,
                "basic_info": r.basic_info,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat()
            }
            for r in reports
        ],
        "limit": limit,
        "offset": offset
    }


@router.get("/reports/{report_id}")
async def get_report_detail(
    report_id: str,
    db: Session = Depends(get_db)
):
    """获取拆解报告详情"""
    report = db.query(AnalysisReport).filter(
        AnalysisReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="拆解报告不存在")
    
    # 提取爆款技巧
    service = VideoAnalysisService()
    techniques = service.extract_techniques({
        "shot_table": report.shot_table or [],
        "golden_3s": report.golden_3s or {},
        "viral_formula": report.viral_formula or {},
        "production_tips": report.production_tips or {},
        "highlights": report.highlights or []
    })
    
    return {
        "id": report.id,
        "video_url": report.video_url,
        "video_info": report.video_info,
        "basic_info": report.basic_info,
        "shot_table": report.shot_table,
        "golden_3s": report.golden_3s,
        "highlights": report.highlights,
        "viral_formula": report.viral_formula,
        "keywords": report.keywords,
        "production_tips": report.production_tips,
        "techniques": techniques,
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat()
    }


@router.post("/batch")
async def batch_analyze(video_urls: List[str]):
    """批量分析视频"""
    task_ids = []
    for video_url in video_urls[:10]:  # 最多10个
        task = analyze_video_async.delay(video_url)
        task_ids.append(task.id)
    
    return {
        "status": "success",
        "task_ids": task_ids,
        "total": len(video_urls),
        "message": f"批量分析任务已启动，共 {len(task_ids)} 个任务"
    }

