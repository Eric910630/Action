"""
爬虫模块
直接集成 TrendRadar 的爬虫逻辑，支持多平台热点抓取
参考 BettaFish 项目，支持小红书专用爬虫
"""
from app.crawlers.base import BaseCrawler
from app.crawlers.trendradar_crawler import TrendRadarCrawler

# 小红书爬虫（可选，需要根据实际页面结构实现）
try:
    from app.crawlers.xiaohongshu_crawler import XiaohongshuCrawler
    __all__ = ["BaseCrawler", "TrendRadarCrawler", "XiaohongshuCrawler"]
except ImportError:
    __all__ = ["BaseCrawler", "TrendRadarCrawler"]

