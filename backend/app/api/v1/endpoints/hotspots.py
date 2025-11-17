"""
热点监控API端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.models.hotspot import Hotspot
from app.models.product import LiveRoom
from app.services.hotspot.service import HotspotMonitorService
from app.services.hotspot.tasks import fetch_daily_hotspots

router = APIRouter()


@router.get("/")
async def get_hotspots(
    platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    live_room_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取热点列表"""
    query = db.query(Hotspot)
    
    # 平台筛选
    if platform:
        query = query.filter(Hotspot.platform == platform)
    
    # 日期筛选
    if start_date:
        query = query.filter(Hotspot.created_at >= start_date)
    if end_date:
        query = query.filter(Hotspot.created_at <= end_date)
    
    # 直播间筛选
    if live_room_id:
        live_room = db.query(LiveRoom).filter(LiveRoom.id == live_room_id).first()
        if not live_room:
            raise HTTPException(status_code=404, detail="直播间不存在")
        
        # 根据直播间关键词筛选（简化版）
        keywords = live_room.keywords or []
        if keywords:
            from sqlalchemy import or_
            conditions = [Hotspot.title.ilike(f"%{kw}%") for kw in keywords]
            query = query.filter(or_(*conditions))
    
    # 获取总数
    total = query.count()
    
    # 获取列表（按时间倒序）
    hotspots = query.order_by(
        Hotspot.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # 解析JSON字段
    import json
    items = []
    for h in hotspots:
        video_structure = None
        content_analysis = None
        if h.video_structure:
            if isinstance(h.video_structure, str):
                try:
                    video_structure = json.loads(h.video_structure)
                except:
                    video_structure = None
            else:
                video_structure = h.video_structure
        
        if h.content_analysis:
            if isinstance(h.content_analysis, str):
                try:
                    content_analysis = json.loads(h.content_analysis)
                except:
                    content_analysis = None
            else:
                content_analysis = h.content_analysis
        
        items.append({
            "id": h.id,
            "title": h.title,
            "url": h.url,
            "platform": h.platform,
            "tags": h.tags,
            "heat_score": h.heat_score,
            "match_score": h.match_score,
            "publish_time": h.publish_time.isoformat() if h.publish_time else None,
            "video_info": h.video_info,
            "video_structure": video_structure,
            "content_analysis": content_analysis,
            "content_compact": h.content_compact,
            "created_at": h.created_at.isoformat(),
            "updated_at": h.updated_at.isoformat()
        })
    
    return {
        "total": total,
        "items": items,
        "limit": limit,
        "offset": offset
    }


@router.post("/fetch")
async def fetch_hotspots(
    platform: Optional[str] = None,
    live_room_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    手动触发热点抓取（使用语义筛选）
    
    Args:
        platform: 平台标识，如果为None则抓取多个平台（douyin, zhihu, weibo, bilibili, xiaohongshu）
        live_room_id: 直播间ID
    """
    # 异步触发Celery任务
    task = fetch_daily_hotspots.delay(platform=platform, live_room_id=live_room_id)
    platforms_info = "多个平台（douyin, zhihu, weibo, bilibili, xiaohongshu）" if platform is None else platform
    return {
        "message": f"热点抓取任务已启动（{platforms_info}，使用语义关联度筛选）",
        "platform": platform,
        "live_room_id": live_room_id,
        "task_id": task.id
    }


@router.get("/visualization")
async def get_hotspots_visualization(
    live_room_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取热点可视化数据（气泡图）
    
    返回格式：
    {
        "categories": [
            {
                "category": "女装",
                "hotspots": [
                    {
                        "id": "...",
                        "title": "...",
                        "heat_score": 95,
                        "match_score": 0.85
                    }
                ]
            }
        ]
    }
    """
    service = HotspotMonitorService()
    
    # 获取所有直播间
    live_rooms = db.query(LiveRoom).all()
    
    result = {"categories": []}
    
    # 优化：只获取最近的热点（限制数量，避免性能问题）
    # 先获取最近500个热点，然后快速筛选（增加数量，确保新抓取的热点能被包含）
    # 排除测试数据（只排除URL中的测试标识，不排除标题中的"测试"，因为真实新闻可能包含这个词）
    from sqlalchemy import not_, or_
    exclude_conditions = [
        Hotspot.url.ilike('%test.com%'),
        Hotspot.url.ilike('%workflow-real-llm%'),
        Hotspot.url.ilike('%/video/test%'),
        # 不排除标题中的"测试"，因为真实新闻可能包含这个词（如"奇瑞就天门山测试意外致歉"）
    ]
    recent_hotspots = db.query(Hotspot).filter(
        not_(or_(*exclude_conditions))
    ).order_by(Hotspot.created_at.desc()).limit(500).all()
    
    for live_room in live_rooms:
        if live_room_id and live_room.id != live_room_id:
            continue
        
        # 快速预筛选：先用关键词快速过滤
        keywords = live_room.keywords or []
        category = live_room.category or ""
        live_room_name = live_room.name or ""
        
        # 预筛选热点（快速匹配）
        prefiltered_hotspots = []
        
        # 定义不相关关键词（用于排除）- 根据直播间名称匹配
        # 注意：使用完整词组匹配，避免误排除（如"生活"不应该排除"生活家居"中的"生活"）
        exclude_keywords_map = {
            "时尚真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "桌子", "椅子", "柜子", "生活家居", "家居用品", "家居设计"],
            "美妆真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "生活家居", "家居用品"],
            "童装真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "美妆", "化妆品", "生活家居", "家居用品", "家居设计", "家居装修", "家居装饰"],
            "轻奢真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "童装", "儿童", "生活家居", "家居用品"],
        }
        
        for hotspot in recent_hotspots:
            hotspot_text = f"{hotspot.title} {' '.join(hotspot.tags or [])}".lower()
            
            # 首先检查是否包含不相关关键词（排除）- 根据直播间名称匹配
            should_exclude = False
            if live_room_name in exclude_keywords_map:
                exclude_keywords = exclude_keywords_map[live_room_name]
                if any(exclude_kw in hotspot_text for exclude_kw in exclude_keywords):
                    should_exclude = True
                    continue  # 直接跳过，不进入预筛选
            
            # 信任LLM的判断：如果热点有content_analysis且电商适配性>=0.3，就进入匹配计算
            # 不再要求标题中必须包含关键词或类目词，因为LLM已经通过语义分析识别出了适用类目
            has_ecommerce_potential = False
            if hotspot.content_analysis:
                try:
                    content_analysis = hotspot.content_analysis
                    if isinstance(content_analysis, str):
                        import json
                        content_analysis = json.loads(content_analysis)
                    
                    ecommerce_fit = content_analysis.get("ecommerce_fit", {})
                    if isinstance(ecommerce_fit, dict):
                        ecommerce_score = float(ecommerce_fit.get("score", 0.0))
                        # 如果电商适配性>=0.3，认为有潜在价值，进入匹配计算
                        if ecommerce_score >= 0.3:
                            has_ecommerce_potential = True
                except Exception:
                    pass
            
            # 预筛选条件：
            # 1. 有电商适配性潜力（>=0.3）- 信任LLM的判断
            # 2. 或者有match_score（已通过语义筛选）
            # 3. 或者有关键词/类目匹配（保留作为补充，但不作为必要条件）
            keyword_match = any(kw.lower() in hotspot_text for kw in keywords) if keywords else False
            category_match = any(cat.strip().lower() in hotspot_text for cat in category.split('、')) if category else False
            has_match_score = hotspot.match_score is not None and hotspot.match_score > 0
            
            # 信任LLM的判断：有电商适配性潜力就进入匹配计算
            if has_ecommerce_potential or has_match_score or keyword_match or category_match:
                prefiltered_hotspots.append(hotspot)
        
        # 如果预筛选后还是太多，限制数量（减少预筛选数量，提高筛选质量）
        if len(prefiltered_hotspots) > 100:
            prefiltered_hotspots = prefiltered_hotspots[:100]
        
        # 快速计算匹配度（不使用Agent，避免阻塞）
        hotspot_scores = []
        for hotspot in prefiltered_hotspots:
            hotspot_text = f"{hotspot.title} {' '.join(hotspot.tags or [])}".lower()
            
            # 1. 关键词匹配（40%权重）
            keyword_score = 0.0
            matched_keywords = []
            if keywords:
                for kw in keywords:
                    if kw.lower() in hotspot_text:
                        matched_keywords.append(kw)
                keyword_score = min(1.0, len(matched_keywords) / len(keywords))
            
            # 2. 类目匹配（20%权重）- 严格匹配
            category_score = 0.0
            if category:
                # 再次检查不相关关键词（双重保险）- 根据直播间名称匹配
                exclude_keywords_map = {
                    "时尚真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "桌子", "椅子", "柜子", "生活家居", "家居用品", "家居设计"],
                    "美妆真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "生活家居", "家居用品"],
                    "童装真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "美妆", "化妆品", "生活家居", "家居用品", "家居设计", "家居装修", "家居装饰"],
                    "轻奢真惠选": ["家具", "家居", "家电", "智能家居", "3c", "数码", "电器", "装修", "北欧", "沙发", "床", "童装", "儿童", "生活家居", "家居用品"],
                }
                
                if live_room_name in exclude_keywords_map:
                    exclude_keywords = exclude_keywords_map[live_room_name]
                    if any(exclude_kw in hotspot_text for exclude_kw in exclude_keywords):
                        # 如果包含不相关关键词，直接返回0匹配度，不继续计算
                        match_score = 0.0
                        hotspot_scores.append({
                            "hotspot": hotspot,
                            "match_score": match_score
                        })
                        continue
                
                category_keywords = category.split('、')
                # 检查是否有类目关键词匹配
                for cat_kw in category_keywords:
                    cat_kw_clean = cat_kw.strip().lower()
                    # 严格匹配：类目关键词必须在热点文本中
                    if cat_kw_clean in hotspot_text:
                        category_score = 1.0
                        break
            
            # 3. 电商适配性匹配（新增）- 基于ContentAnalysisAgent的分析结果
            ecommerce_score = 0.0
            applicable_categories_match = 0.0
            
            # 检查热点是否有ContentAnalysisAgent的分析结果
            if hotspot.content_analysis:
                try:
                    content_analysis = hotspot.content_analysis
                    if isinstance(content_analysis, str):
                        import json
                        content_analysis = json.loads(content_analysis)
                    
                    # 获取电商适配性评分
                    ecommerce_fit = content_analysis.get("ecommerce_fit", {})
                    if isinstance(ecommerce_fit, dict):
                        ecommerce_score = float(ecommerce_fit.get("score", 0.0))
                        
                        # 检查适用类目是否与直播间类目匹配
                        # **重要：不再使用硬编码的同义词映射，而是依赖RelevanceAnalysisAgent的最终判断**
                        # 如果Agent判断不相关，即使适用类目有匹配，也不应该匹配
                        applicable_categories = ecommerce_fit.get("applicable_categories", [])
                        if applicable_categories and category:
                            category_keywords = [cat.strip().lower() for cat in category.split('、')]
                            
                            # 只进行直接文本匹配（精确匹配，避免误匹配）
                            # **不再使用同义词映射，避免"运动鞋服"通过"服饰"匹配到"女装"**
                            matched_categories = [
                                app_cat for app_cat in applicable_categories
                                if any(cat_kw in app_cat.lower() or app_cat.lower() in cat_kw 
                                       for cat_kw in category_keywords)
                            ]
                            
                            if matched_categories:
                                # 直接匹配成功，给满分
                                applicable_categories_match = 1.0
                            else:
                                # 直接匹配失败，不给分数
                                # **不再使用同义词映射或embedding，避免误匹配**
                                # **依赖RelevanceAnalysisAgent的最终判断**
                                applicable_categories_match = 0.0
                except Exception as e:
                    print(f"[匹配度计算] 解析content_analysis失败: {e}")
            
            # 4. 简单语义匹配（40%权重）- 基于关键词重叠
            semantic_score = keyword_score  # 简化：使用关键词匹配作为语义匹配
            
            # 5. 如果热点已经有match_score（从语义筛选中获得），使用它作为基础
            base_match_score = hotspot.match_score if hotspot.match_score and hotspot.match_score > 0 else 0.0
            
            # 综合计算匹配度（优化版：信任LLM的判断）
            # 新权重分配：
            # 1. 内容迁移潜力（60%）- LLM的电商适配性判断，这是最智能的部分
            # 2. 语义关联（25%）- 使用embedding或Agent计算的语义相似度
            # 3. 直接关联（10%）- 关键词+类目匹配（硬编码，权重降低）
            # 4. 适用类目匹配（5%）- LLM识别的适用类目与直播间类目的匹配度
            
            # 计算内容迁移潜力（基于电商适配性，如果有适用类目匹配则加权）
            content_migration_potential = ecommerce_score
            if applicable_categories_match > 0:
                # 如果适用类目有匹配，说明LLM认为这个热点确实适合这个直播间，加权
                content_migration_potential = min(1.0, ecommerce_score * 1.1)
            
            # 计算语义关联（如果有base_match_score，使用它；否则使用关键词匹配作为简单代理）
            semantic_relevance = base_match_score if base_match_score > 0 else (keyword_score * 0.5 + category_score * 0.5)
            
            # 计算直接关联（关键词+类目匹配）
            direct_relevance = (keyword_score * 0.6 + category_score * 0.4)
            
            # 重要：当没有直接关联时（关键词和类目匹配都为0），应该降低内容迁移潜力的权重
            has_direct_match = keyword_score > 0 or category_score > 0
            
            # 综合匹配度计算（优化版：当没有直接关联时，降低匹配度）
            if base_match_score > 0:
                # 如果有base_match_score，说明已经通过Agent计算过语义匹配，使用它
                if has_direct_match:
                    # 有直接关联时，使用正常权重
                    match_score = (
                        content_migration_potential * 0.50 +  # 内容迁移潜力（降低权重）
                        base_match_score * 0.25 +              # 语义关联（使用Agent的结果）
                        direct_relevance * 0.15 +              # 直接关联（提高权重）
                        applicable_categories_match * 0.10     # 适用类目匹配（提高权重）
                    )
                else:
                    # 没有直接关联时，大幅降低内容迁移潜力的权重，提高适用类目匹配的权重
                    match_score = (
                        content_migration_potential * 0.30 +  # 内容迁移潜力（大幅降低权重）
                        base_match_score * 0.20 +              # 语义关联（降低权重）
                        direct_relevance * 0.15 +              # 直接关联（保持）
                        applicable_categories_match * 0.35     # 适用类目匹配（大幅提高权重，因为这是唯一的关联）
                    )
            else:
                # 没有base_match_score时，使用优化后的权重
                if has_direct_match:
                    # 有直接关联时，使用正常权重
                    match_score = (
                        content_migration_potential * 0.50 +  # 内容迁移潜力（降低权重）
                        semantic_relevance * 0.25 +            # 语义关联（简化版）
                        direct_relevance * 0.15 +              # 直接关联（提高权重）
                        applicable_categories_match * 0.10     # 适用类目匹配（提高权重）
                    )
                else:
                    # 没有直接关联时，大幅降低内容迁移潜力的权重，提高适用类目匹配的权重
                    match_score = (
                        content_migration_potential * 0.30 +  # 内容迁移潜力（大幅降低权重）
                        semantic_relevance * 0.20 +            # 语义关联（降低权重）
                        direct_relevance * 0.15 +              # 直接关联（保持）
                        applicable_categories_match * 0.35     # 适用类目匹配（大幅提高权重，因为这是唯一的关联）
                    )
            
            # 重要：当没有直接关联时，即使适用类目有匹配，也应该设置上限
            # 避免间接关联的热点匹配度过高
            if not has_direct_match:
                # 没有直接关联时，匹配度上限为50%
                match_score = min(match_score, 0.5)
                # 如果适用类目匹配是通过同义词（0.8），进一步降低
                if applicable_categories_match == 0.8:
                    match_score = min(match_score, 0.4)  # 同义词匹配上限40%
            
            # 如果内容迁移潜力很高（>=0.6）且适用类目有匹配，即使直接关联度低，也给予基础分数
            # 这体现了对LLM判断的信任，但只在有直接关联时生效
            if has_direct_match and content_migration_potential >= 0.6 and applicable_categories_match > 0 and match_score < 0.3:
                match_score = max(match_score, 0.3)  # 至少30%匹配度
            
            # 不再给0匹配度的热点最小分数，避免低匹配度热点过多
            # 如果计算出的匹配度为0，保持为0，不显示
            
            hotspot_scores.append({
                "hotspot": hotspot,
                "match_score": match_score
            })
        
        # 按匹配度排序，只保留匹配度 >= 阈值的热点
        from app.core.config import settings
        match_threshold = settings.MATCH_SCORE_THRESHOLD
        
        hotspot_scores.sort(key=lambda x: x["match_score"], reverse=True)
        # 过滤掉匹配度低于阈值的热点
        filtered_scores = [
            item for item in hotspot_scores 
            if item["match_score"] >= match_threshold
        ]
        
        # 记录筛选日志
        if len(hotspot_scores) > len(filtered_scores):
            print(
                f"[匹配度筛选] 阈值={match_threshold:.1%}, "
                f"筛选前={len(hotspot_scores)}个, "
                f"筛选后={len(filtered_scores)}个"
            )
        
        # 去重：按标题去重，保留匹配度最高的
        seen_titles = {}
        for item in filtered_scores:
            title = item["hotspot"].title
            if title not in seen_titles:
                seen_titles[title] = item
            else:
                # 如果已存在，保留匹配度更高的
                if item["match_score"] > seen_titles[title]["match_score"]:
                    seen_titles[title] = item
        
        # 转换为列表并重新排序
        unique_hotspots = list(seen_titles.values())
        unique_hotspots.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 不限制数量，通过前端优化显示效果
        top_hotspots = unique_hotspots[:limit]
        
        category_data = {
            "category": live_room.category,
            "live_room_name": live_room.name,
            "live_room_id": live_room.id,
            "hotspots": [
                {
                    "id": item["hotspot"].id,
                    "title": item["hotspot"].title,
                    "url": item["hotspot"].url,
                    "heat_score": item["hotspot"].heat_score or 0,
                    "match_score": item["match_score"],
                    "tags": item["hotspot"].tags or [],
                    "platform": item["hotspot"].platform  # 添加平台信息
                }
                for item in top_hotspots
            ]
        }
        
        result["categories"].append(category_data)
    
    return result


@router.get("/{hotspot_id}")
async def get_hotspot_detail(
    hotspot_id: str,
    db: Session = Depends(get_db)
):
    """获取热点详情"""
    hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
    if not hotspot:
        raise HTTPException(status_code=404, detail="热点不存在")
    
    # 解析JSON字段
    video_structure = None
    content_analysis = None
    if hotspot.video_structure:
        import json
        if isinstance(hotspot.video_structure, str):
            try:
                video_structure = json.loads(hotspot.video_structure)
            except:
                video_structure = None
        else:
            video_structure = hotspot.video_structure
    
    if hotspot.content_analysis:
        import json
        if isinstance(hotspot.content_analysis, str):
            try:
                content_analysis = json.loads(hotspot.content_analysis)
            except:
                content_analysis = None
        else:
            content_analysis = hotspot.content_analysis
    
    return {
        "id": hotspot.id,
        "title": hotspot.title,
        "url": hotspot.url,
        "platform": hotspot.platform,
        "tags": hotspot.tags,
        "heat_score": hotspot.heat_score,
        "match_score": hotspot.match_score,
        "publish_time": hotspot.publish_time.isoformat() if hotspot.publish_time else None,
        "video_info": hotspot.video_info,
        "video_structure": video_structure,
        "content_analysis": content_analysis,
        "content_compact": hotspot.content_compact,
        "created_at": hotspot.created_at.isoformat(),
        "updated_at": hotspot.updated_at.isoformat()
    }


class FilterRequest(BaseModel):
    """筛选请求"""
    keywords: List[str]
    live_room_id: Optional[str] = None


@router.post("/filter")
async def filter_hotspots(
    request: FilterRequest,
    db: Session = Depends(get_db)
):
    """关键词筛选热点"""
    service = HotspotMonitorService()
    
    # 获取所有热点（简化版，实际应该从数据库获取）
    # 这里先获取最近的热点
    query = db.query(Hotspot).order_by(Hotspot.created_at.desc()).limit(100)
    hotspots_data = [
        {
            "title": h.title,
            "url": h.url,
            "tags": h.tags or [],
            "heat_score": h.heat_score,
            "publish_time": h.publish_time,
            "video_info": h.video_info
        }
        for h in query.all()
    ]
    
    # 获取直播间（如果提供）
    live_room = None
    if request.live_room_id:
        live_room = db.query(LiveRoom).filter(LiveRoom.id == request.live_room_id).first()
        if not live_room:
            raise HTTPException(status_code=404, detail="直播间不存在")
    
    # 筛选热点
    filtered = service.filter_hotspots(hotspots_data, request.keywords, live_room)
    
    return {
        "filtered_count": len(filtered),
        "items": filtered
    }

