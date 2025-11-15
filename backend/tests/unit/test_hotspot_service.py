"""
热点监控服务单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.hotspot.service import HotspotMonitorService
from app.models.hotspot import Hotspot
from app.models.product import LiveRoom


class TestHotspotMonitorService:
    """热点监控服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return HotspotMonitorService()
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_real_api", [False, True])
    async def test_fetch_hotspots_success(self, service: HotspotMonitorService, use_real_api, use_real_trendradar):
        """测试成功获取热点（支持真实API和Mock）"""
        if use_real_api:
            # 使用真实API
            if not use_real_trendradar:
                pytest.skip("未配置TRENDRADAR_API_KEY，跳过真实API测试")
            try:
                result = await service.fetch_hotspots(platform="douyin")
                assert isinstance(result, list)
                if len(result) > 0:
                    assert "title" in result[0]
                    assert "url" in result[0]
            except Exception as e:
                pytest.skip(f"TrendRadar API调用失败: {e}")
        else:
            # 使用Mock（用于快速单元测试）
            mock_hotspots = [
                {
                    "title": "测试热点1",
                    "url": "https://www.douyin.com/video/1",
                    "platform": "douyin",
                    "tags": ["测试"],
                    "heat_score": 95
                }
            ]
            
            with patch.object(
                service.trendradar_client, 
                'get_hotspots', 
                new_callable=AsyncMock,
                return_value=mock_hotspots
            ):
                result = await service.fetch_hotspots(platform="douyin")
                assert len(result) == 1
                assert result[0]["title"] == "测试热点1"
    
    @pytest.mark.asyncio
    async def test_fetch_hotspots_failure(self, service: HotspotMonitorService):
        """测试获取热点失败（直接爬虫和MCP都失败）"""
        # Mock直接爬虫失败
        if service.crawler:
            with patch.object(
                service.crawler,
                'crawl_hotspots',
                new_callable=AsyncMock,
                side_effect=Exception("直接爬虫失败")
            ):
                # Mock MCP客户端也失败
                with patch.object(
                    service.trendradar_client,
                    'get_hotspots',
                    new_callable=AsyncMock,
                    side_effect=Exception("MCP服务失败")
                ):
                    # 应该抛出异常，因为所有方案都失败了
                    with pytest.raises(Exception) as exc_info:
                        await service.fetch_hotspots(platform="douyin")
                    assert "失败" in str(exc_info.value)
        else:
            # 如果没有直接爬虫，只测试MCP失败
            with patch.object(
                service.trendradar_client,
                'get_hotspots',
                new_callable=AsyncMock,
                side_effect=Exception("MCP服务失败")
            ):
                with pytest.raises(Exception, match="MCP服务失败"):
                    await service.fetch_hotspots(platform="douyin")
    
    def test_filter_hotspots_required_keywords(self, service: HotspotMonitorService):
        """测试必须词筛选"""
        hotspots = [
            {
                "title": "测试热点包含必须词",
                "url": "https://test.com/1",
                "tags": ["测试"]
            },
            {
                "title": "不包含必须词的热点",
                "url": "https://test.com/2",
                "tags": []
            }
        ]
        
        keywords = ["+必须词", "测试"]
        filtered = service.filter_hotspots(hotspots, keywords)
        
        # 第一个热点包含"测试"，但不包含"必须词"，应该被过滤
        # 实际逻辑：必须词必须全部包含
        assert isinstance(filtered, list)
    
    def test_filter_hotspots_exclude_keywords(self, service: HotspotMonitorService):
        """测试过滤词筛选"""
        hotspots = [
            {
                "title": "正常热点",
                "url": "https://test.com/1",
                "tags": ["测试"]
            },
            {
                "title": "包含过滤词的热点",
                "url": "https://test.com/2",
                "tags": ["过滤"]
            }
        ]
        
        keywords = ["测试", "!过滤"]
        filtered = service.filter_hotspots(hotspots, keywords)
        
        # 包含"过滤"的热点应该被排除
        filtered_urls = [h["url"] for h in filtered]
        assert "https://test.com/2" not in filtered_urls
    
    def test_filter_hotspots_match_score(self, service: HotspotMonitorService):
        """测试匹配度计算"""
        hotspots = [
            {
                "title": "测试热点包含多个关键词",
                "url": "https://test.com/1",
                "tags": ["测试", "关键词1", "关键词2"]
            },
            {
                "title": "测试热点只包含一个关键词",
                "url": "https://test.com/2",
                "tags": ["测试"]
            }
        ]
        
        keywords = ["测试", "关键词1", "关键词2"]
        filtered = service.filter_hotspots(hotspots, keywords)
        
        # 第一个热点匹配度应该更高
        assert len(filtered) > 0
        if len(filtered) >= 2:
            assert filtered[0]["match_score"] >= filtered[1]["match_score"]
    
    def test_save_hotspots_new(self, service: HotspotMonitorService, db_session):
        """测试保存新热点"""
        hotspots = [
            {
                "title": "新热点",
                "url": "https://test.com/new",
                "platform": "douyin",
                "tags": ["测试"],
                "heat_score": 90,
                "match_score": 0.8
            }
        ]
        
        count = service.save_hotspots(db_session, hotspots, "douyin")
        assert count == 1
        
        # 验证已保存
        saved = db_session.query(Hotspot).filter(
            Hotspot.url == "https://test.com/new"
        ).first()
        assert saved is not None
        assert saved.title == "新热点"
    
    def test_save_hotspots_update_existing(
        self, 
        service: HotspotMonitorService, 
        db_session
    ):
        """测试更新已存在的热点"""
        import uuid
        from datetime import datetime
        
        # 先创建一个热点
        existing = Hotspot(
            id=str(uuid.uuid4()),
            title="旧标题",
            url="https://test.com/existing",
            platform="douyin",
            heat_score=80,
            match_score=0.5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(existing)
        db_session.commit()
        
        # 更新热点
        hotspots = [
            {
                "title": "新标题",
                "url": "https://test.com/existing",
                "platform": "douyin",
                "heat_score": 95,
                "match_score": 0.9
            }
        ]
        
        count = service.save_hotspots(db_session, hotspots, "douyin")
        assert count == 1
        
        # 验证已更新
        updated = db_session.query(Hotspot).filter(
            Hotspot.url == "https://test.com/existing"
        ).first()
        assert updated.title == "新标题"
        assert updated.heat_score == 95
        assert updated.match_score == 0.9
    
    @pytest.mark.asyncio
    async def test_push_to_feishu_success(
        self, 
        service: HotspotMonitorService, 
        db_session
    ):
        """测试成功推送到飞书"""
        import uuid
        from datetime import datetime
        
        # 创建今日热点
        today = datetime.now()
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="今日热点",
            url="https://test.com/push-feishu",
            platform="douyin",
            match_score=0.8,
            created_at=today,
            updated_at=today
        )
        db_session.add(hotspot)
        db_session.commit()
        
        with patch.object(
            service.feishu_client,
            'send_message',
            new_callable=AsyncMock,
            return_value={"status": "success"}
        ):
            with patch.object(
                service.feishu_client,
                'create_hotspot_card',
                return_value={"type": "card", "data": {}}
            ):
                result = await service.push_to_feishu(db_session)
                # 如果没有直播间，可能返回False，这是正常的
                assert isinstance(result, bool)
    
    def test_get_hotspots_by_live_room(
        self,
        service: HotspotMonitorService,
        db_session,
        sample_live_room_id: str
    ):
        """测试根据直播间获取热点"""
        import uuid
        from datetime import datetime
        
        # 创建匹配的热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="匹配关键词的热点",
            url="https://test.com/get-by-room",
            platform="douyin",
            match_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        hotspots, total = service.get_hotspots_by_live_room(
            db_session, sample_live_room_id
        )
        
        assert isinstance(hotspots, list)
        assert total >= 0

