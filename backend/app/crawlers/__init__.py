"""
爬虫模块
直接集成 TrendRadar 的爬虫逻辑，支持多平台热点抓取
"""
from app.crawlers.base import BaseCrawler
from app.crawlers.trendradar_crawler import TrendRadarCrawler

__all__ = ["BaseCrawler", "TrendRadarCrawler"]

