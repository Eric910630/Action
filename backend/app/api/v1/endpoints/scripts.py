"""
脚本生成API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import json

from app.core.database import get_db
from app.models.script import Script
from app.models.hotspot import Hotspot
from app.models.product import Product
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
    script_count: int = 5  # 生成脚本数量，默认5个（至少5个）


class ScriptUpdate(BaseModel):
    """更新脚本请求"""
    script_content: Optional[str] = None
    shot_list: Optional[list] = None
    production_notes: Optional[dict] = None
    tags: Optional[dict] = None
    status: Optional[str] = None




@router.post("/generate")
async def generate_script(request: GenerateScriptRequest):
    """生成脚本"""
    # 验证duration范围
    if request.duration < 5 or request.duration > 15:
        raise HTTPException(
            status_code=400,
            detail="视频时长必须在5-15秒之间"
        )
    
    # 验证script_count范围（至少5个）
    if request.script_count < 5:
        raise HTTPException(
            status_code=400,
            detail="脚本数量至少为5个"
        )
    if request.script_count > 10:
        raise HTTPException(
            status_code=400,
            detail="脚本数量最多为10个"
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
    group_by_product: bool = True,  # 新增：是否按商品-热点分组
    db: Session = Depends(get_db)
):
    """获取脚本列表（支持按商品-热点分组）"""
    query = db.query(Script)
    
    if product_id:
        query = query.filter(Script.product_id == product_id)
    
    if status:
        query = query.filter(Script.status == status)
    
    total = query.count()
    scripts = query.order_by(
        Script.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # 如果不需要分组，返回平铺列表（兼容旧版本）
    if not group_by_product:
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
    
    # 按商品-热点分组
    from app.models.product import Product
    from app.models.hotspot import Hotspot
    from collections import defaultdict
    
    # 构建分组结构：商品 -> 热点 -> 脚本列表
    grouped = defaultdict(lambda: defaultdict(list))
    
    for s in scripts:
        # 获取商品信息
        product = db.query(Product).filter(Product.id == s.product_id).first()
        product_name = product.name if product else f"商品({s.product_id[:8]}...)"
        
        # 获取热点信息
        hotspot = db.query(Hotspot).filter(Hotspot.id == s.hotspot_id).first() if s.hotspot_id else None
        hotspot_title = hotspot.title if hotspot else f"热点({s.hotspot_id[:8]}...)" if s.hotspot_id else "无热点"
        
        # 构建脚本信息
        script_info = {
            "id": s.id,
            "hotspot_id": s.hotspot_id,
            "product_id": s.product_id,
            "analysis_report_id": s.analysis_report_id,
            "video_info": s.video_info,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        
        # 分组：商品 -> 热点 -> 脚本
        grouped[s.product_id][s.hotspot_id].append(script_info)
    
    # 转换为前端需要的格式
    result_items = []
    for prod_id, hotspots in grouped.items():
        product = db.query(Product).filter(Product.id == prod_id).first()
        product_info = {
            "product_id": prod_id,
            "product_name": product.name if product else f"商品({prod_id[:8]}...)",
            "product_category": product.category if product else "",
            "hotspots": []
        }
        
        for hotspot_id, scripts_list in hotspots.items():
            hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first() if hotspot_id else None
            hotspot_info = {
                "hotspot_id": hotspot_id,
                "hotspot_title": hotspot.title if hotspot else f"热点({hotspot_id[:8]}...)" if hotspot_id else "无热点",
                "hotspot_platform": hotspot.platform if hotspot else "",
                "scripts": scripts_list
            }
            product_info["hotspots"].append(hotspot_info)
        
        result_items.append(product_info)
    
    return {
        "total": total,
        "items": result_items,  # 分组后的结构
        "limit": limit,
        "offset": offset,
        "grouped": True  # 标识这是分组结构
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


@router.get("/{script_id}/export-pdf")
async def export_script_pdf(
    script_id: str,
    db: Session = Depends(get_db)
):
    """导出脚本为PDF"""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 获取关联的商品和热点信息
    product = db.query(Product).filter(Product.id == script.product_id).first()
    hotspot = db.query(Hotspot).filter(Hotspot.id == script.hotspot_id).first() if script.hotspot_id else None
    
    # 生成PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 定义样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=20
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4b5563'),
        leading=16,
        alignment=TA_JUSTIFY
    )
    
    # 标题
    video_info = script.video_info or {}
    title = video_info.get('title', '未命名脚本')
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 基本信息
    story.append(Paragraph("基本信息", heading_style))
    
    meta_data = [
        ["商品名称", product.name if product else "未知"],
        ["商品品类", product.category if product else "未知"],
        ["视频时长", f"{video_info.get('duration', 10)}秒"],
        ["视频主题", video_info.get('theme', '无')],
        ["核心卖点", video_info.get('core_selling_point', '无')],
    ]
    
    if hotspot:
        meta_data.append(["关联热点", hotspot.title])
        meta_data.append(["热点平台", hotspot.platform])
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 脚本内容
    if script.script_content:
        story.append(Paragraph("脚本内容", heading_style))
        story.append(Paragraph(script.script_content.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 0.3*inch))
    
    # 分镜列表
    shot_list = script.shot_list or []
    if shot_list:
        story.append(Paragraph("分镜列表", heading_style))
        
        # 分镜表格表头
        shot_table_data = [["镜头", "时间", "景别", "画面内容", "台词", "动作", "音乐", "作用", "塑造点"]]
        
        for i, shot in enumerate(shot_list, 1):
            shot_table_data.append([
                str(i),
                shot.get('time_range', ''),
                shot.get('shot_type', ''),
                shot.get('content', '')[:50] + ('...' if len(shot.get('content', '')) > 50 else ''),
                shot.get('dialogue', '')[:50] + ('...' if len(shot.get('dialogue', '')) > 50 else ''),
                shot.get('action', '')[:30] + ('...' if len(shot.get('action', '')) > 30 else ''),
                shot.get('music', '')[:30] + ('...' if len(shot.get('music', '')) > 30 else ''),
                shot.get('purpose', '')[:30] + ('...' if len(shot.get('purpose', '')) > 30 else ''),
                shot.get('shaping_point', '')[:30] + ('...' if len(shot.get('shaping_point', '')) > 30 else ''),
            ])
        
        # 创建分镜表格（由于列太多，需要调整列宽）
        shot_table = Table(shot_table_data, colWidths=[
            0.3*inch, 0.6*inch, 0.5*inch, 1.2*inch, 1.2*inch, 
            0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch
        ])
        shot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        story.append(shot_table)
        story.append(Spacer(1, 0.3*inch))
    
    # 制作要点
    production_notes = script.production_notes or {}
    if production_notes:
        story.append(Paragraph("制作要点", heading_style))
        
        if production_notes.get('shooting_tips'):
            story.append(Paragraph("<b>拍摄要点：</b>", normal_style))
            for tip in production_notes.get('shooting_tips', []):
                story.append(Paragraph(f"• {tip}", normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        if production_notes.get('editing_tips'):
            story.append(Paragraph("<b>剪辑要点：</b>", normal_style))
            for tip in production_notes.get('editing_tips', []):
                story.append(Paragraph(f"• {tip}", normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        if production_notes.get('key_points'):
            story.append(Paragraph("<b>关键要点：</b>", normal_style))
            for point in production_notes.get('key_points', []):
                story.append(Paragraph(f"• {point}", normal_style))
    
    # 生成PDF
    doc.build(story)
    buffer.seek(0)
    
    # 返回PDF文件
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=脚本_{title}.pdf"
        }
    )


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

