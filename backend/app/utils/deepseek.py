"""
DeepSeek API客户端
"""
import httpx
from loguru import logger
from app.core.config import settings
from typing import Optional, Dict, Any


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.api_base = api_base or settings.DEEPSEEK_API_BASE
        self.model = settings.DEEPSEEK_MODEL
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """调用DeepSeek API生成内容"""
        if not self.api_key:
            logger.error("DeepSeek API Key未配置")
            raise ValueError("DeepSeek API Key未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise

