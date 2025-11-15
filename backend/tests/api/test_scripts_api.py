"""
脚本生成API端点测试
"""
import pytest
from unittest.mock import patch
import uuid
from datetime import datetime

from app.models.hotspot import Hotspot
from app.models.product import Product
from app.models.script import Script


class TestScriptsAPI:
    """脚本生成API测试"""
    
    @pytest.fixture
    def test_hotspot(self, db_session, sample_live_room_id: str):
        """创建测试热点"""
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url="https://test.com/hotspot",
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        return hotspot
    
    @pytest.fixture
    def test_product(self, db_session, sample_live_room_id: str):
        """创建测试商品"""
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            category="测试",
            live_room_id=sample_live_room_id,
            price=99.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(product)
        db_session.commit()
        return product
    
    def test_generate_script(self, client, test_hotspot: Hotspot, test_product: Product):
        """测试生成脚本"""
        with patch('app.services.script.tasks.generate_script_async.delay') as mock_task:
            mock_task.return_value.id = "test-task-id"
            
            request_data = {
                "hotspot_id": test_hotspot.id,
                "product_id": test_product.id,
                "duration": 10
            }
            
            response = client.post("/api/v1/scripts/generate", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "success"
    
    def test_generate_script_invalid_duration(self, client, test_hotspot: Hotspot, test_product: Product):
        """测试生成脚本（无效时长）"""
        request_data = {
            "hotspot_id": test_hotspot.id,
            "product_id": test_product.id,
            "duration": 20  # 超过15秒
        }
        
        response = client.post("/api/v1/scripts/generate", json=request_data)
        assert response.status_code == 400
    
    def test_get_scripts(self, client, db_session, test_product: Product):
        """测试获取脚本列表"""
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            script_content="测试脚本",
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        response = client.get("/api/v1/scripts")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    def test_get_scripts_filter_by_status(self, client, db_session, test_product: Product):
        """测试按状态筛选脚本"""
        # 创建不同状态的脚本
        script1 = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        script2 = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            status="approved",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add_all([script1, script2])
        db_session.commit()
        
        response = client.get("/api/v1/scripts?status=draft")
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "draft" for item in data["items"])
    
    def test_get_script_detail(self, client, db_session, test_product: Product):
        """测试获取脚本详情"""
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            script_content="测试脚本内容",
            shot_list=[{"shot_number": 1}],
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        response = client.get(f"/api/v1/scripts/{script.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == script.id
        assert data["script_content"] == "测试脚本内容"
    
    def test_update_script(self, client, db_session, test_product: Product):
        """测试更新脚本"""
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            script_content="旧内容",
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        # 更新脚本
        update_data = {
            "script_content": "新内容",
            "status": "reviewed"
        }
        response = client.put(f"/api/v1/scripts/{script.id}", json=update_data)
        assert response.status_code == 200
        
        # 验证更新
        detail_response = client.get(f"/api/v1/scripts/{script.id}")
        detail_data = detail_response.json()
        assert detail_data["script_content"] == "新内容"
        assert detail_data["status"] == "reviewed"
    
    def test_review_script(self, client, db_session, test_product: Product):
        """测试审核脚本"""
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        # 审核通过
        review_data = {
            "action": "approve",
            "comment": "审核通过"
        }
        response = client.post(f"/api/v1/scripts/{script.id}/review", json=review_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
    
    def test_optimize_script(self, client, db_session, test_product: Product):
        """测试获取优化建议"""
        # 创建脚本（时长过短）
        script = Script(
            id=str(uuid.uuid4()),
            product_id=test_product.id,
            video_info={"duration": 3},  # 过短
            shot_list=[],  # 缺少分镜
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        response = client.post(f"/api/v1/scripts/{script.id}/optimize")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0

