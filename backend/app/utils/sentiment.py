"""
情感分析客户端 - 用于情感关联度计算
"""
import httpx
from typing import Dict, Optional
from loguru import logger
from app.core.config import settings


class SentimentClient:
    """情感分析客户端 - 使用DeepSeek进行情感分析"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.api_base = api_base or settings.DEEPSEEK_API_BASE
        self.model = settings.DEEPSEEK_MODEL
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """分析文本的情感倾向
        
        Args:
            text: 输入文本
            
        Returns:
            情感分析结果，包含：
            - sentiment: 情感倾向（positive/negative/neutral）
            - score: 情感强度（0-1）
        """
        if not self.api_key:
            logger.warning("DeepSeek API Key未配置，无法进行情感分析")
            return {"sentiment": "neutral", "score": 0.5}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                prompt = f"""请分析以下文本的情感倾向，返回JSON格式：
{{
    "sentiment": "positive/negative/neutral",
    "score": 0.0-1.0
}}

文本：{text}"""
                
                response = await client.post(
                    f"{self.api_base}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "你是一个情感分析专家，只返回JSON格式的结果。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 100
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 尝试解析JSON
                import json
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        "sentiment": result.get("sentiment", "neutral"),
                        "score": float(result.get("score", 0.5))
                    }
                
                # 如果解析失败，使用简单规则
                return self._simple_sentiment_analysis(text)
                
        except Exception as e:
            logger.error(f"情感分析失败: {e}，使用简单规则")
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Dict[str, float]:
        """简单的情感分析规则（fallback）"""
        positive_words = ["好", "棒", "赞", "喜欢", "推荐", "值得", "优质", "精美"]
        negative_words = ["差", "坏", "不", "拒绝", "避免", "劣质", "糟糕"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.5 + positive_count * 0.1, 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.5 - negative_count * 0.1, 0.0)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {"sentiment": sentiment, "score": score}
    
    def calculate_sentiment_similarity(
        self,
        sentiment1: Dict[str, float],
        sentiment2: Dict[str, float]
    ) -> float:
        """计算两个情感分析结果的相似度
        
        Args:
            sentiment1: 情感分析结果1
            sentiment2: 情感分析结果2
            
        Returns:
            相似度分数（0-1）
        """
        # 如果情感倾向相同，相似度较高
        if sentiment1["sentiment"] == sentiment2["sentiment"]:
            # 基于情感强度的相似度
            score_diff = abs(sentiment1["score"] - sentiment2["score"])
            similarity = 1.0 - score_diff
        else:
            # 情感倾向不同，相似度较低
            similarity = 0.3
        
        return max(0.0, min(1.0, similarity))

