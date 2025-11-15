"""
Agents模块
提供各种AI Agent实现
"""
from app.agents.base import BaseAgent
from app.agents.video_analysis_agent import VideoAnalysisAgent
from app.agents.relevance_analysis_agent import RelevanceAnalysisAgent
from app.agents.script_generation_agent import ScriptGenerationAgent
from app.agents.content_structure_agent import ContentStructureAgent
from app.agents.content_analysis_agent import ContentAnalysisAgent

__all__ = [
    "BaseAgent",
    "VideoAnalysisAgent",
    "RelevanceAnalysisAgent",
    "ScriptGenerationAgent",
    "ContentStructureAgent",
    "ContentAnalysisAgent",
]

# 延迟导入，避免循环依赖
def get_video_analysis_agent():
    """获取视频拆解Agent实例"""
    from app.agents.video_analysis_agent import VideoAnalysisAgent
    return VideoAnalysisAgent()

def get_relevance_analysis_agent():
    """获取关联度分析Agent实例"""
    from app.agents.relevance_analysis_agent import RelevanceAnalysisAgent
    return RelevanceAnalysisAgent()

def get_script_generation_agent():
    """获取脚本生成Agent实例"""
    from app.agents.script_generation_agent import ScriptGenerationAgent
    return ScriptGenerationAgent()

def get_content_structure_agent():
    """获取内容结构Agent实例"""
    from app.agents.content_structure_agent import ContentStructureAgent
    return ContentStructureAgent()

def get_content_analysis_agent():
    """获取内容分析Agent实例"""
    from app.agents.content_analysis_agent import ContentAnalysisAgent
    return ContentAnalysisAgent()

