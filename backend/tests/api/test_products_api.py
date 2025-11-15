"""
商品管理API端点测试
"""
import pytest
from datetime import date


class TestProductsAPI:
    """商品管理API测试"""
    
    def test_get_products_empty(self, client):
        """测试获取空商品列表"""
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
    
    def test_create_product(self, client, sample_live_room_id: str):
        """测试创建商品"""
        product_data = {
            "name": "测试商品",
            "brand": "测试品牌",
            "category": "测试",
            "live_room_id": sample_live_room_id,
            "price": 99.0,
            "selling_points": ["卖点1"],
            "live_date": "2024-12-15"
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "商品已创建"
    
    def test_create_product_invalid_date(self, client, sample_live_room_id: str):
        """测试创建商品（无效日期格式）"""
        product_data = {
            "name": "测试商品",
            "category": "测试",
            "live_room_id": sample_live_room_id,
            "price": 99.0,
            "live_date": "invalid-date"
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 400
    
    def test_get_product_detail(self, client, sample_live_room_id: str):
        """测试获取商品详情"""
        # 先创建商品
        product_data = {
            "name": "测试商品详情",
            "category": "测试",
            "live_room_id": sample_live_room_id,
            "price": 99.0,
            "live_date": "2024-12-15"
        }
        create_response = client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]
        
        # 获取详情
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "测试商品详情"
    
    def test_get_product_detail_not_found(self, client):
        """测试获取不存在的商品"""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/products/{fake_id}")
        assert response.status_code == 404
    
    def test_update_product(self, client, sample_live_room_id: str):
        """测试更新商品"""
        # 先创建商品
        product_data = {
            "name": "旧名称",
            "category": "测试",
            "live_room_id": sample_live_room_id,
            "price": 99.0,
            "live_date": "2024-12-15"
        }
        create_response = client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]
        
        # 更新商品
        update_data = {
            "name": "新名称",
            "price": 199.0
        }
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "商品已更新"
        
        # 验证更新
        detail_response = client.get(f"/api/v1/products/{product_id}")
        detail_data = detail_response.json()
        assert detail_data["name"] == "新名称"
        assert detail_data["price"] == 199.0

