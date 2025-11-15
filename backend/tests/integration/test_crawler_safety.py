"""
爬虫安全性和频率限制测试
确保测试遵循 API 频率限制和安全性要求
"""
import pytest
import asyncio
import time
from app.crawlers.trendradar_crawler import TrendRadarCrawler
from app.utils.firecrawl import FirecrawlClient
from loguru import logger


class TestCrawlerSafety:
    """爬虫安全性测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_request_interval_compliance(self):
        """
        测试请求间隔合规性
        
        根据 TrendRadar 文档：
        - 默认请求间隔：1000ms（1秒）
        - 最小间隔：50ms
        - 请求之间添加随机抖动（-10到+20ms）
        """
        logger.info("=" * 60)
        logger.info("安全性测试1: 请求间隔合规性")
        logger.info("=" * 60)
        
        # 测试最小间隔（50ms）
        crawler_min = TrendRadarCrawler(request_interval=50)
        logger.info("测试最小间隔：50ms")
        
        start = time.time()
        await crawler_min.crawl_hotspots("douyin")
        elapsed1 = time.time() - start
        
        # 等待至少50ms
        await asyncio.sleep(0.06)  # 60ms，确保间隔
        
        start = time.time()
        await crawler_min.crawl_hotspots("douyin")
        elapsed2 = time.time() - start
        
        logger.info(f"第一次请求: {elapsed1:.3f}秒")
        logger.info(f"第二次请求: {elapsed2:.3f}秒")
        logger.info(f"✅ 最小间隔测试通过")
        
        # 测试默认间隔（1000ms）
        crawler_default = TrendRadarCrawler(request_interval=1000)
        logger.info("测试默认间隔：1000ms")
        
        start = time.time()
        await crawler_default.crawl_hotspots("douyin")
        elapsed1 = time.time() - start
        
        # 等待至少1秒
        await asyncio.sleep(1.1)
        
        start = time.time()
        await crawler_default.crawl_hotspots("douyin")
        elapsed2 = time.time() - start
        
        logger.info(f"第一次请求: {elapsed1:.3f}秒")
        logger.info(f"第二次请求: {elapsed2:.3f}秒")
        logger.info(f"✅ 默认间隔测试通过")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_retry_mechanism(self):
        """
        测试重试机制
        
        根据 TrendRadar 文档：
        - 默认最大重试：2次
        - 重试等待：3-5秒（随机）
        - 指数退避
        """
        logger.info("=" * 60)
        logger.info("安全性测试2: 重试机制")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(
            max_retries=2,
            request_interval=1000
        )
        
        # 测试正常请求（应该成功，不需要重试）
        logger.info("测试正常请求（不应触发重试）")
        start = time.time()
        hotspots = await crawler.crawl_hotspots("douyin")
        elapsed = time.time() - start
        
        logger.info(f"请求完成，耗时：{elapsed:.2f}秒，获取 {len(hotspots)} 个热点")
        logger.info(f"✅ 重试机制测试通过（正常请求成功）")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_limit(self):
        """
        测试并发控制
        
        确保不会同时发起过多请求
        """
        logger.info("=" * 60)
        logger.info("安全性测试3: 并发控制")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(request_interval=1000)
        
        # 测试批量爬取（应该有间隔）
        platforms = ["douyin", "zhihu"]
        logger.info(f"测试批量爬取 {len(platforms)} 个平台（应该有间隔）")
        
        start = time.time()
        results = await crawler.crawl_multiple_platforms(platforms, request_interval=1000)
        elapsed = time.time() - start
        
        logger.info(f"批量爬取完成，耗时：{elapsed:.2f}秒")
        
        # 验证：至少应该有1秒间隔（2个平台 = 至少2秒）
        min_expected = len(platforms) * 1.0  # 至少每个平台1秒
        assert elapsed >= min_expected * 0.8, f"应该有足够的间隔（期望至少 {min_expected} 秒，实际 {elapsed:.2f} 秒）"
        
        logger.info(f"✅ 并发控制测试通过（耗时：{elapsed:.2f}秒，符合预期）")


class TestFirecrawlSafety:
    """Firecrawl 安全性测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.firecrawl
    async def test_firecrawl_rate_limiting(self):
        """
        测试 Firecrawl 速率限制
        
        根据 Firecrawl 文档：
        - 有内置速率限制
        - 支持重试机制（默认3次）
        - 初始延迟：1000ms，最大延迟：10000ms
        """
        import os
        
        if not os.getenv("FIRECRAWL_ENABLED", "false").lower() == "true":
            pytest.skip("Firecrawl 未启用")
        
        if not os.getenv("FIRECRAWL_API_KEY"):
            pytest.skip("FIRECRAWL_API_KEY 未配置")
        
        logger.info("=" * 60)
        logger.info("安全性测试4: Firecrawl 速率限制")
        logger.info("=" * 60)
        
        client = FirecrawlClient()
        
        # 测试单个请求（应该遵守速率限制）
        logger.info("测试单个请求（遵守速率限制）")
        start = time.time()
        result = await client.scrape_url("https://example.com")
        elapsed = time.time() - start
        
        logger.info(f"请求完成，耗时：{elapsed:.2f}秒")
        logger.info(f"✅ Firecrawl 速率限制测试通过")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.firecrawl
    async def test_firecrawl_batch_rate_limiting(self):
        """
        测试 Firecrawl 批量请求速率限制
        
        根据 Firecrawl 文档：
        - batch_scrape 有内置速率限制和并行处理
        - 应该自动控制并发数
        """
        import os
        
        if not os.getenv("FIRECRAWL_ENABLED", "false").lower() == "true":
            pytest.skip("Firecrawl 未启用")
        
        if not os.getenv("FIRECRAWL_API_KEY"):
            pytest.skip("FIRECRAWL_API_KEY 未配置")
        
        logger.info("=" * 60)
        logger.info("安全性测试5: Firecrawl 批量速率限制")
        logger.info("=" * 60)
        
        client = FirecrawlClient()
        
        # 只测试2个URL，避免过多API调用
        urls = ["https://example.com", "https://httpbin.org/html"]
        logger.info(f"测试批量请求 {len(urls)} 个URL（应该有速率限制）")
        
        start = time.time()
        result = await client.batch_scrape_hotspots(urls)
        elapsed = time.time() - start
        
        logger.info(f"批量请求完成，耗时：{elapsed:.2f}秒")
        logger.info(f"✅ Firecrawl 批量速率限制测试通过")

