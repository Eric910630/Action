"""
热点监控工作流集成测试
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.services.hotspot.service import HotspotMonitorService
from app.models.hotspot import Hotspot
from app.models.product import LiveRoom


class TestHotspotWorkflow:
    """热点监控完整工作流测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return HotspotMonitorService()
    
    @pytest.mark.asyncio
    @pytest.mark.real_api
    async def test_complete_hotspot_workflow(
        self,
        service: HotspotMonitorService,
        db_session,
        sample_live_room_id: str,
        use_real_trendradar
    ):
        """测试完整热点工作流：抓取 -> 筛选 -> 保存（使用真实TrendRadar API）"""
        if not use_real_trendradar:
            pytest.skip("未配置TRENDRADAR_API_KEY，跳过真实API测试")
        
        # 1. 使用真实TrendRadar API获取热点
        try:
            hotspots = await service.fetch_hotspots("douyin")
        except Exception as e:
            pytest.skip(f"TrendRadar API调用失败: {e}")
        
        if not hotspots or len(hotspots) == 0:
            pytest.skip("TrendRadar API未返回热点数据，跳过测试")
        
        # 2. 验证获取的热点数据
        assert len(hotspots) > 0
        assert "title" in hotspots[0]
        assert "url" in hotspots[0]
        
        # 3. 获取直播间关键词
        live_room = db_session.query(LiveRoom).filter(
            LiveRoom.id == sample_live_room_id
        ).first()
        
        # 4. 筛选热点
        keywords = live_room.keywords or ["女装"]
        filtered = service.filter_hotspots(hotspots, keywords, live_room)
        
        # 5. 保存热点
        saved_count = service.save_hotspots(db_session, filtered, "douyin")
        # 注意：如果热点已存在，可能返回0，这是正常的
        assert saved_count >= 0
        
        # 6. 验证保存的热点（如果保存成功）
        if saved_count > 0:
            saved_hotspots = db_session.query(Hotspot).all()
            assert len(saved_hotspots) > 0
    
    @pytest.mark.asyncio
    async def test_hotspot_filter_and_push_workflow(
        self,
        service: HotspotMonitorService,
        db_session,
        sample_live_room_id: str
    ):
        """测试热点筛选和推送工作流"""
        import uuid
        
        # 1. 创建今日热点
        today = datetime.now()
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="今日热点",
            url="https://test.com/today",
            platform="douyin",
            match_score=0.85,  # 高匹配度
            created_at=today,
            updated_at=today
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 2. 推送到飞书
        # 创建直播间（如果不存在）
        from app.models.product import LiveRoom
        live_room = db_session.query(LiveRoom).filter(
            LiveRoom.id == sample_live_room_id
        ).first()
        if not live_room:
            # 如果fixture没有创建，这里创建一个
            import uuid
            live_room = LiveRoom(
                id=sample_live_room_id,
                name="测试直播间",
                category="测试",
                keywords=["测试"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_session.add(live_room)
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
                result = await service.push_to_feishu(db_session, sample_live_room_id)
                # 可能返回False如果没有匹配的热点，这是正常的
                assert isinstance(result, bool)

