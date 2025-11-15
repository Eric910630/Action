"""
工具函数
"""
import uuid
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

