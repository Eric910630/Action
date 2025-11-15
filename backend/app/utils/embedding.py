"""
Embedding客户端 - 用于语义关联度计算
"""
import httpx
from typing import List, Optional
from loguru import logger
from app.core.config import settings
import numpy as np


class EmbeddingClient:
    """Embedding客户端 - 使用DeepSeek Embedding API"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.api_base = api_base or settings.DEEPSEEK_API_BASE
        self.model = "text-embedding-3-small"  # DeepSeek兼容OpenAI格式
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的向量表示
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表，如果失败返回None
        """
        if not self.api_key:
            logger.warning("DeepSeek API Key未配置，无法计算语义关联度")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 使用DeepSeek兼容OpenAI的embedding接口
                response = await client.post(
                    f"{self.api_base}/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": text
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # 提取embedding向量
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
                return None
                
        except Exception as e:
            logger.error(f"获取embedding失败: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算两个向量的余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            相似度分数（0-1）
        """
        try:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            # 计算余弦相似度
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            # 归一化到0-1范围（余弦相似度范围是-1到1）
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.error(f"计算余弦相似度失败: {e}")
            return 0.0
    
    async def calculate_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """计算两个文本的语义相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数（0-1）
        """
        vec1 = await self.get_embedding(text1)
        vec2 = await self.get_embedding(text2)
        
        if vec1 is None or vec2 is None:
            logger.warning("无法获取embedding，返回0相似度")
            return 0.0
        
        return self.cosine_similarity(vec1, vec2)

