"""
小红书爬虫实现
参考 BettaFish 项目的 MindSpider 模块架构，实现小红书热点数据抓取
"""
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger

from app.crawlers.base import BaseCrawler


class XiaohongshuCrawler(BaseCrawler):
    """
    小红书爬虫（参考BettaFish的MindSpider实现）
    
    注意：这是一个基础框架，需要根据实际页面结构完善实现
    """
    
    def __init__(
        self,
        base_url: str = "https://www.xiaohongshu.com",
        request_interval: int = 2000,  # 2秒间隔，避免被限流
        max_retries: int = 2,
    ):
        """
        初始化小红书爬虫
        
        Args:
            base_url: 小红书基础URL
            request_interval: 请求间隔（毫秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url
        self.request_interval = request_interval
        self.max_retries = max_retries
        
        # 小红书数据源配置
        # 注意：小红书没有公开的热搜API，需要通过其他方式获取热点
        # 方案1：通过搜索热门关键词（推荐）
        # 方案2：通过分析热门笔记（需要登录）
        # 方案3：使用第三方数据聚合服务
        
        # 热门关键词列表（用于搜索发现热点）
        # 这些关键词可以根据实际情况更新
        self.hot_keywords = [
            "热门", "爆款", "推荐", "好物", "种草", "穿搭", "美妆", 
            "美食", "旅行", "健身", "护肤", "时尚", "生活", "分享"
        ]
        
        # 搜索API端点（需要根据实际API调整）
        self.search_api_url = f"{base_url}/api/sns/web/v1/search/notes"
        
        # 探索页面（可能需要登录）
        self.explore_url = f"{base_url}/explore"
        
    async def crawl_hotspots(
        self,
        platform: str = "xiaohongshu",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        爬取小红书热点数据
        
        参考 BettaFish MindSpider 的实现方式
        
        Args:
            platform: 平台标识（固定为 "xiaohongshu"）
            date: 目标日期，None 表示最新数据
            
        Returns:
            热点列表，格式与 BaseCrawler 规范一致
        """
        logger.info(f"开始爬取小红书热点数据（参考BettaFish实现）")
        
        hotspots = []
        retries = 0
        
        while retries <= self.max_retries:
            try:
                # 方案1：尝试通过搜索API获取热门笔记（推荐）
                # 小红书可能通过搜索热门关键词来发现热点
                try:
                    search_hotspots = await self._fetch_from_search()
                    if search_hotspots:
                        hotspots.extend(search_hotspots)
                        logger.info(f"通过搜索API获取到 {len(search_hotspots)} 个热点")
                except Exception as e:
                    logger.debug(f"搜索API获取失败: {e}")
                
                # 方案2：尝试通过探索页面获取（可能需要登录）
                if not hotspots:
                    try:
                        explore_hotspots = await self._fetch_from_url(self.explore_url)
                        if explore_hotspots:
                            hotspots.extend(explore_hotspots)
                            logger.info(f"通过探索页面获取到 {len(explore_hotspots)} 个热点")
                    except Exception as e:
                        logger.debug(f"探索页面获取失败: {e}")
                
                # 如果获取到数据，返回
                if hotspots:
                    # 去重并排序
                    hotspots = self._deduplicate_hotspots(hotspots)
                    logger.info(f"成功爬取小红书 {len(hotspots)} 个热点")
                    return hotspots[:30]  # 限制返回30个热点
                else:
                    logger.warning(f"未获取到热点数据，所有方案都失败")
                    return []
                    
            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    logger.warning(f"爬取失败: {e}，{2}秒后重试... (尝试 {retries}/{self.max_retries})")
                    await asyncio.sleep(2)
                else:
                    logger.error(f"爬取失败（已重试 {self.max_retries} 次）: {e}")
                    return []
        
        return []
    
    async def _fetch_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        从指定URL获取热点数据
        
        Args:
            url: 目标URL
            
        Returns:
            热点列表
        """
        # 构建请求头（模拟浏览器，参考BettaFish的实现）
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.xiaohongshu.com/",
            "Origin": "https://www.xiaohongshu.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        }
        
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "").lower()
            
            # 根据响应类型选择解析方法
            if "application/json" in content_type:
                return self._parse_json(response.json())
            elif "text/html" in content_type:
                return self._parse_html(response.text)
            else:
                logger.warning(f"未知的响应类型: {content_type}")
                return []
    
    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        解析HTML页面，提取热点数据
        
        注意：需要根据小红书实际页面结构调整
        参考 BettaFish 的解析逻辑
        
        Args:
            html: HTML内容
            
        Returns:
            热点列表
        """
        hotspots = []
        try:
            # 使用 beautifulsoup4 解析HTML
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logger.error("需要安装 beautifulsoup4: pip install beautifulsoup4")
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # TODO: 根据实际页面结构实现解析逻辑
            # 示例（需要实际验证）:
            # hot_items = soup.select('.hot-item, .trending-item, [class*="hot"]')
            # for index, item in enumerate(hot_items, 1):
            #     title_elem = item.select_one('.title, .name, [class*="title"]')
            #     if title_elem:
            #         title = title_elem.get_text(strip=True)
            #         url_elem = item.select_one('a')
            #         url = url_elem.get('href', '') if url_elem else ''
            #         
            #         hotspot = {
            #             "title": title,
            #             "url": self._normalize_url(url),
            #             "platform": "xiaohongshu",
            #             "rank": index,
            #             "heat_score": max(0, 100 - (index - 1)),
            #             "tags": [],
            #             "timestamp": datetime.now().isoformat(),
            #         }
            #         hotspots.append(hotspot)
            
            # 临时：返回空列表，等待实际页面结构分析
            logger.warning("HTML解析逻辑需要根据小红书实际页面结构实现")
            logger.info("提示：可以访问小红书热搜页面，分析DOM结构，然后实现解析逻辑")
            return []
            
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
            return []
    
    def _parse_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析JSON响应，提取热点数据
        
        注意：需要根据小红书实际API响应格式调整
        参考 BettaFish 的解析逻辑
        
        Args:
            data: JSON数据
            
        Returns:
            热点列表
        """
        hotspots = []
        try:
            # TODO: 根据实际API响应格式实现解析逻辑
            # 示例（需要实际验证）:
            # items = data.get("data", {}).get("items", [])
            # 或者
            # items = data.get("result", {}).get("list", [])
            # 
            # for index, item in enumerate(items, 1):
            #     hotspot = {
            #         "title": item.get("title", item.get("name", "")),
            #         "url": item.get("url", item.get("link", "")),
            #         "platform": "xiaohongshu",
            #         "rank": index,
            #         "heat_score": item.get("heat", item.get("score", max(0, 100 - (index - 1)))),
            #         "tags": item.get("tags", []),
            #         "timestamp": datetime.now().isoformat(),
            #     }
            #     hotspots.append(hotspot)
            
            # 临时：返回空列表，等待实际API响应格式分析
            logger.warning("JSON解析逻辑需要根据小红书实际API响应格式实现")
            logger.info("提示：可以抓取小红书API请求，分析响应格式，然后实现解析逻辑")
            return []
            
        except Exception as e:
            logger.error(f"JSON解析失败: {e}")
            return []
    
    async def _fetch_from_search(self) -> List[Dict[str, Any]]:
        """
        通过搜索API获取热门笔记（作为热点数据）
        
        参考 BettaFish 的实现思路：通过搜索热门关键词来发现热点
        
        Returns:
            热点列表
        """
        hotspots = []
        
        # 选择前几个热门关键词进行搜索
        keywords_to_search = self.hot_keywords[:3]  # 只搜索前3个关键词，避免请求过多
        
        for keyword in keywords_to_search:
            try:
                # 构建搜索请求
                # 注意：小红书搜索API可能需要特殊参数，这里提供基础框架
                search_params = {
                    "keyword": keyword,
                    "page": 1,
                    "page_size": 10,  # 每个关键词获取10条
                }
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.xiaohongshu.com/",
                    "Origin": "https://www.xiaohongshu.com",
                }
                
                async with httpx.AsyncClient(
                    timeout=15.0,
                    follow_redirects=True,
                    headers=headers
                ) as client:
                    response = await client.get(self.search_api_url, params=search_params)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            # 解析搜索结果
                            items = self._parse_search_results(data, keyword)
                            if items:
                                hotspots.extend(items)
                                logger.debug(f"关键词 '{keyword}' 搜索到 {len(items)} 条热点")
                        except Exception as e:
                            logger.debug(f"解析搜索结果失败: {e}")
                    else:
                        logger.debug(f"搜索API返回 {response.status_code}，可能需要登录或特殊处理")
                
                # 请求间隔，避免被限流
                await asyncio.sleep(self.request_interval / 1000)
                
            except Exception as e:
                logger.debug(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        return hotspots
    
    def _parse_search_results(self, data: Dict[str, Any], keyword: str) -> List[Dict[str, Any]]:
        """
        解析搜索结果，提取热点数据
        
        注意：需要根据小红书实际API响应格式调整
        
        Args:
            data: API响应数据
            keyword: 搜索关键词
            
        Returns:
            热点列表
        """
        hotspots = []
        try:
            # 尝试多种可能的响应格式
            items = None
            
            # 格式1: data.items
            if "data" in data and "items" in data["data"]:
                items = data["data"]["items"]
            # 格式2: result.items
            elif "result" in data and "items" in data["result"]:
                items = data["result"]["items"]
            # 格式3: items
            elif "items" in data:
                items = data["items"]
            # 格式4: data.notes
            elif "data" in data and "notes" in data["data"]:
                items = data["data"]["notes"]
            
            if not items:
                logger.debug(f"未找到搜索结果，响应格式: {list(data.keys())}")
                return []
            
            for index, item in enumerate(items[:10], 1):  # 每个关键词最多取10条
                # 尝试提取标题
                title = (
                    item.get("title") or 
                    item.get("desc") or 
                    item.get("note_card", {}).get("display_title") or
                    item.get("note_card", {}).get("title") or
                    f"{keyword}相关热点{index}"
                )
                
                # 尝试提取URL
                note_id = item.get("id") or item.get("note_id") or item.get("note_card", {}).get("note_id")
                url = ""
                if note_id:
                    url = f"{self.base_url}/explore/{note_id}"
                
                # 尝试提取热度（点赞数、收藏数等）
                interact_info = item.get("interact_info", {})
                like_count = interact_info.get("liked_count", 0) if isinstance(interact_info, dict) else 0
                heat_score = min(100, like_count // 10)  # 简单的热度计算
                
                hotspot = {
                    "title": title,
                    "url": url,
                    "platform": "xiaohongshu",
                    "rank": index,
                    "heat_score": heat_score if heat_score > 0 else max(0, 100 - (index - 1)),
                    "tags": [keyword],  # 使用搜索关键词作为标签
                    "timestamp": datetime.now().isoformat(),
                }
                hotspots.append(hotspot)
            
            return hotspots
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
            return []
    
    def _deduplicate_hotspots(self, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重热点数据（根据标题相似度）
        
        Args:
            hotspots: 原始热点列表
            
        Returns:
            去重后的热点列表
        """
        if not hotspots:
            return []
        
        # 简单的去重：根据标题
        seen_titles = set()
        unique_hotspots = []
        
        for hotspot in hotspots:
            title = hotspot.get("title", "").strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_hotspots.append(hotspot)
        
        # 按热度排序
        unique_hotspots.sort(key=lambda x: x.get("heat_score", 0), reverse=True)
        
        return unique_hotspots
    
    def _normalize_url(self, url: str) -> str:
        """
        标准化URL（处理相对路径等）
        
        Args:
            url: 原始URL
            
        Returns:
            标准化后的URL
        """
        if not url:
            return ""
        
        # 如果是相对路径，转换为绝对路径
        if url.startswith("/"):
            return f"{self.base_url}{url}"
        
        # 如果已经是绝对路径，直接返回
        if url.startswith("http"):
            return url
        
        return url

