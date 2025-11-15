"""
Pytest配置和共享fixtures
"""
import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# 加载.env文件（如果存在）
load_dotenv()

# 设置测试环境变量
os.environ["TESTING"] = "true"

from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from app.main import app


# 测试数据库配置（使用SQLite内存数据库进行测试）
# 这样可以避免依赖外部数据库，测试更快速和独立
import os
if os.getenv("USE_TEST_DB") == "true":
    # 如果设置了USE_TEST_DB=true，使用测试数据库
    # 如果设置了USE_REAL_DB_FOR_CELERY=true，使用原始数据库（真实LLM测试需要）
    # 这样Celery任务和测试使用相同的数据库
    if os.getenv("USE_REAL_DB_FOR_CELERY") == "true":
        # 使用原始数据库，这样Celery任务可以访问测试数据
        TEST_DATABASE_URL = settings.database_url
        print(f"[测试配置] 使用真实数据库（Celery兼容模式）: {TEST_DATABASE_URL[:60]}...")
    elif "test" in settings.DB_NAME.lower():
        # 已经是测试数据库，直接使用
        TEST_DATABASE_URL = settings.database_url
        print(f"[测试配置] 使用测试数据库: {TEST_DATABASE_URL[:60]}...")
    else:
        # 尝试使用_test后缀的数据库
        TEST_DATABASE_URL = settings.database_url.replace(
            settings.DB_NAME, 
            f"{settings.DB_NAME}_test"
        )
        print(f"[测试配置] 使用_test数据库: {TEST_DATABASE_URL[:60]}...")
else:
    # 默认使用SQLite内存数据库
    TEST_DATABASE_URL = "sqlite:///:memory:"
    print("[测试配置] 使用内存数据库（SQLite）")

# 创建测试数据库引擎
# 注意：PostgreSQL不需要check_same_thread参数
connect_args = {}
if "sqlite" in TEST_DATABASE_URL:
    connect_args["check_same_thread"] = False

test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool if "sqlite" in TEST_DATABASE_URL else None,
    connect_args=connect_args,
    echo=False
)

# SQLite需要启用外键约束
if "sqlite" in TEST_DATABASE_URL:
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=test_engine)
    
    db = TestSessionLocal()
    try:
        yield db
        # 对于真实数据库测试，确保提交所有更改
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
    except Exception:
        db.rollback()
        raise
    finally:
        # 清理数据
        db.close()
        # 注意：对于真实数据库（USE_REAL_DB_FOR_CELERY=true），不删除表数据
        # 因为Celery任务可能需要访问这些数据
        if os.getenv("USE_REAL_DB_FOR_CELERY") != "true":
            # 删除所有表数据（但保留表结构）
            Base.metadata.drop_all(bind=test_engine)
            Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_live_room_data():
    """示例直播间数据"""
    return {
        "name": "测试直播间",
        "category": "测试",
        "keywords": ["测试", "关键词"],
        "ip_character": "测试IP",
        "style": "测试风格"
    }


@pytest.fixture
def sample_product_data(sample_live_room_id):
    """示例商品数据"""
    return {
        "name": "测试商品",
        "brand": "测试品牌",
        "category": "测试",
        "live_room_id": sample_live_room_id,
        "product_link": "https://example.com/product",
        "description": "测试商品描述",
        "selling_points": ["卖点1", "卖点2"],
        "price": 99.0,
        "hand_card": "测试说明手卡",
        "live_date": "2024-12-15"
    }


@pytest.fixture
def sample_live_room_id(db_session, sample_live_room_data):
    """创建测试直播间并返回ID"""
    from app.models.product import LiveRoom
    import uuid
    from datetime import datetime
    
    room = LiveRoom(
        id=str(uuid.uuid4()),
        name=sample_live_room_data["name"],
        category=sample_live_room_data["category"],
        keywords=sample_live_room_data["keywords"],
        ip_character=sample_live_room_data["ip_character"],
        style=sample_live_room_data["style"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)
    return room.id


@pytest.fixture
def sample_hotspot_data():
    """示例热点数据"""
    return {
        "title": "测试热点标题",
        "url": "https://www.douyin.com/video/test123",
        "platform": "douyin",
        "tags": ["测试", "热点"],
        "heat_score": 95,
        "match_score": 0.8
    }


@pytest.fixture
def sample_analysis_report_data():
    """示例拆解报告数据"""
    return {
        "video_url": "https://www.douyin.com/video/test123",
        "video_info": {
            "title": "测试视频",
            "duration": "10秒"
        },
        "basic_info": {
            "theme": "测试主题",
            "content_type": "测试类型"
        },
        "shot_table": [
            {
                "shot_number": 1,
                "time_range": "0-3秒",
                "dialogue": "测试台词",
                "content": "测试内容",
                "viral_technique": "快速切换"
            }
        ],
        "golden_3s": {
            "opening_line": "测试开头",
            "hook_type": "悬念钩子"
        },
        "viral_formula": {
            "formula_name": "测试公式",
            "formula_structure": "测试结构"
        }
    }


@pytest.fixture(scope="session")
def use_real_trendradar():
    """
    根据环境变量决定是否使用真实TrendRadar API
    
    注意：
    - 如果使用直接爬虫（TRENDRADAR_USE_DIRECT_CRAWLER=true，默认），不需要API Key
    - 只有在使用MCP服务（降级方案）时才需要API Key
    - 如果设置了TRENDRADAR_USE_MOCK=true，则使用Mock
    """
    from app.core.config import settings
    use_mock = os.getenv("TRENDRADAR_USE_MOCK", "false").lower() == "true"
    
    if use_mock:
        # 明确要求使用Mock
        return False
    else:
        # 检查是否使用直接爬虫（主要方案）
        use_direct_crawler = getattr(settings, 'TRENDRADAR_USE_DIRECT_CRAWLER', True)
        
        if use_direct_crawler:
            # 直接爬虫不需要API Key，可以直接使用
            return True
        else:
            # 使用MCP服务（降级方案），需要API Key
            # 优先从settings读取，如果没有则从环境变量读取
            api_key = settings.TRENDRADAR_API_KEY or os.getenv("TRENDRADAR_API_KEY")
            if not api_key:
                pytest.skip("使用MCP服务需要TRENDRADAR_API_KEY，但未配置。建议启用直接爬虫（TRENDRADAR_USE_DIRECT_CRAWLER=true）")
            return True


@pytest.fixture(scope="session")
def use_real_llm():
    """
    检查是否使用真实LLM API
    
    对于E2E测试，LLM必须使用真实API
    """
    from app.core.config import settings
    # 优先从settings读取，如果没有则从环境变量读取
    api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        pytest.skip("DEEPSEEK_API_KEY未配置，跳过真实LLM测试")
    return True


@pytest.fixture(scope="session")
def llm_config():
    """LLM配置检查"""
    from app.core.config import settings
    # 优先从settings读取，如果没有则从环境变量读取
    api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        pytest.skip("DEEPSEEK_API_KEY未配置，跳过LLM测试")
    return {
        "api_key": api_key,
        "api_base": settings.DEEPSEEK_API_BASE or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
        "model": settings.DEEPSEEK_MODEL or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    }

