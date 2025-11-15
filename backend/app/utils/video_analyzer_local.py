"""
本地视频分析工具
基于 PySceneDetect + Whisper + MoviePy 实现
"""
import os
import tempfile
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
import httpx

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper未安装，语音转录功能将不可用")

try:
    from scenedetect import detect, ContentDetector, AdaptiveDetector
    from scenedetect.frame_timecode import FrameTimecode
    SCENEDETECT_AVAILABLE = True
except ImportError:
    SCENEDETECT_AVAILABLE = False
    logger.warning("PySceneDetect未安装，场景检测功能将不可用")

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    MOVIEPY_AVAILABLE = False
    # 延迟警告，避免模块加载时重复警告
    pass

from app.core.config import settings


class LocalVideoAnalyzer:
    """本地视频分析器 - 使用开源工具进行视频分析"""
    
    def __init__(self, whisper_model: str = "base"):
        """
        初始化本地视频分析器
        
        Args:
            whisper_model: Whisper模型大小 (tiny, base, small, medium, large)
        """
        self.whisper_model_name = whisper_model or getattr(settings, 'VIDEO_ANALYZER_WHISPER_MODEL', 'base')
        self.whisper_model = None
        self.temp_dir = None
        
        # 检查依赖（只在初始化时警告一次）
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper未安装，语音转录功能将不可用。请运行: pip install openai-whisper")
        if not SCENEDETECT_AVAILABLE:
            logger.warning("PySceneDetect未安装，场景检测功能将不可用。请运行: pip install 'scenedetect[opencv]'")
        if not MOVIEPY_AVAILABLE:
            logger.warning("MoviePy未安装，视频处理功能将不可用。请运行: pip install moviepy")
    
    def _load_whisper_model(self):
        """延迟加载Whisper模型（避免启动时加载）"""
        if not WHISPER_AVAILABLE:
            return None
        
        if self.whisper_model is None:
            try:
                logger.info(f"加载Whisper模型: {self.whisper_model_name}")
                self.whisper_model = whisper.load_model(self.whisper_model_name)
                logger.info("Whisper模型加载完成")
            except Exception as e:
                logger.error(f"加载Whisper模型失败: {e}")
                return None
        
        return self.whisper_model
    
    async def _download_video(self, video_url: str) -> Optional[str]:
        """
        下载视频到临时文件
        
        Args:
            video_url: 视频URL
            
        Returns:
            临时文件路径，失败返回None
        """
        import time
        start_time = time.time()
        
        logger.debug(f"🔍 [探针] _download_video 开始: {video_url[:100]}")
        
        # 检查httpx是否可用
        try:
            import httpx
        except (ImportError, ModuleNotFoundError):
            logger.error("❌ [探针] httpx未安装，无法下载视频。请运行: pip install httpx")
            return None
        
        try:
            # 创建临时目录
            if self.temp_dir is None:
                self.temp_dir = tempfile.mkdtemp(prefix="video_analyzer_")
                logger.debug(f"🔍 [探针] 创建临时目录: {self.temp_dir}")
            
            # 从URL提取文件名
            filename = os.path.basename(video_url.split('?')[0])
            if not filename or '.' not in filename:
                filename = "video.mp4"
            
            temp_path = os.path.join(self.temp_dir, filename)
            logger.debug(f"🔍 [探针] 目标文件路径: {temp_path}")
            
            # 下载视频
            logger.info(f"🔍 [探针] 开始HTTP下载: {video_url[:100]}")
            import httpx
            download_start = time.time()
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                content_size = len(response.content)
                logger.debug(f"🔍 [探针] HTTP响应: status={response.status_code}, size={content_size} bytes, 耗时 {time.time() - download_start:.2f}秒")
                
                write_start = time.time()
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"🔍 [探针] 文件写入完成, 耗时 {time.time() - write_start:.2f}秒")
            
            file_size = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0
            total_time = time.time() - start_time
            logger.info(f"✅ [探针] _download_video 完成: {temp_path}, 文件大小={file_size} bytes, 总耗时 {total_time:.2f}秒")
            return temp_path
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] _download_video 失败, 耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.debug(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            return None
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        获取视频基本信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        if not MOVIEPY_AVAILABLE:
            return {"duration": 0.0, "fps": 0.0, "size": (0, 0)}
        
        try:
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "width": clip.w,
                "height": clip.h
            }
            clip.close()
            return info
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {"duration": 0.0, "fps": 0.0, "size": (0, 0)}
    
    def _detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """
        检测视频场景
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            场景列表，每个场景包含 start_time, end_time
        """
        import time
        start_time = time.time()
        
        logger.debug(f"🔍 [探针] _detect_scenes 开始: {video_path}")
        
        if not SCENEDETECT_AVAILABLE:
            logger.warning("❌ [探针] PySceneDetect未安装，场景检测不可用")
            return []
        
        try:
            logger.info("🔍 [探针] 开始场景检测...")
            # 使用AdaptiveDetector，更准确
            detect_start = time.time()
            scene_list = detect(video_path, AdaptiveDetector())
            detect_time = time.time() - detect_start
            logger.debug(f"🔍 [探针] PySceneDetect检测完成, 耗时 {detect_time:.2f}秒, 原始场景数={len(scene_list)}")
            
            shot_table = []
            for i, (start, end) in enumerate(scene_list, 1):
                shot_table.append({
                    "shot_number": i,
                    "start_time": start.get_seconds(),
                    "end_time": end.get_seconds(),
                    "duration": (end - start).get_seconds(),
                    "start_frame": start.get_frames(),
                    "end_frame": end.get_frames(),
                    "description": ""  # 可以用LLM生成
                })
            
            total_time = time.time() - start_time
            logger.info(f"✅ [探针] _detect_scenes 完成, 耗时 {total_time:.2f}秒, 场景数={len(shot_table)}")
            if shot_table:
                logger.debug(f"🔍 [探针] 场景示例: {shot_table[0] if len(shot_table) > 0 else 'N/A'}")
            return shot_table
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] _detect_scenes 失败, 耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.debug(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            return []
    
    async def _transcribe_audio(self, video_path: str) -> Dict[str, Any]:
        """
        转录音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            转录结果，包含 text 和 segments
        """
        import time
        start_time = time.time()
        
        logger.debug(f"🔍 [探针] _transcribe_audio 开始: {video_path}")
        
        model = self._load_whisper_model()
        if model is None:
            logger.warning("❌ [探针] Whisper模型未加载，语音转录不可用")
            return {"text": "", "segments": []}
        
        try:
            logger.info("🔍 [探针] 开始语音转录...")
            logger.debug(f"🔍 [探针] 使用Whisper模型: {self.whisper_model_name}")
            
            # 在后台线程中运行（Whisper是同步的）
            loop = asyncio.get_event_loop()
            transcribe_start = time.time()
            result = await loop.run_in_executor(
                None,
                lambda: model.transcribe(video_path, language="zh")
            )
            transcribe_time = time.time() - transcribe_start
            logger.debug(f"🔍 [探针] Whisper转录完成, 耗时 {transcribe_time:.2f}秒")
            
            transcript = result.get("text", "")
            segments = result.get("segments", [])
            language = result.get("language", "zh")
            
            total_time = time.time() - start_time
            logger.info(f"✅ [探针] _transcribe_audio 完成, 耗时 {total_time:.2f}秒, 文本长度={len(transcript)}, 分段数={len(segments)}, 语言={language}")
            if transcript:
                logger.debug(f"🔍 [探针] 转录文本预览: {transcript[:200]}...")
            
            return {
                "text": transcript,
                "segments": segments,
                "language": language
            }
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] _transcribe_audio 失败, 耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.debug(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            return {"text": "", "segments": []}
    
    def _extract_key_frames(self, video_path: str, shot_table: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        提取关键帧（每个场景的中间帧）
        
        Args:
            video_path: 视频文件路径
            shot_table: 场景列表
            
        Returns:
            关键帧列表
        """
        if not MOVIEPY_AVAILABLE:
            return []
        
        try:
            clip = VideoFileClip(video_path)
            key_frames = []
            
            for shot in shot_table:
                # 取场景中间时刻的帧
                mid_time = (shot["start_time"] + shot["end_time"]) / 2
                frame = clip.get_frame(mid_time)
                
                key_frames.append({
                    "shot_number": shot["shot_number"],
                    "time": mid_time,
                    "frame": frame.tolist() if hasattr(frame, 'tolist') else None
                })
            
            clip.close()
            return key_frames
            
        except Exception as e:
            logger.error(f"提取关键帧失败: {e}")
            return []
    
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
                - download_video: 是否需要下载视频（默认True）
                - extract_key_frames: 是否提取关键帧（默认False，因为数据量大）
                - whisper_model: Whisper模型大小（覆盖初始化时的设置）
        
        Returns:
            分析结果，格式与远程API一致
        """
        import time
        start_time = time.time()
        
        options = options or {}
        download_video = options.get("download_video", True)
        extract_key_frames = options.get("extract_key_frames", False)
        
        logger.info(f"🔍 [探针] LocalVideoAnalyzer.analyze 开始")
        logger.info(f"🔍 [探针] 输入参数: video_url={video_url[:100]}, download_video={download_video}, extract_key_frames={extract_key_frames}")
        
        # 如果指定了whisper模型，更新
        if "whisper_model" in options:
            logger.info(f"🔍 [探针] 更新Whisper模型: {options['whisper_model']}")
            self.whisper_model_name = options["whisper_model"]
            self.whisper_model = None  # 重置，下次使用时重新加载
        
        video_path = None
        try:
            # 1. 下载视频（如果需要）
            step_start = time.time()
            if download_video:
                logger.info(f"🔍 [探针] 步骤1: 开始下载视频")
                video_path = await self._download_video(video_url)
                if not video_path:
                    raise ValueError("视频下载失败")
                logger.info(f"🔍 [探针] 步骤1完成: 视频下载成功, 耗时 {time.time() - step_start:.2f}秒, 路径={video_path}")
            else:
                # 假设video_url是本地路径
                logger.info(f"🔍 [探针] 步骤1: 使用本地视频路径")
                video_path = video_url
                if not os.path.exists(video_path):
                    raise ValueError(f"视频文件不存在: {video_path}")
                logger.info(f"🔍 [探针] 步骤1完成: 本地路径验证成功, 耗时 {time.time() - step_start:.2f}秒")
            
            # 2. 获取视频基本信息
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤2: 开始获取视频基本信息")
            video_info = self._get_video_info(video_path)
            logger.info(f"🔍 [探针] 步骤2完成: 视频信息获取成功, 耗时 {time.time() - step_start:.2f}秒")
            logger.debug(f"🔍 [探针] 视频信息: duration={video_info.get('duration')}, fps={video_info.get('fps')}, size={video_info.get('size')}")
            
            # 3. 场景检测
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤3: 开始场景检测")
            shot_table = self._detect_scenes(video_path)
            logger.info(f"🔍 [探针] 步骤3完成: 场景检测成功, 耗时 {time.time() - step_start:.2f}秒, 场景数={len(shot_table)}")
            if shot_table:
                logger.debug(f"🔍 [探针] 前3个场景: {shot_table[:3]}")
            
            # 4. 语音转录
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤4: 开始语音转录")
            transcript_result = await self._transcribe_audio(video_path)
            transcript_text = transcript_result.get("text", "")
            logger.info(f"🔍 [探针] 步骤4完成: 语音转录成功, 耗时 {time.time() - step_start:.2f}秒, 文本长度={len(transcript_text)}")
            if transcript_text:
                logger.debug(f"🔍 [探针] 转录文本预览: {transcript_text[:200]}...")
            
            # 5. 提取关键帧（可选，数据量大）
            key_frames = []
            if extract_key_frames:
                step_start = time.time()
                logger.info(f"🔍 [探针] 步骤5: 开始提取关键帧")
                key_frames = self._extract_key_frames(video_path, shot_table)
                logger.info(f"🔍 [探针] 步骤5完成: 关键帧提取成功, 耗时 {time.time() - step_start:.2f}秒, 关键帧数={len(key_frames)}")
            else:
                logger.info(f"🔍 [探针] 步骤5: 跳过关键帧提取（extract_key_frames=False）")
            
            # 6. 构建返回结果（与远程API格式一致）
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤6: 构建返回结果")
            result = {
                "duration": video_info.get("duration", 0.0),
                "fps": video_info.get("fps", 0.0),
                "size": video_info.get("size", (0, 0)),
                "shot_table": shot_table,
                "transcript": transcript_text,
                "script_content": transcript_text,  # 兼容字段
                "segments": transcript_result.get("segments", []),
                "language": transcript_result.get("language", "zh"),
                "key_frames": key_frames if extract_key_frames else [],
                "video_info": video_info
            }
            total_time = time.time() - start_time
            logger.info(f"🔍 [探针] 步骤6完成: 结果构建成功, 耗时 {time.time() - step_start:.4f}秒")
            logger.info(f"✅ [探针] LocalVideoAnalyzer.analyze 完成, 总耗时 {total_time:.2f}秒")
            logger.debug(f"🔍 [探针] 返回结果摘要: duration={result.get('duration')}, scenes={len(result.get('shot_table', []))}, transcript_len={len(transcript_text)}")
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] LocalVideoAnalyzer.analyze 失败, 总耗时 {total_time:.2f}秒")
            logger.error(f"❌ [探针] 错误详情: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            raise
        finally:
            # 清理临时文件
            # 注意：视频文件存储在本地临时目录（tempfile.mkdtemp），不在数据库中
            # 临时目录路径：self.temp_dir（例如：/tmp/video_analyzer_xxxxx）
            # 分析完成后自动删除临时视频文件，节省磁盘空间
            if download_video and video_path and os.path.exists(video_path):
                try:
                    logger.debug(f"🔍 [探针] 清理临时视频文件: {video_path}")
                    os.remove(video_path)
                    logger.debug(f"✅ [探针] 临时视频文件已删除: {video_path}")
                except Exception as e:
                    logger.warning(f"⚠️  [探针] 删除临时视频文件失败: {e}")
    
    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"清理临时目录: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")

