"""
热点监控服务
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from loguru import logger

from app.models.hotspot import Hotspot
from app.models.product import LiveRoom, Product
from app.utils.trendradar import TrendRadarClient
from app.utils.feishu import FeishuClient
from app.utils.embedding import EmbeddingClient
from app.utils.sentiment import SentimentClient
from app.agents.relevance_analysis_agent import RelevanceAnalysisAgent
from app.crawlers.trendradar_crawler import TrendRadarCrawler
from app.utils.firecrawl import FirecrawlClient
from app.core.config import settings


class HotspotMonitorService:
    """热点监控服务（使用Agents）"""
    
    def __init__(
        self,
        use_agent: bool = True,
        use_direct_crawler: bool = None
    ):
        """
        初始化服务
        
        Args:
            use_agent: 是否使用Agent架构，默认True
            use_direct_crawler: 是否优先使用直接爬虫（主要方案），None时从配置读取，默认True
                               如果为False或直接爬虫失败，则使用MCP服务（降级方案）
        """
        self.use_agent = use_agent
        
        # 从配置读取或使用传入参数
        if use_direct_crawler is None:
            self.use_direct_crawler = getattr(settings, 'TRENDRADAR_USE_DIRECT_CRAWLER', True)
        else:
            self.use_direct_crawler = use_direct_crawler
        
        self.trendradar_client = TrendRadarClient()  # MCP客户端（降级方案）
        self.feishu_client = FeishuClient()
        
        # 直接爬虫（主要方案）
        if self.use_direct_crawler:
            self.crawler = TrendRadarCrawler()
        else:
            self.crawler = None
        
        # Firecrawl 客户端（增强功能，可选）
        self.use_firecrawl = getattr(settings, 'FIRECRAWL_ENABLED', False)
        if self.use_firecrawl:
            try:
                self.firecrawl_client = FirecrawlClient()
                logger.info("Firecrawl 客户端已初始化（增强功能已启用）")
            except Exception as e:
                logger.warning(f"Firecrawl 客户端初始化失败: {e}，增强功能将不可用")
                self.firecrawl_client = None
                self.use_firecrawl = False
        else:
            self.firecrawl_client = None
        
        if use_agent:
            self.relevance_agent = RelevanceAnalysisAgent()
        else:
            # 保留原有实现作为fallback
            self.embedding_client = EmbeddingClient()
            self.sentiment_client = SentimentClient()
    
    async def fetch_hotspots(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        从TrendRadar获取热点列表
        
        优先使用直接爬虫（主要方案），失败时自动降级到MCP服务（降级方案）
        
        Args:
            platform: 平台标识
            date: 目标日期
            
        Returns:
            热点列表
        """
        logger.info(f"开始获取热点，平台: {platform}, 使用直接爬虫: {self.use_direct_crawler}")
        
        # 方案1：直接爬虫（主要方案）
        if self.use_direct_crawler and self.crawler:
            try:
                logger.info(f"尝试使用直接爬虫获取 {platform} 的热点")
                hotspots = await self.crawler.crawl_hotspots(platform, date)
                
                if hotspots and len(hotspots) > 0:
                    logger.info(f"直接爬虫成功获取 {len(hotspots)} 个热点")
                    return hotspots
                else:
                    logger.warning(f"直接爬虫返回空结果，降级到MCP服务")
            except Exception as e:
                logger.warning(f"直接爬虫失败: {e}，降级到MCP服务")
        
        # 方案2：MCP服务（降级方案）
        try:
            logger.info(f"使用MCP服务获取 {platform} 的热点（降级方案）")
            hotspots = await self.trendradar_client.get_hotspots(platform, date)
            logger.info(f"MCP服务成功获取 {len(hotspots)} 个热点")
            return hotspots
        except Exception as e:
            logger.error(f"MCP服务也失败: {e}")
            # 如果MCP也失败，返回空列表或抛出异常
            raise Exception(f"所有热点获取方案都失败: 直接爬虫失败，MCP服务也失败: {e}")
    
    def get_main_product(
        self,
        db: Session,
        live_room_id: str,
        target_date: Optional[datetime] = None
    ) -> Optional[Product]:
        """获取直播间的主推商品
        
        Args:
            db: 数据库会话
            live_room_id: 直播间ID
            target_date: 目标日期，如果提供则查找该日期的商品
            
        Returns:
            主推商品对象，如果不存在返回None
        """
        query = db.query(Product).filter(Product.live_room_id == live_room_id)
        
        if target_date:
            from datetime import date
            query = query.filter(Product.live_date == target_date.date())
        
        # 获取最新的商品（按创建时间或直播日期）
        product = query.order_by(
            Product.live_date.desc(),
            Product.created_at.desc()
        ).first()
        
        return product
    
    async def _calculate_live_room_match_score(
        self,
        hotspot: Dict[str, Any],
        live_room: LiveRoom
    ) -> float:
        """计算热点与直播间的匹配度（基于关键词和语义相似度）
        
        Args:
            hotspot: 热点数据
            live_room: 直播间对象
            
        Returns:
            匹配度分数（0-1）
        """
        hotspot_text = f"{hotspot.get('title', '')} {' '.join(hotspot.get('tags', []))}"
        keywords = live_room.keywords or []
        category = live_room.category or ""
        
        # 1. 关键词匹配（40%权重）
        keyword_score = 0.0
        matched_keywords_list = []
        if keywords:
            hotspot_lower = hotspot_text.lower()
            for kw in keywords:
                if kw.lower() in hotspot_lower:
                    matched_keywords_list.append(kw)
            matched_count = len(matched_keywords_list)
            keyword_score = min(1.0, matched_count / len(keywords)) if keywords else 0.0
        
        # 2. 类目匹配（20%权重）
        category_score = 0.0
        category_matched = False
        if category:
            # 检查类目关键词是否在热点文本中
            category_keywords = category.split('、')  # 支持多个类目（用、分隔）
            for cat_kw in category_keywords:
                if cat_kw.strip().lower() in hotspot_text.lower():
                    category_score = 1.0
                    category_matched = True
                    break
        
        # 3. 语义相似度（40%权重）- 如果有Agent
        semantic_score = 0.0
        semantic_details = {}
        if self.use_agent and self.relevance_agent:
            try:
                # 构建直播间文本（包含更丰富的上下文信息）
                live_room_text = f"""
直播间名称：{live_room.name}
类目：{category}
关键词：{', '.join(keywords)}
定位：{live_room.ip_character or '未设置'}
风格：{live_room.style or '未设置'}
"""
                result = await self.relevance_agent.execute({
                    "hotspot_text": hotspot_text,
                    "product_text": live_room_text,
                    "hotspot_tags": hotspot.get('tags', []),
                    "product_category": category
                })
                semantic_score = result.get("relevance_score", 0.0)
                semantic_details = {
                    "semantic_score": result.get("semantic_score", 0.0),
                    "sentiment_score": result.get("sentiment_score", 0.0),
                    "keyword_score": result.get("keyword_score", 0.0)
                }
            except Exception as e:
                logger.warning(f"语义匹配计算失败: {e}，使用关键词匹配")
        
        # 如果没有语义匹配，使用简单的文本相似度
        if semantic_score == 0.0:
            # 简单的文本相似度：检查标题中是否包含关键词
            if keywords:
                matched = sum(1 for kw in keywords if kw.lower() in hotspot_text.lower())
                semantic_score = matched / len(keywords) if keywords else 0.0
        
        # 检查热点是否有ContentAnalysisAgent的分析结果（电商适配性）
        ecommerce_score = 0.0
        applicable_categories_match = 0.0
        
        # 尝试从hotspot对象获取content_analysis（如果是数据库对象）
        hotspot_obj = hotspot if hasattr(hotspot, 'content_analysis') else None
        if hotspot_obj and hotspot_obj.content_analysis:
            try:
                content_analysis = hotspot_obj.content_analysis
                if isinstance(content_analysis, str):
                    import json
                    content_analysis = json.loads(content_analysis)
                
                # 获取电商适配性评分
                ecommerce_fit = content_analysis.get("ecommerce_fit", {})
                if isinstance(ecommerce_fit, dict):
                    ecommerce_score = float(ecommerce_fit.get("score", 0.0))
                    
                    # 检查适用类目是否与直播间类目匹配
                    # 信任LLM的判断，直接使用ContentAnalysisAgent给出的适用类目
                    applicable_categories = ecommerce_fit.get("applicable_categories", [])
                    if applicable_categories and category:
                        category_keywords = [cat.strip().lower() for cat in category.split('、')]
                        
                        # 直接匹配：检查直播间类目关键词是否在适用类目中
                        # 相信LLM已经做了智能判断，不需要硬编码的映射
                        matched_categories = [
                            app_cat for app_cat in applicable_categories
                            if any(cat_kw in app_cat.lower() or app_cat.lower() in cat_kw 
                                   for cat_kw in category_keywords)
                        ]
                        
                        if matched_categories:
                            applicable_categories_match = 1.0
                        else:
                            # 如果适用类目与直播间类目完全不匹配，不给分数
                            # 相信LLM的判断：如果LLM没有将直播间类目列为适用类目，说明不相关
                            applicable_categories_match = 0.0
            except Exception as e:
                logger.warning(f"解析content_analysis失败: {e}")
        
        # 综合计算匹配度（优化版：加入电商适配性）
        match_score = (
            keyword_score * 0.25 +
            category_score * 0.15 +
            semantic_score * 0.15 +
            ecommerce_score * 0.35 +  # 电商适配性权重最高
            applicable_categories_match * 0.1  # 适用类目匹配
        )
        
        # 如果电商适配性很高（>=70%）且适用类目有匹配，即使关键词/类目不匹配，也给予基础分数
        # 但如果适用类目完全不匹配，不应该给保底分数
        if ecommerce_score >= 0.7 and applicable_categories_match > 0 and match_score < 0.3:
            match_score = max(match_score, 0.3)  # 至少30%匹配度
        
        # 详细日志输出
        logger.info(f"""
=== 匹配度详细评分 ===
热点: {hotspot.get('title', '')[:50]}
直播间: {live_room.name} ({category})
关键词匹配: {keyword_score:.3f} (匹配的关键词: {matched_keywords_list})
类目匹配: {category_score:.3f} (类目: {category}, 匹配: {category_matched})
语义匹配: {semantic_score:.3f} {f'(详情: {semantic_details})' if semantic_details else ''}
综合匹配度: {match_score:.3f}
""")
        
        return max(0.0, min(1.0, match_score))
    
    async def calculate_product_match_score(
        self,
        hotspot: Dict[str, Any],
        product: Product
    ) -> float:
        """计算热点与商品的匹配度（基于语义关联度和情感关联度）
        
        Args:
            hotspot: 热点数据
            product: 商品对象
            
        Returns:
            匹配度分数（0-1）
        """
        if self.use_agent:
            # 使用Agent架构
            return await self._calculate_match_score_with_agent(hotspot, product)
        else:
            # 使用传统方法
            return await self._calculate_match_score_legacy(hotspot, product)
    
    async def _calculate_match_score_with_agent(
        self,
        hotspot: Dict[str, Any],
        product: Product
    ) -> float:
        """使用Agent计算匹配度"""
        # 构建热点文本
        hotspot_text = f"{hotspot.get('title', '')} {' '.join(hotspot.get('tags', []))}"
        
        # 构建商品文本
        product_text_parts = [
            product.name or "",
            product.category or "",
            product.description or "",
        ]
        if product.selling_points:
            product_text_parts.extend(product.selling_points)
        product_text = " ".join([p for p in product_text_parts if p])
        
        try:
            result = await self.relevance_agent.execute({
                "hotspot_text": hotspot_text,
                "product_text": product_text,
                "hotspot_tags": hotspot.get('tags', []),
                "product_category": product.category
            })
            
            return result.get("relevance_score", 0.0)
        except Exception as e:
            logger.error(f"Agent匹配度计算失败: {e}，回退到传统方法")
            return await self._calculate_match_score_legacy(hotspot, product)
    
    async def _calculate_match_score_legacy(
        self,
        hotspot: Dict[str, Any],
        product: Product
    ) -> float:
        """传统匹配度计算方法（作为fallback）"""
        # 构建热点文本
        hotspot_text = f"{hotspot.get('title', '')} {' '.join(hotspot.get('tags', []))}"
        
        # 构建商品文本
        product_text_parts = [
            product.name or "",
            product.category or "",
            product.description or "",
        ]
        if product.selling_points:
            product_text_parts.extend(product.selling_points)
        product_text = " ".join([p for p in product_text_parts if p])
        
        # 1. 计算语义关联度（60%权重）
        semantic_score = 0.0
        try:
            semantic_score = await self.embedding_client.calculate_semantic_similarity(
                hotspot_text, product_text
            )
        except Exception as e:
            logger.warning(f"计算语义关联度失败: {e}，使用关键词匹配作为fallback")
            # Fallback: 简单的关键词匹配
            hotspot_lower = hotspot_text.lower()
            product_lower = product_text.lower()
            if product.category and product.category.lower() in hotspot_lower:
                semantic_score = 0.5
            if product.name and product.name.lower() in hotspot_lower:
                semantic_score = max(semantic_score, 0.6)
        
        # 2. 计算情感关联度（30%权重）
        sentiment_score = 0.5  # 默认中性
        try:
            hotspot_sentiment = await self.sentiment_client.analyze_sentiment(hotspot_text)
            product_sentiment = await self.sentiment_client.analyze_sentiment(product_text)
            sentiment_score = self.sentiment_client.calculate_sentiment_similarity(
                hotspot_sentiment, product_sentiment
            )
        except Exception as e:
            logger.warning(f"计算情感关联度失败: {e}，使用默认值")
        
        # 3. 关键词匹配（10%权重）
        keyword_score = 0.0
        if product.category:
            category_lower = product.category.lower()
            hotspot_lower = hotspot_text.lower()
            if category_lower in hotspot_lower:
                keyword_score = 0.5
            if product.name:
                name_lower = product.name.lower()
                if name_lower in hotspot_lower:
                    keyword_score = max(keyword_score, 0.8)
        
        # 综合计算匹配度
        match_score = (
            semantic_score * 0.6 +
            sentiment_score * 0.3 +
            keyword_score * 0.1
        )
        
        return max(0.0, min(1.0, match_score))
    
    async def filter_hotspots_with_semantic(
        self,
        db: Session,
        hotspots: List[Dict[str, Any]],
        live_room_id: Optional[str] = None,
        target_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """使用语义关联度和情感关联度筛选热点
        
        Args:
            db: 数据库会话
            hotspots: 热点列表
            live_room_id: 直播间ID（可选）
            target_date: 目标日期（可选）
            
        Returns:
            筛选后的热点列表，包含match_score字段
        """
        filtered_hotspots = []
        
        # 获取主推商品
        product = None
        if live_room_id:
            product = self.get_main_product(db, live_room_id, target_date)
            if not product:
                logger.warning(f"直播间 {live_room_id} 没有找到主推商品")
        
        # 获取直播间信息（用于关键词匹配）
        live_room = None
        if live_room_id:
            live_room = db.query(LiveRoom).filter(LiveRoom.id == live_room_id).first()
        
        for hotspot in hotspots:
            # 计算匹配度
            if product:
                # 有商品时，使用商品匹配度计算
                match_score = await self.calculate_product_match_score(hotspot, product)
            elif live_room:
                # 没有商品但有直播间时，使用直播间关键词和语义匹配
                match_score = await self._calculate_live_room_match_score(hotspot, live_room)
            else:
                # 既没有商品也没有直播间，匹配度为0
                match_score = 0.0
            
            # 保留所有热点（即使匹配度为0也保留，用于测试和展示）
            hotspot["match_score"] = match_score
            filtered_hotspots.append(hotspot)
        
        # 按匹配度排序
        filtered_hotspots.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        logger.info(f"语义筛选后剩余 {len(filtered_hotspots)} 个热点")
        return filtered_hotspots
    
    def filter_hotspots(
        self,
        hotspots: List[Dict[str, Any]],
        keywords: List[str],
        live_room: Optional[LiveRoom] = None
    ) -> List[Dict[str, Any]]:
        """根据关键词筛选热点
        
        Args:
            hotspots: 热点列表
            keywords: 关键词列表，支持：
                - 普通词：包含即可，提高匹配度
                - 必须词（+标记）：必须包含，否则不匹配
                - 过滤词（!标记）：包含则排除
            live_room: 直播间对象（可选，如果提供会使用直播间的关键词）
        
        Returns:
            筛选后的热点列表，包含match_score字段
        """
        if live_room and live_room.keywords:
            # 如果提供了直播间，合并关键词
            all_keywords = list(set(keywords + live_room.keywords))
        else:
            all_keywords = keywords
        
        # 分类关键词
        required_keywords = []  # 必须词（+标记）
        normal_keywords = []    # 普通词
        exclude_keywords = []   # 过滤词（!标记）
        
        for keyword in all_keywords:
            keyword = keyword.strip()
            if keyword.startswith("+"):
                required_keywords.append(keyword[1:].lower())
            elif keyword.startswith("!"):
                exclude_keywords.append(keyword[1:].lower())
            else:
                normal_keywords.append(keyword.lower())
        
        filtered_hotspots = []
        
        for hotspot in hotspots:
            title = hotspot.get("title", "").lower()
            tags = [tag.lower() for tag in hotspot.get("tags", [])]
            content = title + " " + " ".join(tags)
            
            # 检查过滤词
            has_exclude = any(exclude_word in content for exclude_word in exclude_keywords)
            if has_exclude:
                continue
            
            # 检查必须词
            has_all_required = all(
                required_word in content for required_word in required_keywords
            )
            if required_keywords and not has_all_required:
                continue
            
            # 计算匹配度
            match_score = 0.0
            
            # 必须词权重：50%
            if required_keywords:
                required_matches = sum(
                    1 for word in required_keywords if word in content
                )
                match_score += (required_matches / len(required_keywords)) * 0.5
            
            # 普通词权重：30%
            if normal_keywords:
                normal_matches = sum(
                    1 for word in normal_keywords if word in content
                )
                match_score += (normal_matches / len(normal_keywords)) * 0.3
            
            # 过滤词权重：-100%（已排除，这里不需要处理）
            
            # 只保留匹配度>0的热点
            if match_score > 0:
                hotspot["match_score"] = match_score
                filtered_hotspots.append(hotspot)
        
        # 按匹配度排序
        filtered_hotspots.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        logger.info(f"筛选后剩余 {len(filtered_hotspots)} 个热点")
        return filtered_hotspots
    
    def save_hotspots(
        self,
        db: Session,
        hotspots: List[Dict[str, Any]],
        platform: str = "douyin"
    ) -> int:
        """保存热点到数据库"""
        saved_count = 0
        
        for hotspot_data in hotspots:
            url = hotspot_data.get("url", "")
            if not url:
                continue
            
            # 检查是否已存在
            existing = db.query(Hotspot).filter(Hotspot.url == url).first()
            if existing:
                # 更新现有热点
                existing.title = hotspot_data.get("title", existing.title)
                existing.heat_score = hotspot_data.get("heat_score", existing.heat_score)
                existing.match_score = hotspot_data.get("match_score", existing.match_score)
                existing.tags = hotspot_data.get("tags", existing.tags)
                existing.video_info = hotspot_data.get("video_info", existing.video_info)
                # 新增字段：内容Compact相关
                if "content_compact" in hotspot_data:
                    existing.content_compact = hotspot_data.get("content_compact")
                if "video_structure" in hotspot_data:
                    existing.video_structure = hotspot_data.get("video_structure")
                if "content_analysis" in hotspot_data:
                    existing.content_analysis = hotspot_data.get("content_analysis")
                if hotspot_data.get("publish_time"):
                    existing.publish_time = hotspot_data.get("publish_time")
                existing.updated_at = datetime.now()
                saved_count += 1
            else:
                # 创建新热点
                new_hotspot = Hotspot(
                    id=str(uuid.uuid4()),
                    title=hotspot_data.get("title", ""),
                    url=url,
                    platform=platform,
                    tags=hotspot_data.get("tags"),
                    heat_score=hotspot_data.get("heat_score"),
                    publish_time=hotspot_data.get("publish_time"),
                    video_info=hotspot_data.get("video_info"),
                    match_score=hotspot_data.get("match_score"),
                    # 新增字段：内容Compact相关
                    content_compact=hotspot_data.get("content_compact"),
                    video_structure=hotspot_data.get("video_structure"),
                    content_analysis=hotspot_data.get("content_analysis"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(new_hotspot)
                saved_count += 1
        
        db.commit()
        logger.info(f"成功保存 {saved_count} 个热点")
        return saved_count
    
    async def enrich_hotspot_with_firecrawl(
        self,
        hotspot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用 Firecrawl 增强热点信息（提取详细信息）
        
        Args:
            hotspot: 热点数据字典
            
        Returns:
            增强后的热点数据（包含提取的详细信息）
        """
        if not self.use_firecrawl or not self.firecrawl_client:
            logger.debug("Firecrawl 未启用，跳过热点详情提取")
            return hotspot
        
        url = hotspot.get("url") or hotspot.get("mobileUrl")
        if not url:
            logger.debug("热点没有 URL，跳过 Firecrawl 提取")
            return hotspot
        
        try:
            logger.info(f"使用 Firecrawl 提取热点详情: {url}")
            
            # 使用 Firecrawl 提取结构化信息
            extracted_data = await self.firecrawl_client.extract_hotspot_details(url)
            
            # 合并提取的数据到热点
            if isinstance(extracted_data, dict):
                # 如果返回的是字典，直接合并
                if "content" in extracted_data:
                    # MCP 返回格式：{"content": [{"type": "text", "text": {...}}]}
                    content = extracted_data.get("content", [])
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")
                        try:
                            import json
                            extracted_info = json.loads(text_content) if isinstance(text_content, str) else text_content
                            if isinstance(extracted_info, dict):
                                hotspot.update(extracted_info)
                        except:
                            # 如果不是 JSON，作为文本内容
                            hotspot["extracted_content"] = text_content
                else:
                    # 直接是提取的数据
                    hotspot.update(extracted_data)
            
            logger.info(f"成功提取热点详情: {hotspot.get('title', 'Unknown')}")
            return hotspot
            
        except Exception as e:
            logger.warning(f"Firecrawl 提取热点详情失败: {e}，使用原始数据")
            return hotspot
    
    async def enrich_hotspots_batch(
        self,
        hotspots: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量使用 Firecrawl 增强热点信息
        
        Args:
            hotspots: 热点列表
            max_concurrent: 最大并发数
            
        Returns:
            增强后的热点列表
        """
        if not self.use_firecrawl or not self.firecrawl_client:
            logger.debug("Firecrawl 未启用，跳过批量增强")
            return hotspots
        
        import asyncio
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def enrich_with_semaphore(hotspot):
            async with semaphore:
                return await self.enrich_hotspot_with_firecrawl(hotspot)
        
        # 并发处理所有热点
        enriched_hotspots = await asyncio.gather(
            *[enrich_with_semaphore(hotspot) for hotspot in hotspots],
            return_exceptions=True
        )
        
        # 处理异常（保留原始数据）
        result = []
        for i, enriched in enumerate(enriched_hotspots):
            if isinstance(enriched, Exception):
                logger.warning(f"增强热点 {i} 失败: {enriched}，使用原始数据")
                result.append(hotspots[i])
            else:
                result.append(enriched)
        
        logger.info(f"批量增强完成: {len(result)}/{len(hotspots)} 个热点")
        return result
    
    async def push_to_feishu(
        self,
        db: Session,
        live_room_id: Optional[str] = None
    ) -> bool:
        """推送热点到飞书
        
        Args:
            db: 数据库会话
            live_room_id: 直播间ID，如果提供则只推送该直播间的热点
        
        Returns:
            是否成功
        """
        try:
            # 获取今日热点
            from datetime import date, time
            today = date.today()
            start_time = datetime.combine(today, time.min)
            end_time = datetime.combine(today, time.max)
            
            query = db.query(Hotspot).filter(
                and_(
                    Hotspot.created_at >= start_time,
                    Hotspot.created_at <= end_time,
                    Hotspot.match_score > 0.7  # 只推送匹配度>70%的热点
                )
            ).order_by(Hotspot.match_score.desc()).limit(10)
            
            if live_room_id:
                # 如果指定了直播间，需要根据直播间的关键词筛选
                live_room = db.query(LiveRoom).filter(LiveRoom.id == live_room_id).first()
                if not live_room:
                    logger.warning(f"直播间 {live_room_id} 不存在")
                    return False
                
                # 这里简化处理，实际应该根据关键词进一步筛选
                hotspots = query.all()
                live_room_name = live_room.name
            else:
                # 获取所有直播间的热点
                live_rooms = db.query(LiveRoom).all()
                hotspots = query.all()
                
                # 按直播间分组推送
                for live_room in live_rooms:
                    # 简化处理：推送所有热点，实际应该根据关键词筛选
                    card_data = self.feishu_client.create_hotspot_card(
                        [{
                            "title": h.title,
                            "url": h.url,
                            "heat_score": h.heat_score or 0,
                            "tags": h.tags or []
                        } for h in hotspots[:5]],
                        live_room.name
                    )
                    await self.feishu_client.send_message(card_data)
                
                return True
            
            # 推送单个直播间
            card_data = self.feishu_client.create_hotspot_card(
                [{
                    "title": h.title,
                    "url": h.url,
                    "heat_score": h.heat_score or 0,
                    "tags": h.tags or []
                } for h in hotspots[:5]],
                live_room_name
            )
            await self.feishu_client.send_message(card_data)
            
            logger.info(f"成功推送热点到飞书")
            return True
            
        except Exception as e:
            logger.error(f"推送热点到飞书失败: {e}")
            return False
    
    def get_hotspots_by_live_room(
        self,
        db: Session,
        live_room_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Hotspot], int]:
        """根据直播间获取热点"""
        live_room = db.query(LiveRoom).filter(LiveRoom.id == live_room_id).first()
        if not live_room:
            return [], 0
        
        # 根据直播间的关键词筛选热点
        keywords = live_room.keywords or []
        query = db.query(Hotspot)
        
        if keywords:
            # 构建关键词搜索条件（简化版，实际应该使用全文搜索）
            conditions = []
            for keyword in keywords:
                conditions.append(Hotspot.title.ilike(f"%{keyword}%"))
            
            if conditions:
                query = query.filter(or_(*conditions))
        
        total = query.count()
        hotspots = query.order_by(
            Hotspot.match_score.desc(),
            Hotspot.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return hotspots, total

