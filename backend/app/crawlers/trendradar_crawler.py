"""
TrendRadar 爬虫实现
直接集成 TrendRadar 的爬虫逻辑，通过 newsnow.busiyi.world API 获取热点数据
"""
import json
import random
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx
from loguru import logger

from app.crawlers.base import BaseCrawler
from app.core.config import settings


# 平台 ID 映射（基于 TrendRadar 的配置）
PLATFORM_IDS = {
    "douyin": "douyin",
    "zhihu": "zhihu",
    "weibo": "weibo",
    "toutiao": "toutiao",
    "baidu": "baidu",
    "bilibili": "bilibili-hot-search",
    "tieba": "tieba",
    "thepaper": "thepaper",
    "ifeng": "ifeng",
    "wallstreetcn": "wallstreetcn-hot",
    "cls": "cls-hot",
    "xiaohongshu": "xiaohongshu",  # 小红书
    "xhs": "xiaohongshu",  # 小红书（别名）
}


class TrendRadarCrawler(BaseCrawler):
    """TrendRadar 爬虫（直接调用 API）"""
    
    def __init__(
        self,
        api_base_url: str = "https://newsnow.busiyi.world/api/s",
        proxy_url: Optional[str] = None,
        request_interval: int = 1000,  # 毫秒
        max_retries: int = 2,
    ):
        """
        初始化爬虫
        
        Args:
            api_base_url: API 基础 URL
            proxy_url: 代理 URL（可选）
            request_interval: 请求间隔（毫秒）
            max_retries: 最大重试次数
        """
        self.api_base_url = api_base_url
        self.proxy_url = proxy_url
        self.request_interval = request_interval
        self.max_retries = max_retries
    
    def _get_platform_id(self, platform: str) -> str:
        """
        获取平台 ID
        
        Args:
            platform: 平台标识（如 "douyin", "zhihu"）
            
        Returns:
            平台 ID（用于 API 调用）
        """
        return PLATFORM_IDS.get(platform.lower(), platform.lower())
    
    async def _fetch_data_async(
        self,
        platform_id: str,
        max_retries: int = None,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        异步获取指定平台的热点数据
        
        Args:
            platform_id: 平台 ID
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
            
        Returns:
            (数据字典, 平台ID) 或 (None, 平台ID)
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        url = f"{self.api_base_url}?id={platform_id}&latest"
        
        # httpx 的代理配置格式
        proxies = None
        if self.proxy_url:
            # httpx 使用 http:// 和 https:// 作为 key
            proxies = {
                "http://": self.proxy_url,
                "https://": self.proxy_url,
            }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
        
        retries = 0
        while retries <= max_retries:
            try:
                # httpx.AsyncClient 的 proxies 参数
                client_kwargs = {
                    "timeout": 10.0,
                    "follow_redirects": True
                }
                if proxies:
                    client_kwargs["proxies"] = proxies
                
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    
                    data_json = response.json()
                    
                    status = data_json.get("status", "未知")
                    if status not in ["success", "cache"]:
                        raise ValueError(f"响应状态异常: {status}")
                    
                    status_info = "最新数据" if status == "success" else "缓存数据"
                    logger.debug(f"获取 {platform_id} 成功（{status_info}）")
                    return data_json, platform_id
                    
            except Exception as e:
                retries += 1
                if retries <= max_retries:
                    base_wait = random.uniform(min_retry_wait, max_retry_wait)
                    additional_wait = (retries - 1) * random.uniform(1, 2)
                    wait_time = base_wait + additional_wait
                    logger.warning(
                        f"请求 {platform_id} 失败: {e}. {wait_time:.2f}秒后重试... "
                        f"(尝试 {retries}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"请求 {platform_id} 失败（已重试 {max_retries} 次）: {e}")
                    return None, platform_id
        
        return None, platform_id
    
    async def crawl_hotspots(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        爬取热点数据
        
        Args:
            platform: 平台标识（如 "douyin", "zhihu", "weibo"）
            date: 目标日期，None 表示最新数据（目前 API 只支持最新数据）
            
        Returns:
            热点列表
        """
        platform_id = self._get_platform_id(platform)
        logger.info(f"开始爬取 {platform} (ID: {platform_id}) 的热点数据")
        
        # 调用 API 获取数据
        data, _ = await self._fetch_data_async(platform_id)
        
        if not data:
            logger.warning(f"未能获取 {platform} 的热点数据")
            return []
        
        # 解析数据
        hotspots = []
        items = data.get("items", [])
        
        for index, item in enumerate(items, 1):
            title = item.get("title", "").strip()
            if not title:
                continue
            
            # 计算热度分数（基于排名，排名越靠前分数越高）
            # 假设前 10 名是 100-91 分，11-20 名是 90-81 分，以此类推
            rank = index
            heat_score = max(0, 100 - (rank - 1))
            
            hotspot = {
                "title": title,
                "url": item.get("url", ""),
                "mobileUrl": item.get("mobileUrl", ""),
                "platform": platform,
                "rank": rank,
                "heat_score": heat_score,
                "tags": [],  # TrendRadar API 不提供标签，留空
                "timestamp": datetime.now().isoformat(),
            }
            
            hotspots.append(hotspot)
        
        logger.info(f"成功爬取 {platform} 的 {len(hotspots)} 个热点")
        return hotspots
    
    async def crawl_multiple_platforms(
        self,
        platforms: List[str],
        request_interval: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        爬取多个平台的热点数据
        
        Args:
            platforms: 平台列表
            request_interval: 请求间隔（毫秒），None 使用默认值
            
        Returns:
            字典，key 为平台标识，value 为热点列表
        """
        if request_interval is None:
            request_interval = self.request_interval
        
        results = {}
        
        for i, platform in enumerate(platforms):
            try:
                hotspots = await self.crawl_hotspots(platform)
                results[platform] = hotspots
                
                # 在请求之间添加间隔（最后一个不需要）
                if i < len(platforms) - 1:
                    # 添加随机抖动，避免被限流
                    actual_interval = request_interval + random.randint(-10, 20)
                    actual_interval = max(50, actual_interval)  # 至少 50ms
                    await asyncio.sleep(actual_interval / 1000)
                    
            except Exception as e:
                logger.error(f"爬取 {platform} 失败: {e}")
                results[platform] = []
        
        return results

