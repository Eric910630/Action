"""
AI拆解工具客户端
支持本地分析器和远程API两种模式
"""
import httpx
from loguru import logger
from app.core.config import settings
from typing import Optional, Dict, Any


class VideoAnalyzerClient:
    """AI拆解工具客户端 - 支持本地和远程两种模式"""
    
    def __init__(self, api_url: str = None, api_key: str = None, use_local: bool = None):
        """
        初始化视频分析客户端
        
        Args:
            api_url: 远程API地址（可选）
            api_key: 远程API密钥（可选）
            use_local: 是否使用本地分析器（None时从配置读取）
        """
        self.api_url = api_url or settings.VIDEO_ANALYZER_API_URL
        self.api_key = api_key or settings.VIDEO_ANALYZER_API_KEY
        
        # 决定使用本地还是远程
        if use_local is None:
            self.use_local = getattr(settings, 'VIDEO_ANALYZER_USE_LOCAL', True)
        else:
            self.use_local = use_local
        
        # 初始化本地分析器（如果需要）
        self.local_analyzer = None
        if self.use_local:
            try:
                from app.utils.video_analyzer_local import LocalVideoAnalyzer
                whisper_model = getattr(settings, 'VIDEO_ANALYZER_WHISPER_MODEL', 'base')
                self.local_analyzer = LocalVideoAnalyzer(whisper_model=whisper_model)
                logger.info("本地视频分析器初始化成功")
            except Exception as e:
                logger.warning(f"本地视频分析器初始化失败: {e}，将尝试使用远程API")
                self.use_local = False
        
        # 如果本地分析器不可用，检查远程API配置
        if not self.use_local and not self.api_url:
            logger.warning("本地分析器不可用且远程API未配置，视频分析功能将不可用")
    
    async def analyze(
        self,
        video_url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析视频
        
        Args:
            video_url: 视频URL
            options: 可选参数
        
        Returns:
            分析结果
        """
        import time
        start_time = time.time()
        
        logger.info(f"🔍 [探针] VideoAnalyzerClient.analyze 开始")
        logger.info(f"🔍 [探针] 输入参数: video_url={video_url[:100]}, use_local={self.use_local}, has_local_analyzer={self.local_analyzer is not None}, has_api_url={bool(self.api_url)}")
        
        # 优先使用本地分析器
        if self.use_local and self.local_analyzer:
            try:
                logger.info(f"🔍 [探针] 使用本地分析器分析视频: {video_url[:100]}")
                local_start = time.time()
                result = await self.local_analyzer.analyze(video_url, options)
                local_time = time.time() - local_start
                total_time = time.time() - start_time
                logger.info(f"✅ [探针] VideoAnalyzerClient.analyze 完成 (本地模式), 本地耗时 {local_time:.2f}秒, 总耗时 {total_time:.2f}秒")
                logger.debug(f"🔍 [探针] 返回结果摘要: duration={result.get('duration')}, scenes={len(result.get('shot_table', []))}, transcript_len={len(result.get('transcript', ''))}")
                return result
            except Exception as e:
                local_time = time.time() - start_time
                logger.warning(f"⚠️  [探针] 本地分析器失败, 耗时 {local_time:.2f}秒: {e}，尝试使用远程API")
                # 降级到远程API
                if self.api_url:
                    logger.info(f"🔍 [探针] 降级到远程API")
                    return await self._analyze_remote(video_url, options)
                else:
                    total_time = time.time() - start_time
                    logger.error(f"❌ [探针] VideoAnalyzerClient.analyze 失败, 总耗时 {total_time:.2f}秒: 本地分析器失败且远程API未配置")
                    raise ValueError(f"本地分析器失败且远程API未配置: {e}")
        
        # 使用远程API
        if self.api_url:
            logger.info(f"🔍 [探针] 使用远程API分析视频: {video_url[:100]}")
            return await self._analyze_remote(video_url, options)
        
        # 都没有配置
        total_time = time.time() - start_time
        logger.error(f"❌ [探针] VideoAnalyzerClient.analyze 失败, 耗时 {total_time:.2f}秒: 视频分析器未配置")
        raise ValueError("视频分析器未配置（本地分析器不可用且远程API未配置）")
    
    async def _analyze_remote(
        self,
        video_url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """调用远程API分析视频"""
        import time
        start_time = time.time()
        
        logger.debug(f"🔍 [探针] _analyze_remote 开始: {video_url[:100]}")
        
        if not self.api_url:
            logger.error("❌ [探针] 远程API URL未配置")
            raise ValueError("远程API URL未配置")
        
        try:
            logger.info(f"🔍 [探针] 使用远程API分析视频: {video_url[:100]}")
            logger.debug(f"🔍 [探针] API URL: {self.api_url}, 有API Key: {bool(self.api_key)}")
            
            request_start = time.time()
            async with httpx.AsyncClient(timeout=600.0) as client:  # 10分钟超时
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "video_url": video_url,
                    "options": options or {}
                }
                logger.debug(f"🔍 [探针] 发送请求: payload={payload}")
                
                response = await client.post(
                    f"{self.api_url}/api/v1/analyze",
                    json=payload,
                    headers=headers
                )
                request_time = time.time() - request_start
                logger.debug(f"🔍 [探针] HTTP响应: status={response.status_code}, 耗时 {request_time:.2f}秒")
                
                response.raise_for_status()
                result = response.json()
                
                total_time = time.time() - start_time
                logger.info(f"✅ [探针] _analyze_remote 完成, 总耗时 {total_time:.2f}秒")
                logger.debug(f"🔍 [探针] 返回结果摘要: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                return result
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] _analyze_remote 失败, 耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.debug(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            raise

