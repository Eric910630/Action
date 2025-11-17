"""
应用配置
"""
from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "Action 1.0"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ]
    
    # 数据库配置 (PostgreSQL/PolarDB)
    DB_USER: str = "beewise_tester"
    DB_PASSWORD: str = "z_13731790081"
    DB_HOST: str = "beewise-e2e-test.rwlb.rds.aliyuncs.com"
    DB_PORT: str = "5432"
    DB_NAME: str = "beewise_e2e_db"
    
    # 数据库连接URL（自动构建，可通过环境变量覆盖）
    # 注意：如果设置了DATABASE_URL环境变量，它将覆盖下面的PostgreSQL配置
    DATABASE_URL: str | None = None
    DATABASE_ECHO: bool = False
    
    @computed_field
    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        # 如果明确设置了DATABASE_URL环境变量，使用它
        # 否则使用PostgreSQL配置构建URL
        if self.DATABASE_URL and self.DATABASE_URL.startswith(('postgresql', 'postgres')):
            return self.DATABASE_URL
        # 优先使用PostgreSQL配置
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # TrendRadar配置
    TRENDRADAR_API_URL: str = ""  # MCP服务地址，如: http://localhost:3333/mcp 或 HTTP API地址
    TRENDRADAR_API_KEY: str = ""  # 如果MCP服务需要认证，填写API Key
    TRENDRADAR_USE_MCP: bool = True  # 是否使用MCP协议（默认True，如果URL包含/mcp则自动启用）
    TRENDRADAR_USE_DIRECT_CRAWLER: bool = True  # 是否优先使用直接爬虫（主要方案），默认True。如果为False或直接爬虫失败，则使用MCP服务（降级方案）
    
    # Firecrawl配置（增强功能，可选）
    FIRECRAWL_ENABLED: bool = False  # 是否启用 Firecrawl 增强功能，默认False
    FIRECRAWL_API_KEY: str = ""  # Firecrawl API Key（用于 Cloud API）
    FIRECRAWL_MCP_SERVER_URL: str = ""  # Firecrawl MCP 服务器 URL（如果通过 MCP 调用）
    
    # AI拆解工具配置
    VIDEO_ANALYZER_API_URL: str = ""  # 远程API地址（可选）
    VIDEO_ANALYZER_API_KEY: str = ""  # 远程API密钥（可选）
    VIDEO_ANALYZER_USE_LOCAL: bool = True  # 是否使用本地分析器（默认True）
    VIDEO_ANALYZER_WHISPER_MODEL: str = "base"  # Whisper模型大小 (tiny, base, small, medium, large)
    
    # 飞书配置
    FEISHU_WEBHOOK_URL: str = ""
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 热点匹配度配置
    MATCH_SCORE_THRESHOLD: float = 0.3  # 匹配度阈值（0-1），低于此值的热点将被过滤，默认30%
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

