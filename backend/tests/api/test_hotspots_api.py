"""
热点监控API端点测试
"""
import pytest
from unittest.mock import patch
import uuid
from datetime import datetime

from app.models.hotspot import Hotspot
from app.models.product import LiveRoom


class TestHotspotsAPI:
    """热点监控API测试"""
    
    def test_get_hotspots_empty(self, client):
        """测试获取空热点列表"""
        response = client.get("/api/v1/hotspots")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 0
    
    def test_get_hotspots_with_data(self, client, db_session):
        """测试获取有数据的热点列表"""
        # 创建测试热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url="https://test.com/1",
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        response = client.get("/api/v1/hotspots")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    def test_get_hotspots_filter_by_platform(self, client, db_session):
        """测试按平台筛选热点"""
        # 创建不同平台的热点
        hotspot1 = Hotspot(
            id=str(uuid.uuid4()),
            title="抖音热点",
            url="https://test.com/douyin",
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        hotspot2 = Hotspot(
            id=str(uuid.uuid4()),
            title="微博热点",
            url="https://test.com/weibo",
            platform="weibo",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add_all([hotspot1, hotspot2])
        db_session.commit()
        
        response = client.get("/api/v1/hotspots?platform=douyin")
        assert response.status_code == 200
        data = response.json()
        assert all(item["platform"] == "douyin" for item in data["items"])
    
    def test_fetch_hotspots(self, client):
        """测试手动触发热点抓取"""
        with patch('app.services.hotspot.tasks.fetch_daily_hotspots.delay') as mock_task:
            mock_task.return_value.id = "test-task-id"
            
            response = client.post("/api/v1/hotspots/fetch?platform=douyin")
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["platform"] == "douyin"
    
    def test_get_hotspot_detail(self, client, db_session):
        """测试获取热点详情"""
        # 创建热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url="https://test.com/detail",
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        response = client.get(f"/api/v1/hotspots/{hotspot.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == hotspot.id
        assert data["title"] == "测试热点"
    
    def test_get_hotspot_detail_not_found(self, client):
        """测试获取不存在的热点"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/hotspots/{fake_id}")
        assert response.status_code == 404
    
    def test_filter_hotspots(self, client, db_session, sample_live_room_id: str):
        """测试关键词筛选热点"""
        # 创建热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="包含关键词的热点",
            url="https://test.com/filter",
            platform="douyin",
            tags=["测试"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        response = client.post(
            "/api/v1/hotspots/filter",
            json={
                "keywords": ["关键词"],
                "live_room_id": sample_live_room_id
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "filtered_count" in data
        assert "items" in data

