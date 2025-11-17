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
        return """你是一位资深**直播间引流短视频编导**，擅长创作**真实、直接、有紧迫感**的直播间引流短视频脚本。

你的核心能力：
1. **创作真实、自然的直播间话术**，而不是"硬编出来的广告"
2. **直接传递商品价值**，避免过度渲染情感（避免"虚头巴脑的共情话术"）
3. 结合热点话题和商品特性，创造独特的创意角度
4. 运用直播间常用话术和技巧，确保脚本有爆款潜力

脚本要求：
- 时长控制在5-15秒
- **必须是直播间引流短视频风格，不是传统广告**
- **台词要真实、自然、口语化，不能像"硬编出来的广告"**
- **必须直接传递商品卖点和价格优势，让用户知道"这个商品能解决什么问题"**
- **必须包含直播间特色**：紧迫感（限时、限量、限价）、互动感（"家人们"、"姐妹们"等）
- 适合对应类目直播间风格
- 包含完整的分镜表格（镜头编号、时间区间、景别、画面内容、台词、动作、音乐、作用、塑造点）

**直播间引流短视频 vs 传统广告的区别**：
- ❌ **传统广告**：完整故事线、精心设计的台词、结构完整、更像"作品"
- ✅ **直播间引流短视频**：直接、真实、口语化、有紧迫感、有互动感、更快节奏、更像"真实场景"

台词质量标准（根据品类调整）：
- **女装/快消品（如199元派克服）**：
  - ✅ 好："家人们，这个199元的派克服真的绝了！零下10度都不怕，现在进直播间，限时优惠！"
  - ✅ 好："这个冬天最值得买的派克服，199元，保暖度不输大牌，现在进直播间！"
  - ❌ 差："为什么追个剧还要被冻哭?"（太"编"，不像真实话术）
  - ❌ 差："看着孩子穿着单薄的校服在雪地里跑，我的心都揪起来了"（太虚，没有直接指向商品）
  
- **高端/情感类商品**：
  - ✅ 好："凌晨3点，终于可以躺下。智能床让我每天醒来都像换了张床，现在进直播间！"
  - ❌ 差："这个产品很好用"（空洞，无说服力）

核心原则：
- **必须真实、自然**：不能像"硬编出来的广告"，要像真实的直播间话术
- **必须直接传递商品价值**：价格、功能、性价比、效果
- **必须包含直播间特色**：紧迫感、互动感、行动引导
- **避免过度"内容化"**：不要只是渲染情感，必须明确告诉用户商品能解决什么问题
- **避免传统广告风格**：不要完整的故事线，要更直接、更快节奏

**⚠️ 重要：信息传递 > 场景渲染**
- **电商短视频（尤其是直播间引流）的重点是信息传递，不是场景、音乐、动作表情**
- ✅ **优先传递信息**：价格、功能、效果、性价比、优惠
- ❌ **不要过度渲染**：场景描述、音乐要求、动作表情、情感渲染
- **分镜表格中的"画面内容"、"动作"、"音乐"应该简洁，重点是"台词"中的信息传递**

**📐 直播间引流短视频核心框架方向（不是模板，是方向）**：

**框架1：时间结构方向**
- **前5秒（吸引注意）**：必须包含价格/福利噱头、核心卖点、冲突性提问或引人入胜的画面
- **中间部分（引导互动与成交）**：展示产品功能、使用效果、解决消费痛点、建立信任
- **结尾（引导进入直播间）**：明确的行动号召（CTA），如"点击进入直播间"、"直播间等你"等

**框架2：内容分层方向**
- **60%信息传递**：产品功能、效果、价格、优惠等核心信息（建立信任+激发需求）
- **30%产品展示**：产品使用场景、效果展示（激发需求）
- **10%促销引导**：优惠信息、直播间引导（促成转化）

**框架3：信息传递方向**
- **必须包含的核心信息**：
  1. **价格信息**：明确的价格数字（如"199元"）
  2. **功能信息**：产品核心功能（如"三防面料"、"透气科技"）
  3. **效果信息**：具体效果数据（如"零下10度不怕"、"透气性强3倍"）
  4. **优惠信息**：限时优惠、特价等（如"限时优惠"、"错过等一年"）
  5. **直播间引导**：明确的行动号召（如"现在进直播间"、"点击进入"）

**框架4：黄金三秒法则方向**
- **开头3秒**：必须吸引注意力
  - ✅ 价格冲击（如"199元"）
  - ✅ 冲突性提问（如"零下10度，95%的人还在瑟瑟发抖..."）
  - ✅ 核心卖点（如"三防面料+透气科技"）
  - ❌ 不要冗长的场景铺垫

**框架5：节奏控制方向**
- **紧凑节奏**：避免冗长铺垫，快速传递核心信息
- **信息密度**：每个镜头都应该传递有价值的信息
- **简洁表达**：场景、音乐、动作应该简洁，重点是台词中的信息传递

**⚠️ 重要提示**：
- 这些是**方向框架**，不是固定模板
- 可以根据具体热点和商品特性，灵活运用这些方向
- 但必须确保：信息传递充分、场景渲染简洁、直播间引导明确

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
        
        # 1. 获取热点信息（添加验证日志）
        hotspot_info = get_hotspot_info(hotspot_id)
        if "error" in hotspot_info:
            raise ValueError(f"获取热点信息失败: {hotspot_info['error']}")
        
        # 验证热点ID匹配（防止热点选择错误）
        if hotspot_info.get('id') != hotspot_id:
            raise ValueError(f"热点ID不匹配: 期望={hotspot_id}, 实际={hotspot_info.get('id')}")
        
        logger.info(f"✅ Agent验证: 热点ID={hotspot_id}, 标题={hotspot_info.get('title', '')}")
        
        # 2. 获取商品信息（添加验证日志）
        product_info = get_product_info(product_id)
        if "error" in product_info:
            raise ValueError(f"获取商品信息失败: {product_info['error']}")
        
        # 验证商品ID匹配
        if product_info.get('id') != product_id:
            raise ValueError(f"商品ID不匹配: 期望={product_id}, 实际={product_info.get('id')}")
        
        logger.info(f"✅ Agent验证: 商品ID={product_id}, 名称={product_info.get('name', '')}")
        
        # 3. 获取拆解报告（如果提供）
        analysis_info = None
        if analysis_report_id:
            analysis_info = get_analysis_report_info(analysis_report_id)
        
        # 4. 构建提示词
        prompt = self._build_prompt(hotspot_info, product_info, analysis_info, duration, adjustment_feedback, script_index, total_scripts)
        
        # 5. 调用LLM生成脚本（使用不同的temperature确保多样性）
        try:
            # 根据脚本序号调整temperature，确保每个脚本都有不同的创意
            # script_index=1: 0.7, script_index=2: 0.8, script_index=3: 0.9, script_index=4: 0.75, script_index=5: 0.85
            temperature_map = {1: 0.7, 2: 0.8, 3: 0.9, 4: 0.75, 5: 0.85}
            temperature = temperature_map.get(script_index, 0.8)
            
            logger.info(f"使用temperature={temperature}生成脚本{script_index}/{total_scripts}，确保多样性")
            
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                temperature=temperature,  # 使用不同的temperature确保多样性
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
        
        # 添加多样性提示（增强版）
        diversity_note = ""
        if total_scripts > 1:
            # 定义不同脚本的开场方式和叙事结构
            opening_styles = {
                1: "疑问式开场（提出问题，引发思考）",
                2: "对比式开场（对比差异，制造冲突）",
                3: "故事化开场（讲述故事，情感共鸣）",
                4: "数据化开场（用数据说话，增强说服力）",
                5: "情感化开场（直击情感，引发共鸣）"
            }
            
            narrative_structures = {
                1: "问题-解决方案结构",
                2: "对比-优势结构",
                3: "故事-启示结构",
                4: "数据-证明结构",
                5: "情感-共鸣结构"
            }
            
            diversity_note = f"""
【⚠️ 重要提示 - 脚本多样性要求（必须严格遵守）】
这是第 {script_index} 个脚本（共 {total_scripts} 个）。**必须确保这个脚本与之前的脚本完全不同**：

1. **强制使用不同的切入角度**：
   - 脚本{script_index}必须使用：{opening_styles.get(script_index, "独特开场方式")}
   - 必须采用：{narrative_structures.get(script_index, "独特叙事结构")}
   - **禁止**使用与之前脚本相同的开场方式

2. **强制使用不同的卖点突出**：
   - 必须侧重不同的商品卖点（如果脚本1突出价格，脚本2必须突出功能）
   - 必须使用完全不同的表达方式和话术
   - **禁止**重复之前的卖点表达

3. **强制使用不同的创意元素**：
   - 必须使用不同的镜头语言和视觉呈现
   - 必须采用不同的节奏感（快节奏/慢节奏/起伏节奏）
   - 必须突出不同的情感点（兴奋/温馨/紧张/轻松等）
   - **禁止**使用相同的创意元素

4. **确保独特性**：
   - 每个脚本都必须有独特的创意点和记忆点
   - **绝对禁止**重复之前的表达方式、结构、台词
   - 如果生成的内容与之前的脚本相似，必须重新生成

5. **台词差异化**：
   - 每个脚本的台词必须完全不同
   - 不能只是简单的词语替换，必须是完全不同的表达
   - 每个脚本的台词风格也要不同（正式/轻松/幽默/专业等）
"""
        
        # 提取ContentAnalysisAgent的分析结果（关键！）
        content_analysis = hotspot_info.get('content_analysis')
        video_structure = hotspot_info.get('video_structure')
        content_compact = hotspot_info.get('content_compact')
        
        # 构建热点分析信息（如果有）
        hotspot_analysis_section = ""
        if content_analysis:
            ecommerce_fit = content_analysis.get('ecommerce_fit', {})
            applicable_categories = ecommerce_fit.get('applicable_categories', [])
            ecommerce_score = ecommerce_fit.get('score', 0)
            
            hotspot_analysis_section = f"""
【⚠️ 热点内容分析（ContentAnalysisAgent结果 - 非常重要）】
这是ContentAnalysisAgent对热点内容的深度分析，**必须充分利用这些信息**：

1. **内容摘要**：{content_analysis.get('summary', '无')}
2. **视频风格**：{content_analysis.get('style', '无')}
3. **电商适配性评分**：{ecommerce_score:.2f}（0-1分，越高越适合电商）
4. **适用类目**：{', '.join(applicable_categories) if applicable_categories else '无'}
5. **适配原因**：{ecommerce_fit.get('reasoning', '无')}

**重要提示**：
- 如果适用类目中包含商品品类"{product_info.get('category', '')}"，说明这个热点确实适合这个商品，**必须充分利用这个关联**
- 如果适用类目不包含商品品类，需要**创造性地建立关联**，但不能强行关联
- 电商适配性评分可以帮助判断热点与商品的匹配程度
"""
        
        # 构建视频结构信息（如果有）
        video_structure_section = ""
        if video_structure:
            script_structure = video_structure.get('script_structure', {})
            if script_structure:
                video_structure_section = f"""
【⚠️ 热点视频结构分析（StructureAgent结果 - 重要参考）】
这是StructureAgent对热点视频结构的分析，**可以参考其结构设计**：

1. **Hook（开头钩子）**：{script_structure.get('hook', '无')}
2. **Body（主体内容）**：{script_structure.get('body', '无')}
3. **CTA（行动号召）**：{script_structure.get('cta', '无')}

**参考建议**：
- 可以参考热点视频的hook设计，但必须结合商品特性
- 可以参考热点视频的body结构，但必须突出商品价值
- 必须有自己的CTA，引导用户进入直播间
"""
        
        prompt = f"""请为以下热点和商品生成一个{duration}秒的**直播间引流短视频脚本**（不是传统广告）。

**⚠️ 重要：这是直播间引流短视频，不是传统广告！**
- 必须真实、自然、口语化，不能像"硬编出来的广告"
- 必须包含直播间特色：紧迫感、互动感、行动引导
- 不要完整的故事线，要更直接、更快节奏
- 使用直播间常用话术（"家人们"、"姐妹们"、"真的绝了"、"现在进直播间"等）

**📐 必须遵循核心框架方向**：

**1. 时间结构方向**：
- **前5秒（或前30%）**：必须包含价格/福利噱头、核心卖点、冲突性提问或引人入胜的画面
- **中间部分（60-70%）**：展示产品功能、使用效果、解决消费痛点、建立信任
- **结尾（最后20-30%）**：明确的行动号召（CTA），如"点击进入直播间"、"直播间等你"等

**2. 内容分层方向**：
- **60%信息传递**：产品功能、效果、价格、优惠等核心信息（建立信任+激发需求）
- **30%产品展示**：产品使用场景、效果展示（激发需求）
- **10%促销引导**：优惠信息、直播间引导（促成转化）

**3. 信息传递方向**：
- **必须包含的核心信息**：
  1. **价格信息**：明确的价格数字（如"199元"）
  2. **功能信息**：产品核心功能（如"三防面料"、"透气科技"）
  3. **效果信息**：具体效果数据（如"零下10度不怕"、"透气性强3倍"）
  4. **优惠信息**：限时优惠、特价等（如"限时优惠"、"错过等一年"）
  5. **直播间引导**：明确的行动号召（如"现在进直播间"、"点击进入"）

**4. 黄金三秒法则方向**：
- **开头3秒**：必须吸引注意力
  - ✅ 价格冲击（如"199元"）
  - ✅ 冲突性提问（如"零下10度，95%的人还在瑟瑟发抖..."）
  - ✅ 核心卖点（如"三防面料+透气科技"）
  - ❌ 不要冗长的场景铺垫

**5. 节奏控制方向**：
- **紧凑节奏**：避免冗长铺垫，快速传递核心信息
- **信息密度**：每个镜头都应该传递有价值的信息
- **简洁表达**：场景、音乐、动作应该简洁，重点是台词中的信息传递

{diversity_note}

【热点信息】
标题：{hotspot_info.get('title', '')}
标签：{', '.join(hotspot_info.get('tags', []))}
URL：{hotspot_info.get('url', '')}
热度：{hotspot_info.get('heat_score', 0)}
匹配度：{hotspot_info.get('match_score', 0):.2f}
内容摘要：{content_compact or '无'}
{hotspot_analysis_section}
{video_structure_section}

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
        
        # 根据品类确定策略
        category = product_info.get('category', '')
        price = product_info.get('price', 0)
        
        # 判断是否为快消品/女装类（需要更直接的策略）
        fast_consumption_categories = ['女装', '男装', '童装', '鞋靴', '箱包', '配饰']
        is_fast_consumption = any(cat in category for cat in fast_consumption_categories) or price < 500
        
        category_strategy = ""
        if is_fast_consumption:
            category_strategy = f"""
**⚠️ 品类策略（{category}，价格{price}元）**：
这是快消品/女装类商品，必须采用**直接商品化策略**：
1. **必须直接传递商品价值**：价格、功能、性价比、效果
2. **避免过度"内容化"**：不要只是渲染情感（如"看着孩子...我的心都揪起来了"），必须明确告诉用户商品能解决什么问题
3. **前3秒必须与商品直接相关**：可以是价格冲击、功能展示、效果对比，但不能只是"虚头巴脑的共情话术"
4. **最后3秒必须引导行动**：明确告诉用户"点击进入直播间"、"限时优惠{price}元"等
"""
        else:
            category_strategy = f"""
**⚠️ 品类策略（{category}，价格{price}元）**：
这是高端/功能性商品，可以**平衡内容化和商品化**：
1. 可以有场景和情感，但必须最终指向商品价值
2. 强调功能、效果、体验，但要用具体的方式表达
3. 前3秒可以建立场景，但必须与商品相关
4. 最后3秒必须引导行动
"""
        
        prompt += f"""
【要求】
1. 视频时长：{duration}秒（5-15秒之间）
2. 结合热点话题和商品特性，**必须建立明确的关联**（不能只是简单提到热点）
3. 运用上述爆款技巧和公式
4. **必须直接传递商品卖点和价格优惠**，让用户知道"这个商品能解决什么问题"
5. 适合{category}直播间风格
6. 内容要吸引人，能够引导用户进入直播间
7. {"请确保这个脚本与之前的脚本有明显不同，使用独特的创意角度和表达方式" if total_scripts > 1 else ""}
{category_strategy}
"""
        
        # 如果有调整意见，必须优先考虑（放在要求之后，更突出）
        if adjustment_feedback:
            prompt += f"""

【⚠️ 重要：调整意见（必须严格遵守）】
这是用户对当前脚本的调整意见，**必须严格按照以下要求进行修改**：

{adjustment_feedback}

**重要提示**：
1. 上述调整意见是用户明确提出的修改要求，必须完全遵守
2. 如果调整意见与前面的要求有冲突，以调整意见为准
3. 生成的脚本必须体现出调整意见中的所有要求
4. 不要忽略或遗漏调整意见中的任何一点

"""
        
        prompt += f"""
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
            "content": "画面内容描述（简洁，重点是信息传递）",
            "dialogue": "台词（必须包含核心信息：价格、功能、效果、优惠、直播间引导）",
            "action": "动作（简洁，不要过度渲染）",
            "music": "音乐要求（简洁，不要过度渲染）",
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

【⚠️ 台词质量要求（非常重要 - 根据品类调整）】

**核心原则：必须直接传递商品价值，避免"虚头巴脑的共情话术"**

根据商品品类 {category}，调整策略：

**1. 女装/快消品（如199元派克服、T恤、裤子等）**：
   - ✅ **必须直接**：强调价格、功能、性价比
   - ✅ 好："199元派克服，零下10度也不怕！保暖又好看，限时优惠"
   - ✅ 好："这个冬天最值得买的派克服，199元，保暖度不输大牌"
   - ❌ 差："看着孩子穿着单薄的校服在雪地里跑，我的心都揪起来了"（太虚，没有直接指向商品）
   - ❌ 差："天气冷了，妈妈们都在担心孩子"（过度内容化，没有商品价值）

**2. 家居/功能性商品（如智能床、按摩椅等）**：
   - ✅ **平衡内容化和商品化**：可以有场景和情感，但必须指向商品价值
   - ✅ 好："凌晨3点，终于可以躺下。智能床让我每天醒来都像换了张床"
   - ✅ 好："用了3个月，每天醒来都像换了张床。智能床，真的值得"
   - ❌ 差："运动后需要极致放松"（太简单，无吸引力，也没有指向商品）

**3. 美妆/护肤（如面膜、精华等）**：
   - ✅ **强调效果和价格**：直接告诉用户能解决什么问题
   - ✅ 好："这个面膜用了3天，皮肤真的变好了！现在限时99元"
   - ❌ 差："每个女人都想要好皮肤"（太虚，没有指向商品）

**通用要求**：
1. **必须是直播间引流短视频风格，不是传统广告**：
   - ✅ 真实、自然、口语化（"家人们"、"姐妹们"、"真的绝了"等）
   - ✅ 有紧迫感（"限时"、"限量"、"现在进直播间"等）
   - ✅ 有互动感（"家人们"、"姐妹们"、"你们觉得呢"等）
   - ❌ 不要完整的故事线（不要像"追剧→冷→穿派克服"这样的完整故事）
   - ❌ 不要"硬编出来的广告"（不要像"为什么追个剧还要被冻哭?"这样编出来的场景）

2. **⚠️ 信息传递 > 场景渲染（非常重要）**：
   - **电商短视频（尤其是直播间引流）的重点是信息传递，不是场景、音乐、动作表情**
   - ✅ **优先传递信息**：价格、功能、效果、性价比、优惠（这些信息必须在台词中明确传递）
   - ❌ **不要过度渲染**：场景描述（如"深夜地铁站，女主角疲惫地走出地铁，寒风吹起她的发丝"）、音乐要求（如"轻柔略带忧伤的钢琴前奏"）、动作表情（如"缩着肩膀，快步走出"）
   - **分镜表格中的"画面内容"、"动作"、"音乐"应该简洁，重点是"台词"中的信息传递**
   - **台词必须包含核心信息**：价格、功能、效果、优惠、直播间引导

3. **必须直接传递商品价值**：价格、功能、效果、性价比
   - 前3秒必须直接展示商品或价格（不能只是渲染情感）
   - 必须明确告诉用户"这个商品能解决什么问题"
   - **台词中必须包含具体信息**：价格数字、功能特点、效果数据、优惠信息

4. **必须包含直播间特色**：
   - 使用直播间常用话术（"家人们"、"姐妹们"、"真的绝了"、"现在进直播间"等）
   - 有紧迫感（"限时"、"限量"、"限价"等）
   - 最后3秒必须引导行动（"现在进直播间"、"限时优惠"等）

5. **避免传统广告风格**：
   - ❌ 不要完整的故事线（起承转合）
   - ❌ 不要"硬编出来的场景"（如"为什么追个剧还要被冻哭?"）
   - ❌ 不要过度渲染情感（如"看着孩子...我的心都揪起来了"）
   - ❌ **不要过度渲染场景、音乐、动作表情**（这些应该简洁，重点是信息传递）
   - ✅ 要更直接、更快节奏、更真实

**差异化要求**：
- 每个脚本的台词风格必须不同
- 不能只是简单的词语替换
- 要有完全不同的表达方式，但都必须：
  - 真实、自然、口语化
  - 直接指向商品价值
  - 包含直播间特色

请确保：
- shot_list中的镜头数量合理，总时长不超过{duration}秒
- 每个镜头都有明确的时间区间
- **台词必须真实、自然、口语化，不能像"硬编出来的广告"**
- **必须包含直播间特色**：紧迫感、互动感、行动引导
- **必须直接传递商品价值**：价格、功能、性价比
- **⚠️ 信息传递 > 场景渲染**：
  - **台词必须包含核心信息**：价格数字、功能特点、效果数据、优惠信息、直播间引导
  - **画面内容、动作、音乐应该简洁**，不要过度渲染场景、情感、氛围
  - **重点是信息传递，不是场景渲染**
- 标签和话题要与内容匹配

**⚠️ 再次强调：这是直播间引流短视频，不是传统广告！**
- 不要完整的故事线（如"追剧→冷→穿派克服"）
- 不要"硬编出来的场景"（如"为什么追个剧还要被冻哭?"）
- 不要过度渲染场景、音乐、动作表情（这些应该简洁，重点是信息传递）
- 要真实、自然、口语化，像真实的直播间话术
- 要直接、快速、有紧迫感
- 要包含直播间常用话术（"家人们"、"姐妹们"、"真的绝了"、"现在进直播间"等）
- **信息传递 > 场景渲染**：台词中必须包含价格、功能、效果、优惠等核心信息
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

