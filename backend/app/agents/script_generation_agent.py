"""
脚本生成Agent
负责基于热点、商品和拆解报告生成视频脚本
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from app.agents.base import BaseAgent
from app.tools.database_tools import get_hotspot_info, get_product_info, get_analysis_report_info


class ScriptGenerationAgent(BaseAgent):
    """脚本生成Agent"""
    
    def _init_tools(self) -> List:
        """初始化工具"""
        return [
            get_hotspot_info,
            get_product_info,
            get_analysis_report_info,
        ]
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位资深短视频编导，擅长创作引流短视频脚本。
你需要：
1. 结合热点话题和商品特性
2. 运用爆款技巧和公式
3. 生成高质量的拍摄脚本和分镜
4. 提供制作要点建议

脚本要求：
- 时长控制在5-15秒
- 内容简洁有力，能够吸引用户点击进入直播间
- 突出商品卖点和价格优惠
- 适合对应类目直播间风格
- 包含完整的分镜表格（镜头编号、时间区间、景别、画面内容、台词、动作、音乐、作用、塑造点）

请以JSON格式返回结果。"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行脚本生成
        
        Args:
            input_data: 包含以下字段：
                - hotspot_id: 热点ID
                - product_id: 商品ID
                - analysis_report_id: 拆解报告ID（可选）
                - duration: 视频时长（秒），默认10秒
                - adjustment_feedback: 调整意见（可选，用于重新生成）
                - script_index: 脚本序号（1-5），用于生成不同版本的脚本
                - total_scripts: 总脚本数量，默认5个
        
        Returns:
            包含以下字段的字典：
                - video_info: 视频基本信息
                - script_content: 脚本内容
                - shot_list: 分镜列表
                - production_notes: 制作要点
                - tags: 推荐标签和话题
        """
        hotspot_id = input_data.get("hotspot_id")
        product_id = input_data.get("product_id")
        analysis_report_id = input_data.get("analysis_report_id")
        duration = input_data.get("duration", 10)
        adjustment_feedback = input_data.get("adjustment_feedback")
        script_index = input_data.get("script_index", 1)
        total_scripts = input_data.get("total_scripts", 5)
        
        if not hotspot_id or not product_id:
            raise ValueError("hotspot_id和product_id不能为空")
        
        logger.info(f"开始生成脚本: 热点={hotspot_id}, 商品={product_id}, 时长={duration}秒, 脚本序号={script_index}/{total_scripts}")
        
        # 1. 获取热点信息
        hotspot_info = get_hotspot_info(hotspot_id)
        if "error" in hotspot_info:
            raise ValueError(f"获取热点信息失败: {hotspot_info['error']}")
        
        # 2. 获取商品信息
        product_info = get_product_info(product_id)
        if "error" in product_info:
            raise ValueError(f"获取商品信息失败: {product_info['error']}")
        
        # 3. 获取拆解报告（如果提供）
        analysis_info = None
        if analysis_report_id:
            analysis_info = get_analysis_report_info(analysis_report_id)
        
        # 4. 构建提示词
        prompt = self._build_prompt(hotspot_info, product_info, analysis_info, duration, adjustment_feedback, script_index, total_scripts)
        
        # 5. 调用LLM生成脚本
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 6. 解析响应
            script_data = self._parse_response(content)
            
            logger.info("脚本生成成功")
            return script_data
            
        except Exception as e:
            logger.error(f"脚本生成失败: {e}")
            raise
    
    def _build_prompt(
        self,
        hotspot_info: Dict[str, Any],
        product_info: Dict[str, Any],
        analysis_info: Optional[Dict[str, Any]],
        duration: int,
        adjustment_feedback: Optional[str] = None,
        script_index: int = 1,
        total_scripts: int = 5
    ) -> str:
        """构建提示词，支持生成多个不同版本的脚本"""
        
        # 添加多样性提示
        diversity_note = ""
        if total_scripts > 1:
            diversity_note = f"""
【重要提示 - 脚本多样性要求】
这是第 {script_index} 个脚本（共 {total_scripts} 个）。请确保这个脚本与之前的脚本有明显不同：

1. **不同的切入角度**：
   - 脚本{script_index}可以使用：{"疑问式开场" if script_index == 1 else "对比式开场" if script_index == 2 else "故事化开场" if script_index == 3 else "数据化开场" if script_index == 4 else "情感化开场"}
   - 采用不同的叙事结构

2. **不同的卖点突出**：
   - 可以侧重不同的商品卖点
   - 使用不同的表达方式

3. **不同的创意元素**：
   - 使用不同的镜头语言
   - 采用不同的节奏感
   - 突出不同的情感点

4. **确保独特性**：
   - 每个脚本都应该有独特的创意点
   - 避免重复的表达方式和结构
"""
        
        prompt = f"""请为以下热点和商品生成一个{duration}秒的引流短视频脚本。
{diversity_note}

【热点信息】
标题：{hotspot_info.get('title', '')}
标签：{', '.join(hotspot_info.get('tags', []))}
URL：{hotspot_info.get('url', '')}
热度：{hotspot_info.get('heat_score', 0)}
匹配度：{hotspot_info.get('match_score', 0):.2f}

【商品信息】
名称：{product_info.get('name', '')}
品牌：{product_info.get('brand', '无')}
品类：{product_info.get('category', '')}
核心卖点：
"""
        
        for point in product_info.get('selling_points', []):
            prompt += f"- {point}\n"
        
        prompt += f"""价格：{product_info.get('price', 0)}元
商品描述：{product_info.get('description', '无')}
说明手卡：{product_info.get('hand_card', '无')}
"""
        
        # 添加拆解报告信息
        if analysis_info:
            prompt += "\n【爆款技巧】\n"
            viral_formula = analysis_info.get('viral_formula', {})
            if viral_formula.get('formula_name'):
                prompt += f"爆款公式：{viral_formula.get('formula_name')}\n"
                prompt += f"公式结构：{viral_formula.get('formula_structure', '')}\n"
            
            production_tips = analysis_info.get('production_tips', {})
            if production_tips.get('shooting_tips'):
                prompt += "拍摄要点：\n"
                for tip in production_tips['shooting_tips']:
                    prompt += f"- {tip}\n"
        
        # 如果有调整意见，添加到要求中
        if adjustment_feedback:
            prompt += f"\n【调整意见】\n{adjustment_feedback}\n"
        
        prompt += f"""
【要求】
1. 视频时长：{duration}秒（5-15秒之间）
2. 结合热点话题和商品特性
3. 运用上述爆款技巧和公式
4. 突出商品卖点和价格优惠
5. 适合{product_info.get('category', '')}直播间风格
6. 内容要吸引人，能够引导用户进入直播间
7. {"请确保这个脚本与之前的脚本有明显不同，使用独特的创意角度和表达方式" if total_scripts > 1 else ""}

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
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析LLM返回的内容"""
        import json
        import re
        
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                script_data = json.loads(json_str)
            else:
                # 如果没有JSON，尝试手动构建
                script_data = self._build_default_script(content)
            
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
            return self._build_default_script(content)
    
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

