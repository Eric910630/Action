"""
内容结构Agent
负责提取视频的结构化信息（文本、画面、音频等）
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from app.agents.base import BaseAgent
from app.utils.video_analyzer import VideoAnalyzerClient
from app.utils.web_content_extractor import WebContentExtractor
import json
import re


class VideoStructure(BaseModel):
    """视频结构化信息"""
    duration: float = Field(description="视频时长（秒）", default=0.0)
    key_frames: List[Dict[str, Any]] = Field(description="关键帧信息", default_factory=list)
    scenes: List[Dict[str, Any]] = Field(description="场景信息", default_factory=list)
    visual_elements: Dict[str, Any] = Field(description="视觉元素（人物、物品、背景等）", default_factory=dict)
    audio_elements: Dict[str, Any] = Field(description="音频元素（音乐、旁白等）", default_factory=dict)
    transcript: str = Field(description="视频文本转录", default="")
    tags: List[str] = Field(description="视频标签（从文案中提取的#tag）", default_factory=list)


class ContentStructureAgent(BaseAgent):
    """内容结构Agent - 提取视频结构化信息"""
    
    def __init__(self):
        super().__init__()
        # 使用本地视频分析工具包（PySceneDetect + Whisper + MoviePy）
        self.video_analyzer = VideoAnalyzerClient()
        # 使用网页内容提取工具（Trafilatura）作为补充
        self.web_extractor = WebContentExtractor()
    
    def _init_tools(self) -> List:
        """初始化工具"""
        return []
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的视频内容分析专家，擅长提取视频的结构化信息。

工作流程：
1. 首先使用本地视频分析工具包（PySceneDetect + Whisper + MoviePy）提取视频的原始结构信息
2. 然后基于提取的信息，使用AI进行深度分析和补充

你需要从视频信息中提取：
1. 视频时长
2. 关键帧信息（时间点、画面描述）
3. 场景信息（场景切换、场景描述）
4. 视觉元素（人物、物品、背景、动作等）
5. 音频元素（音乐、旁白、音效等）
6. 视频文本转录（如果有）
7. 视频标签（从文案中提取的#tag，如 #美食 #旅行 等）

请以JSON格式返回结构化数据。"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行视频结构提取
        
        Args:
            input_data: 包含以下字段：
                - url: 视频URL（必需）
                - title: 视频标题（可选）
                
        Returns:
            VideoStructure 结构化数据
        """
        url = input_data.get("url")
        title = input_data.get("title", "")
        
        if not url:
            raise ValueError("URL不能为空")
        
        import time
        start_time = time.time()
        
        logger.info(f"🔍 [探针] ContentStructureAgent.execute 开始")
        logger.info(f"🔍 [探针] 输入参数: url={url[:100]}, title={title[:50] if title else 'N/A'}")
        logger.info(f"开始提取视频结构: {url}")
        
        video_structure_data = {
            "duration": 0.0,
            "key_frames": [],
            "scenes": [],
            "visual_elements": {},
            "audio_elements": {},
            "transcript": "",
            "tags": []
        }
        
        try:
            # 1. 尝试使用VideoAnalyzer提取视频信息（本地或远程）
            video_info = None
            try:
                step_start = time.time()
                logger.info(f"🔍 [探针] 步骤1: 调用VideoAnalyzer提取视频信息")
                video_info = await self.video_analyzer.analyze(url)
                step_time = time.time() - step_start
                logger.info(f"✅ [探针] 步骤1完成: VideoAnalyzer提取成功, 耗时 {step_time:.2f}秒")
                logger.info(f"VideoAnalyzer提取成功: {url}")
                
                # 解析视频信息
                if isinstance(video_info, dict):
                    logger.debug(f"🔍 [探针] 解析视频信息: keys={list(video_info.keys())}")
                    
                    # 提取时长
                    if "duration" in video_info:
                        video_structure_data["duration"] = float(video_info.get("duration", 0))
                        logger.debug(f"🔍 [探针] 提取时长: {video_structure_data['duration']}")
                    
                    # 提取关键帧和场景（如果VideoAnalyzer提供）
                    if "shot_table" in video_info:
                        shots = video_info.get("shot_table", [])
                        video_structure_data["scenes"] = shots
                        logger.debug(f"🔍 [探针] 提取场景: 场景数={len(shots)}")
                    
                    # 提取文本转录
                    if "transcript" in video_info:
                        video_structure_data["transcript"] = video_info.get("transcript", "")
                        logger.debug(f"🔍 [探针] 提取转录: 文本长度={len(video_structure_data['transcript'])}")
                    elif "script_content" in video_info:
                        video_structure_data["transcript"] = video_info.get("script_content", "")
                        logger.debug(f"🔍 [探针] 提取脚本内容: 文本长度={len(video_structure_data['transcript'])}")
                    
                    # 从转录文本中提取标签（#tag）
                    transcript_text = video_structure_data.get("transcript", "")
                    if transcript_text:
                        tags = self._extract_tags_from_text(transcript_text)
                        if tags:
                            video_structure_data["tags"] = tags
                            logger.debug(f"🔍 [探针] 从转录文本提取标签: {tags}")
                    
                    # 提取关键帧（如果提供）
                    if "key_frames" in video_info and video_info["key_frames"]:
                        video_structure_data["key_frames"] = video_info.get("key_frames", [])
                        logger.debug(f"🔍 [探针] 提取关键帧: 关键帧数={len(video_structure_data['key_frames'])}")
                else:
                    logger.warning(f"⚠️  [探针] video_info不是字典类型: {type(video_info)}")
                
            except Exception as e:
                step_time = time.time() - step_start
                logger.error(f"❌ [探针] 步骤1失败, 耗时 {step_time:.2f}秒: VideoAnalyzer提取失败: {e}")
                logger.warning(f"⚠️  视频解析失败，将继续尝试提取网页内容作为补充")
            
            # 1.5. 提取网页内容作为补充（替代Firecrawl，无论视频分析成功与否都尝试）
            # 这样可以获取网页上的文本内容、描述等信息，作为视频分析的补充
            try:
                step_start_web = time.time()
                logger.info(f"🔍 [探针] 步骤1.5: 提取网页内容作为补充（替代Firecrawl）")
                web_content = await self.web_extractor.extract_from_url(url, include_metadata=True)
                step_time_web = time.time() - step_start_web
                
                if web_content.get("content"):
                    # 如果视频分析没有提取到转录文本，使用网页内容作为补充
                    if not video_structure_data.get("transcript"):
                        video_structure_data["transcript"] = web_content.get("content", "")
                        logger.info(f"✅ [探针] 步骤1.5完成: 网页内容提取成功（作为转录文本补充）, 耗时 {step_time_web:.2f}秒, 内容长度={len(video_structure_data['transcript'])}")
                    else:
                        # 如果已有转录文本，将网页内容追加作为补充信息
                        existing_transcript = video_structure_data.get("transcript", "")
                        web_text = web_content.get("content", "")
                        if web_text and web_text not in existing_transcript:
                            # 只追加新内容，避免重复
                            video_structure_data["transcript"] = f"{existing_transcript}\n\n[网页补充内容]\n{web_text}"
                            logger.info(f"✅ [探针] 步骤1.5完成: 网页内容提取成功（追加补充信息）, 耗时 {step_time_web:.2f}秒, 追加长度={len(web_text)}")
                        else:
                            logger.info(f"✅ [探针] 步骤1.5完成: 网页内容提取成功（但内容重复或为空）, 耗时 {step_time_web:.2f}秒")
                    
                    # 从网页内容中提取标签（如果还没有标签）
                    if not video_structure_data.get("tags") and video_structure_data.get("transcript"):
                        tags = self._extract_tags_from_text(video_structure_data["transcript"])
                        if tags:
                            video_structure_data["tags"] = tags
                            logger.debug(f"🔍 [探针] 从网页内容提取标签: {tags}")
                else:
                    logger.warning(f"⚠️  [探针] 步骤1.5: 网页内容提取失败或为空")
            except Exception as web_e:
                logger.warning(f"⚠️  网页内容提取失败: {web_e}，将使用已有信息继续处理")
            
            # 2. 使用LLM进行结构化分析和补充
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤2: 使用LLM进行结构化分析和补充")
            analysis_prompt = f"""
请分析以下视频内容，提取结构化信息：

视频标题：{title}
视频URL：{url}
已有信息：
- 时长：{video_structure_data['duration']}秒
- 场景数：{len(video_structure_data['scenes'])}
- 转录文本：{video_structure_data['transcript'][:500] if video_structure_data['transcript'] else '无'}

请补充以下信息（如果已有信息不足，请基于标题和URL进行合理推断）：
1. 关键帧信息（至少3-5个关键时间点的画面描述）
2. 视觉元素（人物、物品、背景、动作等）
3. 音频元素（音乐风格、旁白特点等）
4. 场景描述（如果场景信息不足）
5. 视频标签（从转录文本中提取的#tag，如 #美食 #旅行 #搞笑 等，如果没有则基于内容推断）

请以JSON格式返回，格式如下：
{{
    "key_frames": [
        {{"time": 0.0, "description": "画面描述"}},
        ...
    ],
    "visual_elements": {{
        "characters": ["人物描述"],
        "objects": ["物品描述"],
        "background": "背景描述",
        "actions": ["动作描述"]
    }},
    "audio_elements": {{
        "music": "音乐风格描述",
        "voiceover": "旁白特点",
        "sound_effects": ["音效描述"]
    }},
    "scenes": [
        {{"start_time": 0.0, "end_time": 5.0, "description": "场景描述"}},
        ...
    ],
    "tags": ["#标签1", "#标签2", ...]
}}
"""
            
            try:
                llm_start = time.time()
                logger.debug(f"🔍 [探针] 调用LLM生成结构化数据")
                response = await self.llm_client.generate(
                    prompt=analysis_prompt,
                    system_prompt=self._get_system_prompt(),
                    temperature=0.3,
                    max_tokens=2000
                )
                llm_time = time.time() - llm_start
                logger.debug(f"🔍 [探针] LLM响应, 耗时 {llm_time:.2f}秒")
                
                # 解析LLM响应
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.debug(f"🔍 [探针] LLM返回内容长度: {len(content)}")
                
                # 尝试提取JSON
                if "{" in content and "}" in content:
                    # 提取JSON部分
                    start_idx = content.find("{")
                    end_idx = content.rfind("}") + 1
                    json_str = content[start_idx:end_idx]
                    logger.debug(f"🔍 [探针] 提取JSON字符串, 长度: {len(json_str)}")
                    
                    try:
                        llm_data = json.loads(json_str)
                        logger.debug(f"🔍 [探针] JSON解析成功: keys={list(llm_data.keys())}")
                        
                        # 合并LLM分析结果
                        if "key_frames" in llm_data:
                            old_count = len(video_structure_data["key_frames"])
                            video_structure_data["key_frames"] = llm_data.get("key_frames", [])
                            logger.debug(f"🔍 [探针] 合并关键帧: {old_count} -> {len(video_structure_data['key_frames'])}")
                        if "visual_elements" in llm_data:
                            video_structure_data["visual_elements"] = llm_data.get("visual_elements", {})
                            logger.debug(f"🔍 [探针] 合并视觉元素: {list(video_structure_data['visual_elements'].keys())}")
                        if "audio_elements" in llm_data:
                            video_structure_data["audio_elements"] = llm_data.get("audio_elements", {})
                            logger.debug(f"🔍 [探针] 合并音频元素: {list(video_structure_data['audio_elements'].keys())}")
                        if "scenes" in llm_data and not video_structure_data["scenes"]:
                            video_structure_data["scenes"] = llm_data.get("scenes", [])
                            logger.debug(f"🔍 [探针] 补充场景: {len(video_structure_data['scenes'])} 个")
                        if "tags" in llm_data:
                            # 合并LLM提取的标签和从文本中提取的标签
                            llm_tags = llm_data.get("tags", [])
                            existing_tags = video_structure_data.get("tags", [])
                            # 去重并合并
                            all_tags = list(set(existing_tags + llm_tags))
                            video_structure_data["tags"] = all_tags
                            logger.debug(f"🔍 [探针] 合并标签: {len(all_tags)} 个标签")
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️  [探针] LLM返回的JSON解析失败: {e}")
                else:
                    logger.warning(f"⚠️  [探针] LLM返回内容中未找到JSON结构")
            except Exception as e:
                logger.warning(f"⚠️  [探针] LLM分析失败: {e}，使用基础信息")
            
            step_time = time.time() - step_start
            logger.info(f"✅ [探针] 步骤2完成: LLM结构化分析成功, 耗时 {step_time:.2f}秒")
            
            # 2.5. 如果还没有标签，从转录文本中再次提取
            if not video_structure_data.get("tags"):
                transcript_text = video_structure_data.get("transcript", "")
                if transcript_text:
                    tags = self._extract_tags_from_text(transcript_text)
                    if tags:
                        video_structure_data["tags"] = tags
                        logger.debug(f"🔍 [探针] 从转录文本提取标签（补充）: {tags}")
            
            # 3. 验证并返回结构化数据
            step_start = time.time()
            logger.info(f"🔍 [探针] 步骤3: 验证并返回结构化数据")
            video_structure = VideoStructure(**video_structure_data)
            step_time = time.time() - step_start
            
            total_time = time.time() - start_time
            logger.info(f"✅ [探针] 步骤3完成: 数据验证成功, 耗时 {step_time:.4f}秒")
            logger.info(f"✅ [探针] ContentStructureAgent.execute 完成, 总耗时 {total_time:.2f}秒")
            logger.debug(f"🔍 [探针] 返回结果摘要: duration={video_structure_data.get('duration')}, scenes={len(video_structure_data.get('scenes', []))}, transcript_len={len(video_structure_data.get('transcript', ''))}")
            
            logger.info(f"视频结构提取完成: {url}")
            return {
                "status": "success",
                "video_structure": video_structure.model_dump()
            }
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [探针] ContentStructureAgent.execute 失败, 总耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.error(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
            logger.error(f"视频结构提取失败: {e}")
            # 返回基础结构（避免完全失败）
            return {
                "status": "partial",
                "video_structure": VideoStructure(**video_structure_data).model_dump(),
                "error": str(e)
            }
    
    def _extract_tags_from_text(self, text: str) -> List[str]:
        """
        从文本中提取标签（#tag格式）
        
        Args:
            text: 输入文本
            
        Returns:
            标签列表（包含#符号）
        """
        if not text:
            return []
        
        # 使用正则表达式提取所有 #tag 格式的标签
        # 匹配 # 后面跟着中文、英文、数字、下划线的标签
        tag_pattern = r'#[\u4e00-\u9fa5a-zA-Z0-9_]+'
        tags = re.findall(tag_pattern, text)
        
        # 去重并保持顺序
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        
        logger.debug(f"🔍 [探针] 从文本中提取到 {len(unique_tags)} 个标签: {unique_tags[:10]}")
        return unique_tags

