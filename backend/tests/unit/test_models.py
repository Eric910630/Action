"""
数据模型单元测试
"""
import pytest
import uuid
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.hotspot import Hotspot
from app.models.product import Product, LiveRoom
from app.models.script import Script
from app.models.analysis import AnalysisReport


class TestHotspotModel:
    """热点模型测试"""
    
    def test_create_hotspot(self, db_session: Session):
        """测试创建热点"""
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url="https://www.douyin.com/video/test",
            platform="douyin",
            tags=["测试", "热点"],
            heat_score=95,
            match_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(hotspot)
        db_session.commit()
        
        assert hotspot.id is not None
        assert hotspot.title == "测试热点"
        assert hotspot.platform == "douyin"
    
    def test_hotspot_unique_url(self, db_session: Session):
        """测试热点URL唯一性"""
        url = "https://www.douyin.com/video/test-unique"
        
        hotspot1 = Hotspot(
            id=str(uuid.uuid4()),
            title="热点1",
            url=url,
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot1)
        db_session.commit()
        
        # 尝试创建相同URL的热点应该失败
        hotspot2 = Hotspot(
            id=str(uuid.uuid4()),
            title="热点2",
            url=url,
            platform="douyin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot2)
        
        from sqlalchemy.exc import IntegrityError
        try:
            db_session.commit()
            pytest.fail("应该抛出IntegrityError")
        except IntegrityError:
            db_session.rollback()  # 回滚以清理状态
            assert True  # 测试通过


class TestProductModel:
    """商品模型测试"""
    
    def test_create_product(self, db_session: Session, sample_live_room_id: str):
        """测试创建商品"""
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            brand="测试品牌",
            category="测试",
            live_room_id=sample_live_room_id,
            price=99.0,
            selling_points=["卖点1", "卖点2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.name == "测试商品"
        assert product.price == 99.0
    
    def test_product_foreign_key(self, db_session: Session):
        """测试商品外键约束"""
        # 使用不存在的live_room_id应该失败（如果外键约束启用）
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            live_room_id="non-existent-id",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(product)
        
        from sqlalchemy.exc import IntegrityError
        # SQLite在启用外键约束时会检查外键
        try:
            db_session.commit()
            pytest.fail("应该抛出IntegrityError")
        except IntegrityError:
            db_session.rollback()  # 回滚以清理状态
            assert True  # 测试通过


class TestLiveRoomModel:
    """直播间模型测试"""
    
    def test_create_live_room(self, db_session: Session):
        """测试创建直播间"""
        room = LiveRoom(
            id=str(uuid.uuid4()),
            name="测试直播间",
            category="测试",
            keywords=["关键词1", "关键词2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(room)
        db_session.commit()
        
        assert room.id is not None
        assert room.name == "测试直播间"
        assert len(room.keywords) == 2


class TestScriptModel:
    """脚本模型测试"""
    
    def test_create_script(
        self, 
        db_session: Session, 
        sample_live_room_id: str
    ):
        """测试创建脚本"""
        # 先创建商品
        from app.models.product import Product
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            live_room_id=sample_live_room_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(product)
        db_session.commit()
        
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=product.id,
            script_content="测试脚本内容",
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(script)
        db_session.commit()
        
        assert script.id is not None
        assert script.status == "draft"
        assert script.product_id == product.id


class TestAnalysisReportModel:
    """拆解报告模型测试"""
    
    def test_create_analysis_report(self, db_session: Session):
        """测试创建拆解报告"""
        report = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url="https://www.douyin.com/video/test",
            video_info={"title": "测试视频"},
            basic_info={"theme": "测试主题"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(report)
        db_session.commit()
        
        assert report.id is not None
        assert report.video_url == "https://www.douyin.com/video/test"
    
    def test_analysis_report_unique_url(self, db_session: Session):
        """测试拆解报告URL唯一性"""
        url = "https://www.douyin.com/video/test-unique-report"
        
        report1 = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url=url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report1)
        db_session.commit()
        
        # 尝试创建相同URL的报告应该失败
        report2 = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url=url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report2)
        
        from sqlalchemy.exc import IntegrityError
        try:
            db_session.commit()
            pytest.fail("应该抛出IntegrityError")
        except IntegrityError:
            db_session.rollback()  # 回滚以清理状态
            assert True  # 测试通过

