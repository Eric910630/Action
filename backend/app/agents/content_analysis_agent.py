"""
内容分析Agent
负责分析视频内容并评估电商适配性
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from loguru import logger
from app.agents.base import BaseAgent
import json


class EcommerceFit(BaseModel):
    """电商适配性"""
    score: float = Field(description="适配性评分（0-1）", ge=0, le=1, default=0.0)
    reasoning: str = Field(description="适配性原因", default="")
    applicable_categories: List[str] = Field(description="适用类目列表", default_factory=list)


class ContentAnalysis(BaseModel):
    """内容分析结果"""
    summary: str = Field(description="视频内容摘要", default="")
    style: str = Field(description="视频风格描述", default="")
    script_structure: Dict[str, str] = Field(description="脚本结构（hook, body, cta）", default_factory=dict)
    ecommerce_fit: Dict[str, Any] = Field(description="电商适配性评估", default_factory=dict)


class ContentAnalysisAgent(BaseAgent):
    """内容分析Agent - 分析视频内容并评估电商适配性"""
    
    def _init_tools(self) -> List:
        """初始化工具"""
        return []
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的电商内容分析专家，擅长分析视频内容并评估其是否**有特殊的爆点可以迁移到直播带货的直播间引流视频、产品种草视频、产品机制透穿视频上**。

你需要：
1. 分析视频的核心主题和内容摘要
2. 识别视频的风格特点（如：搞笑、专业、情感、实用等）
3. 分析脚本结构（开头钩子、主体内容、行动号召）
4. 评估电商适配性：
   - 判断视频风格是否**有特殊的爆点可以迁移到直播带货的直播间引流视频、产品种草视频、产品机制透穿视频上**
   - 评估内容的情感倾向和**增加曝光与吸引刷到这个短视频的观众的兴趣的能力**
   - 识别**此视频中的爆点，是否有机会迁移到直播间即将售卖、种草、引流、透穿机制的商品上**
   - 给出适配性评分（0-1）

注意：
- 适配性评估不需要区分具体品类，只考虑是否有可能用在直播带货
- 评分要客观，基于内容的实际特点
- 适用类目要具体，但不要过于局限

请以JSON格式返回分析结果。"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行内容分析
        
        Args:
            input_data: 包含以下字段：
                - video_structure: 视频结构化信息（必需）
                - title: 视频标题（可选）
                - url: 视频URL（可选）
                
        Returns:
            ContentAnalysis 结构化数据
        """
        video_structure = input_data.get("video_structure", {})
        title = input_data.get("title", "")
        url = input_data.get("url", "")
        
        if not video_structure:
            raise ValueError("video_structure不能为空")
        
        logger.info(f"开始内容分析: {title[:50] if title else url}")
        
        # 构建分析提示词
        transcript = video_structure.get("transcript", "")
        visual_elements = video_structure.get("visual_elements", {})
        scenes = video_structure.get("scenes", [])
        duration = video_structure.get("duration", 0)
        
        analysis_prompt = f"""
分析以下视频内容，判断是否**有特殊的爆点可以迁移到直播带货的直播间引流视频、产品种草视频、产品机制透穿视频上**：

视频标题：{title}
视频时长：{duration}秒

视频内容：
- 转录文本：{transcript[:500] if transcript else '无转录文本'}
- 视觉元素：{json.dumps(visual_elements, ensure_ascii=False)[:300] if visual_elements else '无'}
- 场景数：{len(scenes)}

请提供以下分析：
1. **内容摘要**：用1-2句话概括视频的核心内容
2. **视频风格**：描述视频的风格特点（如：搞笑、专业、情感、实用、教育等）
3. **脚本结构**：
   - hook（开头钩子）：视频如何吸引观众
   - body（主体内容）：主要内容是什么
   - cta（行动号召）：是否有明确的引导
4. **电商适配性评估**：
   - score（评分0-1）：此视频中的爆点，是否有机会迁移到直播间即将售卖、种草、引流、透穿机制的商品上
   - reasoning（原因）：为什么有或没有爆点可以迁移，具体有哪些爆点可以迁移
   - applicable_categories（适用类目）：如果适合，可以用于哪些商品类目（如：女装、美妆、家居等）
     **重要**：适用类目要准确、具体，只列出真正相关的类目。如果内容与某个类目完全不相关，不要列出。
     例如：如果内容是关于"收藏品"的，不要列出"女装"；如果内容是关于"便利店食品"的，不要列出"时尚"。
     要基于内容的实际特点，判断哪些类目可以真正使用这个热点进行带货。

请以JSON格式返回，格式如下：
{{
    "summary": "内容摘要",
    "style": "视频风格描述",
    "script_structure": {{
        "hook": "开头钩子分析",
        "body": "主体内容分析",
        "cta": "行动号召分析"
    }},
    "ecommerce_fit": {{
        "score": 0.85,
        "reasoning": "适配性原因分析",
        "applicable_categories": ["女装", "美妆"]
    }}
}}
"""
        
        try:
            response = await self.llm_client.generate(
                prompt=analysis_prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
                max_tokens=1500
            )
            
            # 解析LLM响应
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取JSON
            analysis_data = {
                "summary": "",
                "style": "",
                "script_structure": {},
                "ecommerce_fit": {
                    "score": 0.0,
                    "reasoning": "",
                    "applicable_categories": []
                }
            }
            
            if "{" in content and "}" in content:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_str = content[start_idx:end_idx]
                
                try:
                    llm_data = json.loads(json_str)
                    analysis_data.update(llm_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"LLM返回的JSON解析失败: {e}，使用文本提取")
                    # 如果JSON解析失败，尝试从文本中提取关键信息
                    if "摘要" in content or "summary" in content.lower():
                        # 简单提取摘要
                        lines = content.split("\n")
                        for line in lines:
                            if "摘要" in line or "summary" in line.lower():
                                analysis_data["summary"] = line.split("：")[-1].strip() if "：" in line else line.strip()
                                break
            
            # 验证并构建结构化数据
            ecommerce_fit_data = analysis_data.get("ecommerce_fit", {})
            ecommerce_fit = EcommerceFit(
                score=float(ecommerce_fit_data.get("score", 0.0)),
                reasoning=ecommerce_fit_data.get("reasoning", ""),
                applicable_categories=ecommerce_fit_data.get("applicable_categories", [])
            )
            
            content_analysis = ContentAnalysis(
                summary=analysis_data.get("summary", ""),
                style=analysis_data.get("style", ""),
                script_structure=analysis_data.get("script_structure", {}),
                ecommerce_fit=ecommerce_fit.model_dump()
            )
            
            logger.info(f"内容分析完成: 适配性评分={ecommerce_fit.score:.2f}")
            return {
                "status": "success",
                "content_analysis": content_analysis.model_dump()
            }
            
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            # 返回默认分析结果
            default_analysis = ContentAnalysis(
                summary=title or "无摘要",
                style="未知",
                script_structure={},
                ecommerce_fit=EcommerceFit(score=0.0, reasoning="分析失败", applicable_categories=[]).model_dump()
            )
            return {
                "status": "error",
                "content_analysis": default_analysis.model_dump(),
                "error": str(e)
            }

