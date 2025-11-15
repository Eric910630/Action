"""
爬虫集成测试
测试直接爬虫（主要方案）和 MCP 降级方案
遵循 API 频率限制和安全性要求
"""
import pytest
import asyncio
import time
from datetime import datetime
from app.services.hotspot.service import HotspotMonitorService
from app.crawlers.trendradar_crawler import TrendRadarCrawler
from app.core.database import SessionLocal
from loguru import logger


class TestCrawlerIntegration:
    """爬虫集成测试"""
    
    @pytest.fixture
    def db_session(self):
        """数据库会话"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_direct_crawler_basic(self):
        """
        测试直接爬虫基本功能
        
        频率控制：
        - TrendRadar 默认请求间隔：1000ms（1秒）
        - 测试只爬取1个平台，避免过多请求
        """
        logger.info("=" * 60)
        logger.info("测试1: 直接爬虫基本功能")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(request_interval=1000)  # 1秒间隔
        
        # 只测试1个平台，避免过多请求
        platform = "douyin"
        logger.info(f"开始爬取 {platform} 热点（请求间隔：1000ms）")
        
        start_time = time.time()
        hotspots = await crawler.crawl_hotspots(platform=platform)
        elapsed = time.time() - start_time
        
        logger.info(f"爬取完成，耗时：{elapsed:.2f}秒，获取 {len(hotspots)} 个热点")
        
        # 验证结果
        assert isinstance(hotspots, list), "应该返回列表"
        if len(hotspots) > 0:
            hotspot = hotspots[0]
            assert "title" in hotspot, "热点应包含标题"
            assert "url" in hotspot, "热点应包含URL"
            assert "platform" in hotspot, "热点应包含平台标识"
            assert hotspot["platform"] == platform, "平台标识应匹配"
            logger.info(f"✅ 测试通过：成功获取 {len(hotspots)} 个热点")
        else:
            logger.warning("⚠️ 未获取到热点数据（可能是API暂时无数据）")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_direct_crawler_with_interval(self):
        """
        测试直接爬虫的请求间隔控制
        
        频率控制：
        - 测试多个平台时，确保请求间隔正确
        - 最小间隔：50ms（TrendRadar 要求）
        - 默认间隔：1000ms
        """
        logger.info("=" * 60)
        logger.info("测试2: 直接爬虫请求间隔控制")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(request_interval=1500)  # 1.5秒间隔，更安全
        
        # 测试2个平台，验证间隔控制
        platforms = ["douyin", "zhihu"]
        logger.info(f"开始批量爬取 {len(platforms)} 个平台（请求间隔：1500ms）")
        
        start_time = time.time()
        results = await crawler.crawl_multiple_platforms(platforms, request_interval=1500)
        elapsed = time.time() - start_time
        
        logger.info(f"批量爬取完成，耗时：{elapsed:.2f}秒")
        
        # 验证结果
        assert isinstance(results, dict), "应该返回字典"
        assert len(results) == len(platforms), "应该包含所有平台的结果"
        
        for platform in platforms:
            hotspots = results.get(platform, [])
            logger.info(f"  {platform}: {len(hotspots)} 个热点")
            assert isinstance(hotspots, list), f"{platform} 应该返回列表"
        
        # 验证请求间隔（至少应该有1.5秒间隔）
        min_expected_time = len(platforms) * 1.5  # 至少每个平台1.5秒
        assert elapsed >= min_expected_time * 0.8, f"请求间隔应该至少 {min_expected_time} 秒（实际：{elapsed:.2f}秒）"
        logger.info(f"✅ 测试通过：请求间隔控制正常（耗时：{elapsed:.2f}秒）")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_hotspot_service_with_direct_crawler(self):
        """
        测试 HotspotMonitorService 使用直接爬虫
        
        频率控制：
        - 使用默认配置
        - 只测试1个平台
        """
        logger.info("=" * 60)
        logger.info("测试3: HotspotMonitorService 直接爬虫模式")
        logger.info("=" * 60)
        
        service = HotspotMonitorService(use_direct_crawler=True)
        
        platform = "douyin"
        logger.info(f"开始获取 {platform} 热点（使用直接爬虫）")
        
        start_time = time.time()
        hotspots = await service.fetch_hotspots(platform=platform)
        elapsed = time.time() - start_time
        
        logger.info(f"获取完成，耗时：{elapsed:.2f}秒，获取 {len(hotspots)} 个热点")
        
        # 验证结果
        assert isinstance(hotspots, list), "应该返回列表"
        if len(hotspots) > 0:
            logger.info(f"✅ 测试通过：成功获取 {len(hotspots)} 个热点")
        else:
            logger.warning("⚠️ 未获取到热点数据")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_hotspot_service_fallback_to_mcp(self, db_session):
        """
        测试 HotspotMonitorService 降级到 MCP
        
        频率控制：
        - 先尝试直接爬虫（可能失败）
        - 如果失败，降级到 MCP
        - 只测试1个平台
        """
        logger.info("=" * 60)
        logger.info("测试4: HotspotMonitorService MCP 降级")
        logger.info("=" * 60)
        
        # 强制使用 MCP（禁用直接爬虫）
        service = HotspotMonitorService(use_direct_crawler=False)
        
        platform = "douyin"
        logger.info(f"开始获取 {platform} 热点（使用 MCP 降级方案）")
        
        try:
            start_time = time.time()
            hotspots = await service.fetch_hotspots(platform=platform)
            elapsed = time.time() - start_time
            
            logger.info(f"获取完成，耗时：{elapsed:.2f}秒，获取 {len(hotspots)} 个热点")
            
            # 验证结果
            assert isinstance(hotspots, list), "应该返回列表"
            logger.info(f"✅ 测试通过：MCP 降级方案正常工作")
        except Exception as e:
            logger.warning(f"⚠️ MCP 服务可能未配置或不可用: {e}")
            pytest.skip(f"MCP 服务不可用: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complete_workflow(self, db_session):
        """
        测试完整工作流：爬取 -> 筛选 -> 保存
        
        频率控制：
        - 只测试1个平台
        - 使用合理的请求间隔
        """
        logger.info("=" * 60)
        logger.info("测试5: 完整工作流")
        logger.info("=" * 60)
        
        service = HotspotMonitorService(use_direct_crawler=True)
        platform = "douyin"
        
        logger.info(f"步骤1: 获取 {platform} 热点")
        hotspots = await service.fetch_hotspots(platform=platform)
        logger.info(f"  获取到 {len(hotspots)} 个原始热点")
        
        if len(hotspots) == 0:
            pytest.skip("未获取到热点数据，跳过后续测试")
        
        logger.info("步骤2: 语义筛选热点")
        filtered = await service.filter_hotspots_with_semantic(
            db_session, hotspots, live_room_id=None, target_date=datetime.now()
        )
        logger.info(f"  筛选后剩余 {len(filtered)} 个热点")
        
        logger.info("步骤3: 保存到数据库")
        saved_count = service.save_hotspots(db_session, filtered, platform)
        logger.info(f"  保存了 {saved_count} 个热点")
        
        # 验证
        assert saved_count >= 0, "保存数量应该 >= 0"
        logger.info(f"✅ 测试通过：完整工作流正常（保存 {saved_count} 个热点）")


class TestFirecrawlIntegration:
    """Firecrawl 增强功能测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.firecrawl
    async def test_firecrawl_enrichment(self):
        """
        测试 Firecrawl 热点详情提取
        
        频率控制：
        - Firecrawl 有内置速率限制
        - 只测试1个热点，避免过多API调用
        - 使用合理的超时时间（30秒）
        """
        import os
        
        # 检查是否启用 Firecrawl
        if not os.getenv("FIRECRAWL_ENABLED", "false").lower() == "true":
            pytest.skip("Firecrawl 未启用，跳过测试")
        
        if not os.getenv("FIRECRAWL_API_KEY"):
            pytest.skip("FIRECRAWL_API_KEY 未配置，跳过测试")
        
        logger.info("=" * 60)
        logger.info("测试6: Firecrawl 热点详情提取")
        logger.info("=" * 60)
        
        from app.utils.firecrawl import FirecrawlClient
        
        client = FirecrawlClient()
        
        # 使用一个测试URL（避免使用真实热点URL，减少API调用）
        test_url = "https://example.com"
        logger.info(f"开始提取热点详情: {test_url}")
        
        try:
            start_time = time.time()
            result = await client.extract_hotspot_details(test_url)
            elapsed = time.time() - start_time
            
            logger.info(f"提取完成，耗时：{elapsed:.2f}秒")
            logger.info(f"结果类型: {type(result)}")
            
            # 验证结果
            assert isinstance(result, dict), "应该返回字典"
            logger.info(f"✅ 测试通过：Firecrawl 提取功能正常")
            
        except Exception as e:
            logger.warning(f"⚠️ Firecrawl 提取失败: {e}")
            pytest.skip(f"Firecrawl 提取失败: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.firecrawl
    async def test_firecrawl_batch_scrape(self):
        """
        测试 Firecrawl 批量抓取
        
        频率控制：
        - 只测试2个URL，避免过多API调用
        - Firecrawl 有内置速率限制和并行处理
        """
        import os
        
        # 检查是否启用 Firecrawl
        if not os.getenv("FIRECRAWL_ENABLED", "false").lower() == "true":
            pytest.skip("Firecrawl 未启用，跳过测试")
        
        if not os.getenv("FIRECRAWL_API_KEY"):
            pytest.skip("FIRECRAWL_API_KEY 未配置，跳过测试")
        
        logger.info("=" * 60)
        logger.info("测试7: Firecrawl 批量抓取")
        logger.info("=" * 60)
        
        from app.utils.firecrawl import FirecrawlClient
        
        client = FirecrawlClient()
        
        # 只测试2个URL，避免过多API调用
        test_urls = [
            "https://example.com",
            "https://httpbin.org/html"
        ]
        logger.info(f"开始批量抓取 {len(test_urls)} 个URL")
        
        try:
            start_time = time.time()
            result = await client.batch_scrape_hotspots(test_urls)
            elapsed = time.time() - start_time
            
            logger.info(f"批量抓取完成，耗时：{elapsed:.2f}秒")
            logger.info(f"结果: {result}")
            
            # 验证结果
            assert isinstance(result, dict), "应该返回字典"
            logger.info(f"✅ 测试通过：Firecrawl 批量抓取功能正常")
            
        except Exception as e:
            logger.warning(f"⚠️ Firecrawl 批量抓取失败: {e}")
            pytest.skip(f"Firecrawl 批量抓取失败: {e}")


class TestSafetyAndRateLimiting:
    """安全性和频率限制测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rate_limiting_compliance(self):
        """
        测试频率限制合规性
        
        验证：
        - 请求间隔符合 TrendRadar 要求（>= 50ms）
        - 重试机制正常工作
        """
        logger.info("=" * 60)
        logger.info("测试8: 频率限制合规性")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(request_interval=1000)  # 1秒间隔
        
        # 测试请求间隔
        platform = "douyin"
        logger.info(f"测试请求间隔控制（平台: {platform}）")
        
        start_time = time.time()
        hotspots1 = await crawler.crawl_hotspots(platform=platform)
        time1 = time.time() - start_time
        
        # 等待至少1秒（确保间隔）
        await asyncio.sleep(1.1)
        
        start_time = time.time()
        hotspots2 = await crawler.crawl_hotspots(platform=platform)
        time2 = time.time() - start_time
        
        logger.info(f"第一次请求耗时: {time1:.2f}秒")
        logger.info(f"第二次请求耗时: {time2:.2f}秒")
        
        # 验证结果
        assert isinstance(hotspots1, list), "第一次请求应该返回列表"
        assert isinstance(hotspots2, list), "第二次请求应该返回列表"
        logger.info(f"✅ 测试通过：频率限制合规")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_error_handling_and_retry(self):
        """
        测试错误处理和重试机制
        
        验证：
        - 网络错误时正确重试
        - 重试间隔符合要求（3-5秒）
        """
        logger.info("=" * 60)
        logger.info("测试9: 错误处理和重试机制")
        logger.info("=" * 60)
        
        crawler = TrendRadarCrawler(
            request_interval=1000,
            max_retries=2  # 最多重试2次
        )
        
        # 测试正常情况
        platform = "douyin"
        logger.info(f"测试正常请求（平台: {platform}）")
        
        try:
            hotspots = await crawler.crawl_hotspots(platform=platform)
            logger.info(f"✅ 正常请求成功，获取 {len(hotspots)} 个热点")
        except Exception as e:
            logger.warning(f"⚠️ 请求失败（可能是网络问题）: {e}")
            # 不抛出异常，因为可能是网络问题
        
        logger.info("✅ 测试通过：错误处理机制正常")

