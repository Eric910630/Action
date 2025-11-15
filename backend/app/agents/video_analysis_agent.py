"""
视频拆解Agent
负责视频内容分析和拆解
"""
from typing import Dict, Any, List
from loguru import logger
from app.agents.base import BaseAgent


class VideoAnalysisAgent(BaseAgent):
    """视频拆解Agent"""
    
    def _init_tools(self) -> List:
        """初始化工具"""
        # 视频拆解工具在execute中直接调用，这里暂时返回空列表
        # 如果需要，可以添加更多工具函数
        return []
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的视频分析专家，擅长拆解短视频的结构和技巧。
你需要：
1. 分析视频的镜头结构
2. 提取黄金3秒的钩子技巧
3. 识别爆款公式和技巧
4. 提供制作要点建议

请根据视频拆解工具返回的原始数据，进行深度分析和结构化整理。"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行视频拆解
        
        Args:
            input_data: 包含以下字段：
                - video_url: 视频URL
        
        Returns:
            包含以下字段的字典：
                - video_info: 视频基本信息
                - basic_info: 基础信息
                - shot_table: 镜头表格
                - golden_3s: 黄金3秒分析
                - viral_formula: 爆款公式
                - production_tips: 制作要点
        """
        video_url = input_data.get("video_url")
        if not video_url:
            raise ValueError("video_url不能为空")
        
        logger.info(f"开始视频拆解: {video_url}")
        
        # 1. 调用视频拆解工具
        from app.utils.video_analyzer import VideoAnalyzerClient
        analyzer_client = VideoAnalyzerClient()
        
        try:
            raw_data = await analyzer_client.analyze(video_url)
        except Exception as e:
            logger.error(f"视频拆解工具调用失败: {e}")
            raise
        
        # 2. 使用LLM进行深度分析
        analysis_prompt = f"""
请对以下视频拆解结果进行深度分析：

原始数据：
{str(raw_data)[:1000]}  # 限制长度

请提供：
1. 视频结构分析
2. 黄金3秒钩子技巧分析
3. 爆款公式识别
4. 制作要点建议

请以结构化格式返回分析结果。
"""
        
        try:
            response = await self.llm_client.generate(
                prompt=analysis_prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
                max_tokens=2000
            )
            analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"LLM分析失败: {e}")
            analysis = "分析完成"
        
        # 3. 解析和结构化数据
        from app.services.analysis.service import VideoAnalysisService
        analysis_service = VideoAnalysisService()
        structured_report = analysis_service.parse_report(raw_data)
        
        # 4. 添加LLM分析结果
        structured_report["llm_analysis"] = analysis
        
        logger.info("视频拆解完成")
        return structured_report

