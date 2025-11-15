"""
爬虫基类
定义所有爬虫的通用接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseCrawler(ABC):
    """爬虫基类"""
    
    @abstractmethod
    async def crawl_hotspots(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        爬取热点数据
        
        Args:
            platform: 平台标识（如 "douyin", "zhihu", "weibo"）
            date: 目标日期，None 表示最新数据
            
        Returns:
            热点列表，每个热点包含：
            - title: 标题
            - url: URL
            - mobileUrl: 移动端 URL（如果有）
            - platform: 平台标识
            - rank: 排名
            - heat_score: 热度分数（如果有）
        """
        pass
    
    def normalize_hotspot(self, raw_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        标准化热点数据格式
        
        Args:
            raw_data: 原始数据
            platform: 平台标识
            
        Returns:
            标准化后的热点数据
        """
        return {
            "title": raw_data.get("title", ""),
            "url": raw_data.get("url", ""),
            "mobileUrl": raw_data.get("mobileUrl", ""),
            "platform": platform,
            "rank": raw_data.get("rank", 0),
            "heat_score": raw_data.get("heat_score", 0),
            "tags": raw_data.get("tags", []),
            "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
        }

