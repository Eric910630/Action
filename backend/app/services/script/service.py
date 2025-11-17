"""
脚本生成服务
"""
import uuid
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.script import Script
from app.models.hotspot import Hotspot
from app.models.product import Product
from app.models.analysis import AnalysisReport
from app.utils.deepseek import DeepSeekClient
from app.agents.script_generation_agent import ScriptGenerationAgent


class ScriptGeneratorService:
    """脚本生成服务（使用Agent）"""
    
    def __init__(self, use_agent: bool = True):
        """
        初始化服务
        
        Args:
            use_agent: 是否使用Agent架构，默认True
        """
        self.use_agent = use_agent
        if use_agent:
            self.script_agent = ScriptGenerationAgent()
        else:
            # 保留原有实现作为fallback
            self.deepseek_client = DeepSeekClient()
        
        # 优化建议也需要LLM，所以保留deepseek_client
        if not hasattr(self, 'deepseek_client'):
            self.deepseek_client = DeepSeekClient()
        
        # 为了兼容，也添加llm_client别名
        self.llm_client = self.deepseek_client
    
    def build_prompt(
        self,
        hotspot: Hotspot,
        product: Product,
        analysis_report: Optional[AnalysisReport] = None,
        duration: int = 10,
        script_index: int = 1,
        total_scripts: int = 5
    ) -> str:
        """构建脚本生成提示词，支持生成多个不同版本的脚本"""
        
        # 提取热点信息
        hotspot_info = f"""
热点标题：{hotspot.title}
热点标签：{', '.join(hotspot.tags or [])}
热点URL：{hotspot.url}
"""
        
        # 提取商品信息
        selling_points = product.selling_points or []
        selling_points_str = '\n'.join([f"- {point}" for point in selling_points])
        
        product_info = f"""
商品名称：{product.name}
品牌：{product.brand or '无'}
品类：{product.category}
核心卖点：
{selling_points_str}
价格：{product.price}
商品描述：{product.description or '无'}
说明手卡：{product.hand_card or '无'}
"""
        
        # 提取爆款技巧
        techniques_info = ""
        viral_formula_info = ""
        
        if analysis_report:
            # 提取技巧
            from app.services.analysis.service import VideoAnalysisService
            analysis_service = VideoAnalysisService()
            techniques = analysis_service.extract_techniques({
                "shot_table": analysis_report.shot_table or [],
                "golden_3s": analysis_report.golden_3s or {},
                "viral_formula": analysis_report.viral_formula or {},
                "production_tips": analysis_report.production_tips or {},
                "highlights": analysis_report.highlights or []
            })
            
            if techniques:
                techniques_info = "\n爆款技巧：\n"
                for tech in techniques[:5]:  # 最多5个技巧
                    techniques_info += f"- {tech.get('name', '')}: {tech.get('description', '')}\n"
            
            # 提取爆款公式
            viral_formula = analysis_report.viral_formula or {}
            if viral_formula.get("formula_name"):
                viral_formula_info = f"""
爆款公式：{viral_formula.get('formula_name')}
公式结构：{viral_formula.get('formula_structure', '')}
运用方式：{viral_formula.get('application_method', '')}
"""
        
        # 构建完整提示词
        diversity_note = ""
        if total_scripts > 1:
            diversity_note = f"""
【重要提示】
这是第 {script_index} 个脚本（共 {total_scripts} 个）。请确保这个脚本与之前的脚本有明显不同：
- 使用不同的切入角度和表达方式
- 采用不同的叙事结构（如：问题-解决方案、对比、故事化等）
- 突出不同的卖点或情感点
- 使用不同的开场方式（如：疑问式、对比式、故事式等）
- 确保每个脚本都有独特的创意点
"""
        
        prompt = f"""你是一位资深短视频编导，需要基于以下信息生成一个{duration}秒的引流短视频脚本。

【热点信息】
{hotspot_info}

【商品信息】
{product_info}

{techniques_info}

{viral_formula_info}

{diversity_note}

【要求】
1. 视频时长：{duration}秒（5-15秒之间）
2. 结合热点话题和商品特性
3. 运用上述爆款技巧和公式
4. 突出商品卖点和价格优惠
5. 适合{product.category}直播间风格
6. 内容要吸引人，能够引导用户进入直播间
7. {"请确保这个脚本与之前的脚本有明显不同，使用不同的创意角度和表达方式" if total_scripts > 1 else ""}

请生成以下内容，并以JSON格式返回：
{{
    "video_info": {{
        "title": "视频标题",
        "duration": {duration},
        "theme": "视频主题",
        "core_selling_point": "核心卖点"
    }},
    "script_content": "完整脚本内容（包含台词、动作、镜头描述）",
    "shot_list": [
        {{
            "shot_number": 1,
            "time_range": "0-3秒",
            "shot_type": "中景/特写/全景",
            "content": "画面内容描述",
            "dialogue": "台词",
            "action": "动作",
            "music": "音乐要求",
            "purpose": "镜头作用",
            "shaping_point": "塑造点"
        }}
    ],
    "production_notes": {{
        "shooting_tips": ["拍摄要点1", "拍摄要点2"],
        "editing_tips": ["剪辑要点1", "剪辑要点2"],
        "key_points": ["关键要点1", "关键要点2"]
    }},
    "tags": {{
        "recommended_tags": ["推荐标签1", "推荐标签2"],
        "recommended_topics": ["推荐话题1", "推荐话题2"]
    }}
}}

请确保：
- shot_list中的镜头数量合理，总时长不超过{duration}秒
- 每个镜头都有明确的时间区间
- 台词要简洁有力，突出卖点
- 标签和话题要与内容匹配
"""
        
        return prompt
    
    async def generate_script(
        self,
        hotspot: Hotspot,
        product: Product,
        analysis_report: Optional[AnalysisReport] = None,
        duration: int = 10,
        adjustment_feedback: Optional[str] = None,
        script_index: int = 1,  # 新增：当前脚本序号（1-5）
        total_scripts: int = 5  # 新增：总脚本数量
    ) -> Dict[str, Any]:
        """生成脚本（使用Agent），支持生成多个不同版本的脚本"""
        logger.info(f"开始生成脚本: 商品={product.name}, 热点={hotspot.title}, 脚本序号={script_index}/{total_scripts}, 使用Agent={self.use_agent}, adjustment_feedback={'有' if adjustment_feedback else '无'}")
        
        if self.use_agent:
            # 使用Agent架构
            try:
                result = await self.script_agent.execute({
                    "hotspot_id": hotspot.id,
                    "product_id": product.id,
                    "analysis_report_id": analysis_report.id if analysis_report else None,
                    "duration": duration,
                    "adjustment_feedback": adjustment_feedback,
                    "script_index": script_index,  # 传入脚本序号
                    "total_scripts": total_scripts  # 传入总数量
                })
                
                logger.info(f"脚本生成成功（使用Agent），序号={script_index}")
                return result
            except Exception as e:
                logger.error(f"Agent脚本生成失败: {e}，回退到传统方法")
                # 回退到传统方法
                return await self._generate_script_legacy(hotspot, product, analysis_report, duration, script_index, total_scripts)
        else:
            # 使用传统方法
            return await self._generate_script_legacy(hotspot, product, analysis_report, duration, script_index, total_scripts)
    
    async def _generate_script_legacy(
        self,
        hotspot: Hotspot,
        product: Product,
        analysis_report: Optional[AnalysisReport] = None,
        duration: int = 10,
        script_index: int = 1,
        total_scripts: int = 5
    ) -> Dict[str, Any]:
        """传统脚本生成方法（作为fallback），支持生成多个不同版本的脚本"""
        # 构建提示词
        prompt = self.build_prompt(hotspot, product, analysis_report, duration, script_index, total_scripts)
        
        # 系统提示词
        system_prompt = """你是一位经验丰富的短视频编导，擅长创作引流短视频脚本。
你需要根据热点、商品信息和爆款技巧，生成高质量的拍摄脚本和分镜。
脚本要简洁有力，能够吸引用户点击进入直播间。"""
        
        try:
            # 调用DeepSeek API
            response = await self.deepseek_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=3000
            )
            
            # 解析响应
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析JSON
            script_data = self.parse_script_response(content)
            
            logger.info("脚本生成成功（传统方法）")
            return script_data
            
        except Exception as e:
            logger.error(f"脚本生成失败: {e}")
            raise
    
    def parse_script_response(self, content: str) -> Dict[str, Any]:
        """解析AI返回的脚本内容"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                script_data = json.loads(json_str)
            else:
                # 如果没有JSON，尝试手动构建
                script_data = self._build_script_from_text(content)
            
            # 验证和补充数据
            if "shot_list" not in script_data:
                script_data["shot_list"] = []
            
            if "production_notes" not in script_data:
                script_data["production_notes"] = {
                    "shooting_tips": [],
                    "editing_tips": [],
                    "key_points": []
                }
            
            if "tags" not in script_data:
                script_data["tags"] = {
                    "recommended_tags": [],
                    "recommended_topics": []
                }
            
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"解析脚本JSON失败: {e}")
            # 返回默认结构
            return self._build_default_script(content)
    
    def _build_script_from_text(self, content: str) -> Dict[str, Any]:
        """从文本构建脚本结构"""
        return {
            "video_info": {
                "title": "生成的视频",
                "duration": 10,
                "theme": "商品推广",
                "core_selling_point": "价格优惠"
            },
            "script_content": content,
            "shot_list": [],
            "production_notes": {
                "shooting_tips": [],
                "editing_tips": [],
                "key_points": []
            },
            "tags": {
                "recommended_tags": [],
                "recommended_topics": []
            }
        }
    
    def _build_default_script(self, content: str) -> Dict[str, Any]:
        """构建默认脚本结构"""
        return {
            "video_info": {
                "title": "生成的视频",
                "duration": 10,
                "theme": "商品推广",
                "core_selling_point": "价格优惠"
            },
            "script_content": content,
            "shot_list": [
                {
                    "shot_number": 1,
                    "time_range": "0-10秒",
                    "shot_type": "中景",
                    "content": "商品展示",
                    "dialogue": "请查看脚本内容",
                    "action": "展示商品",
                    "music": "轻快背景音乐",
                    "purpose": "吸引注意",
                    "shaping_point": "突出商品"
                }
            ],
            "production_notes": {
                "shooting_tips": ["注意光线", "突出商品特点"],
                "editing_tips": ["快速切换", "节奏紧凑"],
                "key_points": ["突出价格", "强调优惠"]
            },
            "tags": {
                "recommended_tags": ["商品", "优惠"],
                "recommended_topics": ["好物推荐"]
            }
        }
    
    def generate_shot_list(self, script_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成分镜表格（如果shot_list不完整，则补充）"""
        shot_list = script_data.get("shot_list", [])
        
        # 如果shot_list为空，尝试从script_content中提取
        if not shot_list and script_data.get("script_content"):
            # 简化处理：创建一个默认分镜
            shot_list = [
                {
                    "shot_number": 1,
                    "time_range": f"0-{script_data.get('video_info', {}).get('duration', 10)}秒",
                    "shot_type": "中景",
                    "content": "商品展示",
                    "dialogue": script_data.get("script_content", "")[:50],
                    "action": "展示商品",
                    "music": "背景音乐",
                    "purpose": "吸引注意",
                    "shaping_point": "突出商品"
                }
            ]
        
        # 确保每个镜头都有编号
        for idx, shot in enumerate(shot_list, 1):
            if "shot_number" not in shot:
                shot["shot_number"] = idx
        
        return shot_list
    
    def save_script(
        self,
        db: Session,
        hotspot_id: str,
        product_id: str,
        analysis_report_id: Optional[str],
        script_data: Dict[str, Any],
        status: str = "draft"
    ) -> Script:
        """保存脚本到数据库"""
        # 修复：确保空字符串转换为None，避免外键约束错误
        if analysis_report_id == '' or not analysis_report_id:
            analysis_report_id = None
        
        script = Script(
            id=str(uuid.uuid4()),
            hotspot_id=hotspot_id,
            product_id=product_id,
            analysis_report_id=analysis_report_id,  # 现在确保是None而不是空字符串
            video_info=script_data.get("video_info"),
            script_content=script_data.get("script_content"),
            shot_list=script_data.get("shot_list"),
            production_notes=script_data.get("production_notes"),
            tags=script_data.get("tags"),
            status=status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(script)
        db.commit()
        db.refresh(script)
        
        logger.info(f"保存脚本: {script.id}")
        return script
    
    async def get_optimization_suggestions(self, script: Script) -> List[Dict[str, Any]]:
        """获取脚本优化建议（使用LLM生成更智能的建议）"""
        suggestions = []
        
        video_info = script.video_info or {}
        duration = video_info.get("duration", 0)
        shot_list = script.shot_list or []
        script_content = script.script_content or ""
        
        # 基础检查
        # 时长检查
        if duration < 5:
            suggestions.append({
                "type": "duration",
                "level": "warning",
                "message": "视频时长过短，建议至少5秒",
                "suggestion": "增加内容或放慢节奏"
            })
        elif duration > 15:
            suggestions.append({
                "type": "duration",
                "level": "warning",
                "message": "视频时长过长，建议控制在15秒以内",
                "suggestion": "精简内容或加快节奏"
            })
        
        # 分镜检查
        if not shot_list or len(shot_list) == 0:
            suggestions.append({
                "type": "shot_list",
                "level": "error",
                "message": "缺少分镜信息",
                "suggestion": "请补充分镜表格"
            })
        elif len(shot_list) < 2:
            suggestions.append({
                "type": "shot_list",
                "level": "info",
                "message": "分镜数量较少，建议增加镜头切换",
                "suggestion": "可以增加特写、全景等不同景别"
            })
        
        # 标签检查
        tags = script.tags or {}
        if not tags.get("recommended_tags"):
            suggestions.append({
                "type": "tags",
                "level": "warning",
                "message": "缺少推荐标签",
                "suggestion": "添加相关标签以提高曝光"
            })
        
        # 使用LLM生成更详细的优化建议
        try:
            llm_suggestions = await self._generate_llm_optimization_suggestions(script)
            suggestions.extend(llm_suggestions)
        except Exception as e:
            logger.warning(f"LLM生成优化建议失败: {e}，使用基础建议")
        
        return suggestions
    
    async def _generate_llm_optimization_suggestions(self, script: Script) -> List[Dict[str, Any]]:
        """使用LLM生成优化建议"""
        video_info = script.video_info or {}
        shot_list = script.shot_list or []
        script_content = script.script_content or ""
        
        # 构建提示词
        prompt = f"""请分析以下视频脚本，提供优化建议：

【视频信息】
标题：{video_info.get('title', '无')}
时长：{video_info.get('duration', 0)}秒
主题：{video_info.get('theme', '无')}
核心卖点：{video_info.get('core_selling_point', '无')}

【脚本内容】
{script_content[:500] if script_content else '无'}

【分镜信息】
分镜数量：{len(shot_list)}
"""
        
        if shot_list:
            for i, shot in enumerate(shot_list[:3], 1):
                prompt += f"\n镜头{i}：{shot.get('time_range', '')} - {shot.get('content', '')} - {shot.get('dialogue', '')}"
        
        prompt += """

请提供3-5条具体的优化建议，包括：
1. 内容优化（台词、卖点突出等）
2. 节奏优化（时长、镜头切换等）
3. 视觉优化（景别、画面等）
4. 转化优化（引导进入直播间等）

请以JSON格式返回，格式如下：
{
  "suggestions": [
    {
      "type": "内容/节奏/视觉/转化",
      "level": "info/warning/error",
      "message": "问题描述",
      "suggestion": "具体建议"
    }
  ]
}
"""
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt="你是一位短视频优化专家，擅长分析脚本并提供专业的优化建议。",
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析JSON响应
            import json
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("suggestions", [])
            else:
                # 如果解析失败，返回空列表
                return []
        except Exception as e:
            logger.error(f"LLM生成优化建议失败: {e}")
            return []

