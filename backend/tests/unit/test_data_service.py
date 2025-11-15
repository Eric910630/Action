"""
数据管理服务单元测试
"""
import pytest
from datetime import date

from app.services.data.service import DataService
from app.models.product import Product, LiveRoom


class TestDataService:
    """数据管理服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return DataService()
    
    # ========== 商品管理测试 ==========
    
    def test_create_product(self, service: DataService, db_session, sample_live_room_id: str):
        """测试创建商品"""
        product_data = {
            "name": "测试商品",
            "brand": "测试品牌",
            "category": "测试",
            "live_room_id": sample_live_room_id,
            "price": 99.0,
            "selling_points": ["卖点1", "卖点2"]
        }
        
        product = service.create_product(db_session, product_data)
        
        assert product.id is not None
        assert product.name == "测试商品"
        assert product.price == 99.0
    
    def test_get_product(self, service: DataService, db_session, sample_live_room_id: str):
        """测试获取商品"""
        # 先创建商品
        product_data = {
            "name": "测试商品",
            "live_room_id": sample_live_room_id,
            "price": 99.0
        }
        product = service.create_product(db_session, product_data)
        
        # 获取商品
        retrieved = service.get_product(db_session, product.id)
        
        assert retrieved is not None
        assert retrieved.id == product.id
        assert retrieved.name == "测试商品"
    
    def test_get_products(self, service: DataService, db_session, sample_live_room_id: str):
        """测试获取商品列表"""
        # 创建多个商品
        for i in range(3):
            product_data = {
                "name": f"商品{i}",
                "live_room_id": sample_live_room_id,
                "price": 99.0 + i
            }
            service.create_product(db_session, product_data)
        
        products, total = service.get_products(db_session)
        
        assert total >= 3
        assert len(products) >= 3
    
    def test_get_products_filter_by_live_room(
        self, 
        service: DataService, 
        db_session, 
        sample_live_room_id: str
    ):
        """测试按直播间筛选商品"""
        # 创建商品
        product_data = {
            "name": "测试商品",
            "live_room_id": sample_live_room_id,
            "price": 99.0
        }
        service.create_product(db_session, product_data)
        
        products, total = service.get_products(
            db_session, 
            live_room_id=sample_live_room_id
        )
        
        assert total >= 1
        assert all(p.live_room_id == sample_live_room_id for p in products)
    
    def test_update_product(self, service: DataService, db_session, sample_live_room_id: str):
        """测试更新商品"""
        # 先创建商品
        product_data = {
            "name": "旧名称",
            "live_room_id": sample_live_room_id,
            "price": 99.0
        }
        product = service.create_product(db_session, product_data)
        
        # 更新商品
        update_data = {
            "name": "新名称",
            "price": 199.0
        }
        updated = service.update_product(db_session, product.id, update_data)
        
        assert updated is not None
        assert updated.name == "新名称"
        assert updated.price == 199.0
    
    def test_delete_product(self, service: DataService, db_session, sample_live_room_id: str):
        """测试删除商品"""
        # 先创建商品
        product_data = {
            "name": "待删除商品",
            "live_room_id": sample_live_room_id,
            "price": 99.0
        }
        product = service.create_product(db_session, product_data)
        product_id = product.id
        
        # 删除商品
        result = service.delete_product(db_session, product_id)
        assert result is True
        
        # 验证已删除
        deleted = service.get_product(db_session, product_id)
        assert deleted is None
    
    # ========== 直播间管理测试 ==========
    
    def test_create_live_room(self, service: DataService, db_session):
        """测试创建直播间"""
        room_data = {
            "name": "测试直播间",
            "category": "测试",
            "keywords": ["关键词1", "关键词2"]
        }
        
        room = service.create_live_room(db_session, room_data)
        
        assert room.id is not None
        assert room.name == "测试直播间"
        assert len(room.keywords) == 2
    
    def test_get_live_room(self, service: DataService, db_session):
        """测试获取直播间"""
        # 先创建直播间
        room_data = {
            "name": "测试直播间",
            "category": "测试"
        }
        room = service.create_live_room(db_session, room_data)
        
        # 获取直播间
        retrieved = service.get_live_room(db_session, room.id)
        
        assert retrieved is not None
        assert retrieved.id == room.id
    
    def test_get_live_rooms(self, service: DataService, db_session):
        """测试获取直播间列表"""
        # 创建多个直播间
        for i in range(3):
            room_data = {
                "name": f"直播间{i}",
                "category": "测试"
            }
            service.create_live_room(db_session, room_data)
        
        rooms = service.get_live_rooms(db_session)
        
        assert len(rooms) >= 3
    
    def test_get_live_rooms_filter_by_category(self, service: DataService, db_session):
        """测试按类别筛选直播间"""
        # 创建不同类别的直播间
        room_data1 = {"name": "测试1", "category": "类别1"}
        room_data2 = {"name": "测试2", "category": "类别2"}
        service.create_live_room(db_session, room_data1)
        service.create_live_room(db_session, room_data2)
        
        rooms = service.get_live_rooms(db_session, category="类别1")
        
        assert all(r.category == "类别1" for r in rooms)
    
    def test_update_live_room(self, service: DataService, db_session):
        """测试更新直播间"""
        # 先创建直播间
        room_data = {
            "name": "旧名称",
            "category": "测试"
        }
        room = service.create_live_room(db_session, room_data)
        
        # 更新直播间
        update_data = {
            "name": "新名称",
            "keywords": ["新关键词"]
        }
        updated = service.update_live_room(db_session, room.id, update_data)
        
        assert updated is not None
        assert updated.name == "新名称"
        assert len(updated.keywords) == 1
    
    def test_delete_live_room(self, service: DataService, db_session):
        """测试删除直播间"""
        # 先创建直播间
        room_data = {
            "name": "待删除直播间",
            "category": "测试"
        }
        room = service.create_live_room(db_session, room_data)
        room_id = room.id
        
        # 删除直播间
        result = service.delete_live_room(db_session, room_id)
        assert result is True
        
        # 验证已删除
        deleted = service.get_live_room(db_session, room_id)
        assert deleted is None

