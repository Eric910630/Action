"""
系统设置API端点
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import os
from pathlib import Path


router = APIRouter()


class DeepSeekApiKeyRequest(BaseModel):
    """DeepSeek API Key配置请求"""
    api_key: str


class DeepSeekApiKeyResponse(BaseModel):
    """DeepSeek API Key配置响应"""
    configured: bool
    masked_key: Optional[str] = None  # 只显示前4位和后4位，中间用*代替


@router.get("/deepseek-api-key")
async def get_deepseek_api_key() -> DeepSeekApiKeyResponse:
    """获取DeepSeek API Key配置状态"""
    from app.core.config import settings
    
    api_key = settings.DEEPSEEK_API_KEY
    
    if not api_key:
        return DeepSeekApiKeyResponse(configured=False)
    
    # 只显示前4位和后4位
    if len(api_key) > 8:
        masked = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    else:
        masked = "*" * len(api_key)
    
    return DeepSeekApiKeyResponse(configured=True, masked_key=masked)


@router.post("/deepseek-api-key")
async def set_deepseek_api_key(request: DeepSeekApiKeyRequest) -> dict:
    """设置DeepSeek API Key"""
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API Key不能为空")
    
    api_key = request.api_key.strip()
    
    # 验证API Key格式（DeepSeek API Key通常以sk-开头）
    if not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=400,
            detail="API Key格式不正确，DeepSeek API Key应以'sk-'开头"
        )
    
    try:
        # 读取.env文件（从项目根目录）
        project_root = Path(__file__).parent.parent.parent.parent.parent
        env_file = project_root / ".env"
        env_content = ""
        
        if env_file.exists():
            env_content = env_file.read_text(encoding="utf-8")
        
        # 更新或添加DEEPSEEK_API_KEY
        lines = env_content.split("\n")
        found = False
        new_lines = []
        
        for line in lines:
            if line.strip().startswith("DEEPSEEK_API_KEY="):
                new_lines.append(f"DEEPSEEK_API_KEY={api_key}")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            # 如果不存在，添加到文件末尾
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append(f"DEEPSEEK_API_KEY={api_key}")
        
        # 写入.env文件
        env_file.write_text("\n".join(new_lines), encoding="utf-8")
        
        # 更新当前运行时的配置（通过环境变量）
        os.environ["DEEPSEEK_API_KEY"] = api_key
        
        # 重新加载配置（需要重启应用才能完全生效）
        logger.info("DeepSeek API Key已更新到.env文件")
        
        return {
            "status": "success",
            "message": "API Key已保存。部分功能可能需要重启应用才能生效。"
        }
    except Exception as e:
        logger.error(f"保存DeepSeek API Key失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"保存API Key失败: {str(e)}"
        )

