"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.database_url,  # 使用computed_field
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
    # 生产环境优化：增加连接池大小以支持更多并发用户
    pool_size=20,        # 连接池大小：从默认5增加到20
    max_overflow=30,     # 最大溢出连接数：从默认10增加到30
    pool_timeout=30,     # 获取连接超时时间：30秒
    # 添加连接超时设置，避免长时间等待
    connect_args={
        "connect_timeout": 2,  # 2秒连接超时（本地开发时快速失败）
    } if "postgresql" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

