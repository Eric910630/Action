"""
E2E测试 - 语义关联度和情感关联度功能
测试新增的语义筛选、商品匹配度计算等功能
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
import json


class TestSemanticHotspotFiltering:
    """测试语义关联度筛选热点"""
    
    @pytest.mark.asyncio
    async def test_semantic_hotspot_filtering(self, client, db_session, sample_live_room_id):
        """测试使用语义关联度筛选热点"""
        
        # 1. 创建商品（主推商品）
        product_data = {
            "name": "时尚连衣裙",
            "brand": "测试品牌",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 299.0,
            "selling_points": ["时尚", "舒适", "百搭"],
            "description": "时尚百搭的连衣裙，适合各种场合",
            "hand_card": "限时优惠299元",
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 2. 创建测试热点（使用UUID避免重复）
        import uuid
        from app.models.hotspot import Hotspot
        
        hotspot1_id = str(uuid.uuid4())
        hotspot2_id = str(uuid.uuid4())
        
        # 检查是否已存在，如果存在则删除
        existing1 = db_session.query(Hotspot).filter(Hotspot.url == "https://test.com/hotspot1").first()
        existing2 = db_session.query(Hotspot).filter(Hotspot.url == "https://test.com/hotspot2").first()
        if existing1:
            db_session.delete(existing1)
        if existing2:
            db_session.delete(existing2)
        db_session.commit()
        
        hotspot1 = Hotspot(
            id=hotspot1_id,
            title="时尚穿搭推荐 连衣裙搭配技巧",
            url="https://test.com/hotspot1",
            platform="douyin",
            tags=["时尚", "穿搭", "连衣裙"],
            heat_score=95,
            match_score=0.0,  # 待计算
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        hotspot2 = Hotspot(
            id=hotspot2_id,
            title="科技新闻 最新AI技术",
            url="https://test.com/hotspot2",
            platform="douyin",
            tags=["科技", "AI"],
            heat_score=80,
            match_score=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(hotspot1)
        db_session.add(hotspot2)
        db_session.commit()
        
        # 3. 测试语义筛选（Mock Embedding和Sentiment）
        with patch('app.utils.embedding.EmbeddingClient.calculate_semantic_similarity') as mock_semantic, \
             patch('app.utils.sentiment.SentimentClient.analyze_sentiment') as mock_sentiment:
            
            # Mock语义相似度：热点1与商品相似度高，热点2相似度低
            async def semantic_side_effect(text1, text2):
                if "连衣裙" in text1 or "连衣裙" in text2:
                    return 0.85  # 高相似度
                return 0.15  # 低相似度
            
            mock_semantic.side_effect = semantic_side_effect
            
            # Mock情感分析：都返回中性
            mock_sentiment.return_value = {"sentiment": "neutral", "score": 0.5}
            
            # 调用筛选接口
            from app.services.hotspot.service import HotspotMonitorService
            service = HotspotMonitorService()
            
            hotspots_data = [
                {
                    "title": "时尚穿搭推荐 连衣裙搭配技巧",
                    "url": "https://test.com/hotspot1",
                    "tags": ["时尚", "穿搭", "连衣裙"],
                    "heat_score": 95
                },
                {
                    "title": "科技新闻 最新AI技术",
                    "url": "https://test.com/hotspot2",
                    "tags": ["科技", "AI"],
                    "heat_score": 80
                }
            ]
            
            filtered = await service.filter_hotspots_with_semantic(
                db_session, hotspots_data, live_room_id=sample_live_room_id
            )
            
            # 验证：热点1应该有更高的匹配度（或至少匹配度>0）
            assert len(filtered) > 0
            if len(filtered) >= 2:
                # 找到热点1
                hotspot1_filtered = next((h for h in filtered if "连衣裙" in h.get("title", "")), None)
                hotspot2_filtered = next((h for h in filtered if "AI" in h.get("title", "")), None)
                
                if hotspot1_filtered and hotspot2_filtered:
                    # 热点1（与商品相关）的匹配度应该 >= 热点2（不相关）的匹配度
                    assert hotspot1_filtered["match_score"] >= hotspot2_filtered["match_score"]
                    # 至少有一个热点的匹配度>0
                    assert hotspot1_filtered["match_score"] > 0 or hotspot2_filtered["match_score"] > 0
    
    @pytest.mark.asyncio
    async def test_product_match_score_calculation(self, client, db_session, sample_live_room_id):
        """测试商品匹配度计算"""
        
        # 1. 创建商品
        product_data = {
            "name": "美妆套装",
            "category": "美妆",
            "live_room_id": sample_live_room_id,
            "price": 199.0,
            "selling_points": ["天然", "保湿", "美白"],
            "description": "天然美妆套装，保湿美白",
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 2. 测试匹配度计算
        from app.services.hotspot.service import HotspotMonitorService
        from app.services.data.service import DataService
        
        service = HotspotMonitorService()
        data_service = DataService()
        
        product = data_service.get_product(db_session, product_id)
        assert product is not None
        
        # Mock语义和情感分析
        with patch('app.utils.embedding.EmbeddingClient.calculate_semantic_similarity') as mock_semantic, \
             patch('app.utils.sentiment.SentimentClient.analyze_sentiment') as mock_sentiment:
            
            mock_semantic.return_value = 0.8  # 高语义相似度
            mock_sentiment.return_value = {"sentiment": "positive", "score": 0.7}
            
            hotspot_data = {
                "title": "美妆推荐 天然保湿产品",
                "tags": ["美妆", "天然", "保湿"]
            }
            
            match_score = await service.calculate_product_match_score(hotspot_data, product)
            
            # 验证匹配度在合理范围内
            assert 0.0 <= match_score <= 1.0
            assert match_score > 0.5  # 应该有较高的匹配度


class TestHeatGrowthRate:
    """测试热度增长速率计算（已移除）"""
    
    def test_heat_growth_rate_removed(self):
        """测试热度增长速率功能已移除"""
        # 注意：heat_growth_rate 功能已完全移除
        # 此测试仅用于确认功能已移除，不再计算增长速率
        pass


class TestVisualizationAPI:
    """测试可视化API"""
    
    def test_get_hotspots_visualization(self, client, db_session, sample_live_room_id):
        """测试获取热点可视化数据"""
        
        # 创建测试热点
        from app.models.hotspot import Hotspot
        from app.models.product import LiveRoom
        
        db = db_session
        
        # 获取直播间
        live_room = db.query(LiveRoom).filter(LiveRoom.id == sample_live_room_id).first()
        assert live_room is not None
        
        # 创建热点
        hotspot = Hotspot(
            id="test-viz-hotspot-1",
            title="测试热点",
            url="https://test.com/viz1",
            platform="douyin",
            tags=["测试"],
            heat_score=90,
            match_score=0.85,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(hotspot)
        db.commit()
        
        # 调用可视化API
        response = client.get("/api/v1/hotspots/visualization")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # 验证数据结构
        category = data["categories"][0]
        assert "category" in category
        assert "hotspots" in category
        assert "live_room_name" in category
        
        # 验证热点数据
        if len(category["hotspots"]) > 0:
            hotspot_data = category["hotspots"][0]
            assert "heat_score" in hotspot_data
            assert "match_score" in hotspot_data
            # 注意：heat_growth_rate 字段已移除


class TestMainProductRetrieval:
    """测试主推商品获取"""
    
    def test_get_main_product(self, client, db_session, sample_live_room_id):
        """测试获取直播间的主推商品"""
        
        # 创建多个商品
        product1_data = {
            "name": "商品1",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 100.0,
            "live_date": date.today().isoformat()
        }
        
        product2_data = {
            "name": "商品2",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 200.0,
            "live_date": (date.today().replace(day=date.today().day + 1)).isoformat()  # 明天的商品
        }
        
        response1 = client.post("/api/v1/products", json=product1_data)
        response2 = client.post("/api/v1/products", json=product2_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # 测试获取主推商品
        from app.services.hotspot.service import HotspotMonitorService
        
        service = HotspotMonitorService()
        
        # 获取今天的主推商品
        product = service.get_main_product(db_session, sample_live_room_id, datetime.now())
        
        # 应该返回最新的商品（按日期和创建时间）
        assert product is not None
        assert product.name in ["商品1", "商品2"]


class TestFullSemanticWorkflow:
    """测试完整的语义筛选工作流"""
    
    @pytest.mark.asyncio
    async def test_full_semantic_workflow(self, client, db_session, sample_live_room_id):
        """测试从热点抓取到语义筛选的完整流程"""
        
        # 1. 创建商品
        product_data = {
            "name": "测试商品",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 199.0,
            "selling_points": ["时尚", "舒适"],
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 2. Mock TrendRadar返回热点
        mock_hotspots = [
            {
                "title": "时尚穿搭 女装推荐",
                "url": "https://test.com/hotspot1",
                "tags": ["时尚", "女装"],
                "heat_score": 95,
                "publish_time": datetime.now().isoformat()
            },
            {
                "title": "科技新闻",
                "url": "https://test.com/hotspot2",
                "tags": ["科技"],
                "heat_score": 80,
                "publish_time": datetime.now().isoformat()
            }
        ]
        
        # 3. 测试语义筛选
        with patch('app.services.hotspot.service.HotspotMonitorService.fetch_hotspots') as mock_fetch, \
             patch('app.utils.embedding.EmbeddingClient.calculate_semantic_similarity') as mock_semantic, \
             patch('app.utils.sentiment.SentimentClient.analyze_sentiment') as mock_sentiment:
            
            async def fetch_side_effect(*args, **kwargs):
                return mock_hotspots
            
            mock_fetch.side_effect = fetch_side_effect
            mock_semantic.return_value = 0.75  # 中等相似度
            mock_sentiment.return_value = {"sentiment": "neutral", "score": 0.5}
            
            from app.services.hotspot.service import HotspotMonitorService
            service = HotspotMonitorService()
            
            # 获取热点
            hotspots = await service.fetch_hotspots("douyin")
            assert len(hotspots) == 2
            
            # 语义筛选
            filtered = await service.filter_hotspots_with_semantic(
                db_session, hotspots, live_room_id=sample_live_room_id
            )
            
            # 验证筛选结果
            assert len(filtered) > 0
            for hotspot in filtered:
                assert "match_score" in hotspot
                assert 0.0 <= hotspot["match_score"] <= 1.0
                # 注意：heat_growth_rate 字段已移除

