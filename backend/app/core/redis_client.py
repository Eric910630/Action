"""
Redis客户端配置
"""
import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    # 生产环境优化：增加连接池大小以支持更多并发
    max_connections=50,  # 连接池大小：从默认增加到50
)

