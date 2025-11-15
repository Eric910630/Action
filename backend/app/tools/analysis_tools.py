"""
分析工具
供Agents使用的分析相关工具函数
"""
from typing import Dict, Any
from loguru import logger


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    计算语义相似度
    
    Args:
        text1: 文本1
        text2: 文本2
    
    Returns:
        相似度分数 (0-1)
    """
    from app.utils.embedding import EmbeddingClient
    client = EmbeddingClient()
    
    try:
        # 注意：这里需要异步调用，但在工具中同步包装
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，使用线程池
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    client.calculate_semantic_similarity(text1, text2)
                )
                return future.result()
        else:
            return loop.run_until_complete(
                client.calculate_semantic_similarity(text1, text2)
            )
    except Exception as e:
        logger.error(f"计算语义相似度失败: {e}")
        return 0.0


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    分析情感倾向
    
    Args:
        text: 待分析文本
    
    Returns:
        情感分析结果字典
    """
    from app.utils.sentiment import SentimentClient
    client = SentimentClient()
    
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    client.analyze_sentiment(text)
                )
                return future.result()
        else:
            return loop.run_until_complete(client.analyze_sentiment(text))
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        return {"sentiment": "neutral", "score": 0.5}

