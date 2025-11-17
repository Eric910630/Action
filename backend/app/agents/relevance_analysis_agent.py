"""
关联度分析Agent
负责分析热点与商品/直播间的关联度
"""
import json
from typing import Dict, Any, List
from loguru import logger
from app.agents.base import BaseAgent
from app.tools.analysis_tools import calculate_semantic_similarity, analyze_sentiment
from app.tools.websearch_tools import web_search, search_endorsements
from app.services.config.live_room_config import LiveRoomConfigService


class RelevanceAnalysisAgent(BaseAgent):
    """关联度分析Agent（增强版：支持配置文件）"""
    
    def __init__(self, model_name: str = "deepseek-chat", api_key: str = None):
        """初始化Agent"""
        super().__init__(model_name, api_key)
        self.config_service = LiveRoomConfigService()
    
    def _init_tools(self) -> List:
        """初始化工具"""
        return [
            calculate_semantic_similarity,
            analyze_sentiment,
            web_search,
            search_endorsements,
        ]
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """# 角色
你是一位专业的电商内容分析专家，拥有以下专业能力：
- 10年+电商运营与内容营销经验
- 深度热点趋势洞察能力
- 精准匹配度分析专长
- 直播间/商品定位理解能力

## 分析准则
DEPTH: 从表面关联到深层语义，挖掘真实匹配价值
LOGIC: 建立清晰的匹配逻辑链条，确保评估客观准确
PRACTICE: 提供可执行的匹配建议和优化方向

## 约束条件
1. 匹配度评估必须基于客观事实，避免主观臆断
2. 每个匹配度分数都要有具体的支撑证据
3. 分析结果要具备实际应用指导价值
4. 保持专业术语的准确性和一致性
5. 匹配度计算要达到可解释、可复现的程度

## 分析框架
### 语义相似度分析（权重60%）
- **主题相关性**：核心主题是否匹配、话题领域是否一致、概念关联度分析
- **关键词重叠**：直接关键词匹配、同义词/近义词匹配、相关概念匹配
- **上下文相似度**：使用场景匹配度、目标受众重叠度、价值主张一致性

### 情感匹配度分析（权重30%）
- **情感倾向**：正面/中性/负面情感识别、情感强度评估、情感一致性判断
- **品牌调性匹配**：热点情感与直播间定位的契合度、是否适合推广商品、是否存在品牌风险
- **情感共鸣度**：能否引发目标受众共鸣、情感触发点识别、情绪转化潜力

### 关键词匹配分析（权重10%）
- **直接匹配**：直播间关键词在热点中的出现、类目关键词匹配、品牌/产品词匹配
- **语义匹配**：同义词匹配、相关概念匹配、上下位关系匹配
- **类目匹配**：一级类目匹配度、二级类目匹配度、跨类目关联度

## 匹配度评分标准
- **0.8-1.0**：高度相关，强烈推荐（主题高度一致、关键词大量重叠、情感完全匹配、适用类目匹配）
- **0.6-0.8**：相关，推荐（主题基本一致、关键词部分重叠、情感基本匹配、适用类目基本匹配）
- **0.4-0.6**：部分相关，可考虑（主题有一定关联、关键词少量重叠、情感需要调整、适用类目可能匹配）
- **0.2-0.4**：相关性较低（主题关联度弱、关键词几乎无重叠、情感不匹配、适用类目不匹配）
- **0.0-0.2**：不相关，不推荐（主题完全不相关、无关键词重叠、情感冲突、适用类目完全不匹配）

## ⚠️ 重要：适用类目匹配检查
在计算匹配度之前，**必须检查ContentAnalysisAgent识别的适用类目是否与直播间类目匹配**：
1. **如果适用类目与直播间类目完全不匹配**（如"汽车"vs"家居"、"运动鞋服"vs"女装"）：
   - 即使主题有一定关联，也应该大幅降低匹配度（不超过0.4）
   - 如果主题完全不相关，应该直接返回0.2以下
2. **如果适用类目与直播间类目匹配**：
   - 可以正常计算匹配度
   - 适用类目匹配是重要的加分项
3. **避免误匹配**：
   - "家电"不应该匹配"家居家装"（虽然都包含"家"，但类目不同）
   - "运动鞋服"不应该匹配"女装"（虽然都包含"服"，但目标群体不同）
   - "奢侈品"不应该匹配"快消品"（虽然都是商品，但定位完全不同）

## 综合匹配度计算
- 语义关联度权重：60%（主题相关性30% + 关键词重叠20% + 上下文相似度10%）
- 情感匹配度权重：30%（情感倾向匹配15% + 品牌调性匹配10% + 情感共鸣度5%）
- 关键词匹配权重：10%（直接匹配5% + 语义匹配3% + 类目匹配2%）

## 执行要求
1. 使用提供的工具函数计算语义相似度和情感分析
2. **如果热点涉及知名人物（运动员、艺人、明星等），使用web_search或search_endorsements工具查找其代言和品牌信息**
3. **如果发现相关代言或品牌，将其作为额外的匹配依据，提升匹配度评分**
4. 基于计算结果进行深度分析，提供匹配原因和改进建议
5. 确保每个分数都有具体证据支撑
6. 识别强匹配点和弱匹配点
7. 评估应用场景和潜在风险

## 代言和品牌信息查找
当热点涉及以下情况时，应该使用web_search或search_endorsements工具：
- **运动员**：查找其代言的运动品牌、装备品牌等
- **艺人/明星**：查找其代言的化妆品、服装、电子产品等品牌
- **综艺节目**：查找节目的赞助商、合作品牌等
- **其他知名人物**：查找其相关的商业合作和品牌露出

**使用方法**：
- 使用`search_endorsements(person_name, category)`查找特定人物的代言信息
- 使用`web_search(query)`进行更广泛的搜索
- 将找到的品牌信息与直播间类目进行匹配，如果匹配则提升匹配度

请根据提供的工具函数计算结果，给出准确、专业的匹配度评估，并提供详细的分析报告。"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行关联度分析（增强版：支持完整内容包和直播间画像）
        
        Args:
            input_data: 包含以下字段（兼容旧版本和新版本）：
                # 旧版本字段（向后兼容）
                - hotspot_text: 热点文本
                - product_text: 商品文本
                - hotspot_tags: 热点标签（可选）
                - product_category: 商品类目（可选）
                # 新版本字段（优先使用）
                - content_package: 完整内容包（包含video_structure, content_analysis等）
                - live_room_name: 直播间名称（用于加载配置文件）
                - live_room_id: 直播间ID（可选，用于从数据库获取）
        
        Returns:
            包含以下字段的字典：
                - relevance_score: 关联度分数 (0-1)
                - semantic_score: 语义相似度分数
                - sentiment_score: 情感匹配度分数
                - analysis: 分析报告文本
        """
        # 检查是否使用新版本（完整内容包）
        content_package = input_data.get("content_package")
        live_room_name = input_data.get("live_room_name")
        
        if content_package and live_room_name:
            # 使用新版本：完整内容包 + 直播间画像
            return await self._execute_with_content_package(content_package, live_room_name)
        else:
            # 使用旧版本：向后兼容
            return await self._execute_legacy(input_data)
    
    async def _execute_with_content_package(
        self,
        content_package: Dict[str, Any],
        live_room_name: str
    ) -> Dict[str, Any]:
        """使用完整内容包和直播间画像进行分析"""
        import time
        start_time = time.time()
        
        logger.info(f"🔍 [匹配Agent] 开始匹配分析 - 直播间: {live_room_name}")
        logger.debug(f"🔍 [匹配Agent] 输入参数: live_room_name={live_room_name}")
        
        try:
            # 1. 加载直播间配置
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤1: 加载直播间配置")
            live_room_profile = self.config_service.get_live_room_profile(live_room_name)
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤1完成: 直播间配置加载成功, 耗时 {step_time:.2f}秒")
            logger.debug(f"🔍 [匹配Agent] 直播间画像长度: {len(live_room_profile)}")
            
            # 2. 提取热点信息
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤2: 提取热点信息")
            title = content_package.get("title", "")
            content_analysis = content_package.get("content_analysis", {})
            video_structure = content_package.get("video_structure", {})
            
            summary = content_analysis.get("summary", "")
            style = content_analysis.get("style", "")
            ecommerce_fit = content_analysis.get("ecommerce_fit", {})
            ecommerce_score = ecommerce_fit.get("score", 0.0)
            
            logger.debug(f"🔍 [匹配Agent] 热点标题: {title[:50] if title else 'N/A'}")
            logger.debug(f"🔍 [匹配Agent] 内容摘要长度: {len(summary)}")
            logger.debug(f"🔍 [匹配Agent] 视频风格: {style}")
            logger.debug(f"🔍 [匹配Agent] 电商适配性评分: {ecommerce_score}")
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤2完成: 热点信息提取成功, 耗时 {step_time:.2f}秒")
            
            # 3. 查找代言和品牌信息（如果热点涉及知名人物）
            endorsement_info = None
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤3: 查找代言和品牌信息")
            
            # 尝试从标题中提取人物名称（简单实现，可以优化）
            # 如果标题包含常见的人物关键词，尝试搜索代言信息
            person_keywords = ["王楚钦", "林高远", "樊振东", "何杰", "张伟丽"]  # 可以扩展
            detected_person = None
            for keyword in person_keywords:
                if keyword in title:
                    detected_person = keyword
                    break
            
            if detected_person:
                try:
                    logger.info(f"🔍 [匹配Agent] 检测到人物: {detected_person}，查找代言信息")
                    # 获取直播间类目用于过滤
                    category = live_room_profile.split("类目：")[1].split("\n")[0] if "类目：" in live_room_profile else None
                    endorsement_info = search_endorsements(detected_person, category)
                    logger.info(f"✅ [匹配Agent] 找到 {endorsement_info.get('total', 0)} 条代言信息")
                except Exception as e:
                    logger.warning(f"⚠️  [匹配Agent] 查找代言信息失败: {e}")
            else:
                logger.debug(f"🔍 [匹配Agent] 未检测到知名人物，跳过代言搜索")
            
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤3完成: 代言信息查找完成, 耗时 {step_time:.2f}秒")
            
            # 4. 构建匹配提示词（包含代言信息）
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤4: 构建匹配分析提示词")
            
            endorsement_text = ""
            if endorsement_info and endorsement_info.get("total", 0) > 0:
                endorsements = endorsement_info.get("endorsements", [])
                endorsement_text = "\n\n**代言和品牌信息**：\n"
                for i, endo in enumerate(endorsements[:3], 1):  # 只显示前3条
                    endorsement_text += f"{i}. {endo.get('title', '')}\n   {endo.get('snippet', '')[:200]}...\n"
                endorsement_text += "\n**重要**：如果找到的代言品牌与直播间类目匹配，应该提升匹配度评分。"
            
            # 提取适用类目信息
            applicable_categories = ecommerce_fit.get("applicable_categories", [])
            applicable_categories_text = ""
            if applicable_categories:
                applicable_categories_text = f"\n- **适用类目**（ContentAnalysisAgent识别）：{', '.join(applicable_categories)}\n  ⚠️ **重要**：必须检查这些适用类目是否与直播间类目匹配。如果不匹配，应该大幅降低匹配度。"
            
            analysis_prompt = f"""
请分析以下热点与直播间的匹配度：

热点信息：
- 标题：{title}
- 内容摘要：{summary}
- 视频风格：{style}
- 电商适配性评分：{ecommerce_score:.2f}
- 电商适配性原因：{ecommerce_fit.get('reasoning', '')}
{applicable_categories_text}
- 视频结构：{str(video_structure)[:500] if video_structure else '无'}
{endorsement_text}

直播间画像：
{live_room_profile}

请从以下维度进行匹配分析：
1. 主题相关性（30%）
2. 受众匹配度（25%）
3. 风格契合度（20%）
4. 内容转化潜力（15%）
5. 风险评估（10%）

**特别注意**：
- **适用类目匹配检查**（最重要）：
  - 如果ContentAnalysisAgent识别的适用类目与直播间类目完全不匹配（如"汽车"vs"家居"、"运动鞋服"vs"女装"），应该大幅降低匹配度（不超过0.4）
  - 如果适用类目与直播间类目匹配，可以正常计算匹配度，适用类目匹配是重要的加分项
  - 避免误匹配："家电"不应该匹配"家居家装"、"运动鞋服"不应该匹配"女装"
- 如果找到了代言和品牌信息，且品牌与直播间类目匹配，应该提升匹配度评分
- 代言信息可以作为额外的匹配依据，说明热点人物与直播间类目有商业关联

请提供：
- 综合匹配度（0-1）
- 各维度评分
- 匹配原因
- 改进建议
"""
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤4完成: 提示词构建成功, 耗时 {step_time:.2f}秒")
            logger.debug(f"🔍 [匹配Agent] 提示词长度: {len(analysis_prompt)}")
            
            # 5. 调用LLM进行匹配分析
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤5: 调用LLM进行匹配分析")
            logger.debug(f"🔍 [匹配Agent] 调用LLM: temperature=0.7, max_tokens=1000")
            response = await self.llm_client.generate(
                prompt=analysis_prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
                max_tokens=1000
            )
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤5完成: LLM分析成功, 耗时 {step_time:.2f}秒")
            
            analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.debug(f"🔍 [匹配Agent] LLM返回分析长度: {len(analysis)}")
            logger.debug(f"🔍 [匹配Agent] LLM分析内容预览: {analysis[:200]}...")
            
            # 6. 从分析中提取匹配度（简单实现：使用电商适配性作为基础）
            step_start = time.time()
            logger.info(f"🔍 [匹配Agent] 步骤6: 计算匹配度分数")
            
            # 如果找到代言信息且与类目匹配，提升基础分数
            endorsement_bonus = 0.0
            if endorsement_info and endorsement_info.get("total", 0) > 0:
                # 检查代言信息中是否包含直播间类目相关的品牌
                category = live_room_profile.split("类目：")[1].split("\n")[0] if "类目：" in live_room_profile else ""
                if category:
                    for endo in endorsement_info.get("endorsements", []):
                        snippet = endo.get("snippet", "").lower()
                        title = endo.get("title", "").lower()
                        if category.lower() in snippet or category.lower() in title:
                            endorsement_bonus = 0.1  # 如果找到匹配的代言，额外加10%
                            logger.info(f"✅ [匹配Agent] 找到匹配的代言信息，提升匹配度 {endorsement_bonus:.1%}")
                            break
            # 实际应该从LLM返回的结构化数据中提取，这里先简化
            relevance_score = ecommerce_score * 0.7 + endorsement_bonus  # 基础分 + 代言加分
            logger.debug(f"🔍 [匹配Agent] 基础匹配度（基于电商适配性）: {relevance_score:.3f} = {ecommerce_score:.3f} * 0.7 + {endorsement_bonus:.3f}")
            
            # 6. 计算语义相似度（作为补充）
            hotspot_text = f"{title} {summary}"
            live_room_text = live_room_profile
            logger.debug(f"🔍 [匹配Agent] 计算语义相似度: 热点文本长度={len(hotspot_text)}, 直播间文本长度={len(live_room_text)}")
            semantic_score = calculate_semantic_similarity(hotspot_text, live_room_text)
            logger.debug(f"🔍 [匹配Agent] 语义相似度: {semantic_score:.3f}")
            
            # 综合匹配度
            final_score = (relevance_score * 0.6 + semantic_score * 0.4)
            logger.debug(f"🔍 [匹配Agent] 综合匹配度计算: {final_score:.3f} = {relevance_score:.3f} * 0.6 + {semantic_score:.3f} * 0.4")
            step_time = time.time() - step_start
            logger.info(f"✅ [匹配Agent] 步骤6完成: 匹配度计算成功, 耗时 {step_time:.2f}秒")
            
            result = {
                "status": "success",
                "relevance_score": final_score,
                "semantic_score": semantic_score,
                "sentiment_score": 0.5,  # 暂时使用默认值
                "keyword_score": 0.0,  # 暂时使用默认值
                "analysis": analysis,
                "ecommerce_fit_score": ecommerce_score
            }
            
            total_time = time.time() - start_time
            logger.info(f"✅ [匹配Agent] 匹配分析完成, 总耗时 {total_time:.2f}秒")
            logger.info(f"✅ [匹配Agent] 最终匹配度: {final_score:.3f} (语义: {semantic_score:.3f}, 电商适配: {ecommerce_score:.3f})")
            logger.debug(f"🔍 [匹配Agent] 完整结果: {json.dumps(result, ensure_ascii=False)}")
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ [匹配Agent] 使用完整内容包分析失败, 耗时 {total_time:.2f}秒: {e}")
            import traceback
            logger.error(f"❌ [匹配Agent] 错误堆栈:\n{traceback.format_exc()}")
            logger.warning(f"⚠️  [匹配Agent] 回退到传统方法")
            # 回退到传统方法
            return await self._execute_legacy({
                "hotspot_text": content_package.get("title", ""),
                "product_text": live_room_name
            })
    
    async def _execute_legacy(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """传统方法（向后兼容）"""
        import time
        start_time = time.time()
        
        hotspot_text = input_data.get("hotspot_text", "")
        product_text = input_data.get("product_text", "")
        
        if not hotspot_text or not product_text:
            raise ValueError("hotspot_text和product_text不能为空")
        
        logger.info(f"🔍 [匹配Agent] 开始关联度分析（传统方法）")
        logger.debug(f"🔍 [匹配Agent] 热点文本: {hotspot_text[:50]}...")
        logger.debug(f"🔍 [匹配Agent] 商品文本: {product_text[:50]}...")
        
        # 1. 计算语义相似度
        step_start = time.time()
        logger.info(f"🔍 [匹配Agent] 步骤1: 计算语义相似度")
        semantic_score = calculate_semantic_similarity(hotspot_text, product_text)
        step_time = time.time() - step_start
        logger.info(f"✅ [匹配Agent] 步骤1完成: 语义相似度={semantic_score:.3f}, 耗时 {step_time:.2f}秒")
        logger.debug(f"🔍 [匹配Agent] 语义相似度计算详情: 热点文本长度={len(hotspot_text)}, 商品文本长度={len(product_text)}")
        
        # 2. 分析情感
        step_start = time.time()
        logger.info(f"🔍 [匹配Agent] 步骤2: 分析情感匹配度")
        hotspot_sentiment = analyze_sentiment(hotspot_text)
        product_sentiment = analyze_sentiment(product_text)
        logger.debug(f"🔍 [匹配Agent] 热点情感: {hotspot_sentiment}")
        logger.debug(f"🔍 [匹配Agent] 商品情感: {product_sentiment}")
        
        # 计算情感匹配度（简单实现：如果情感一致则高分）
        sentiment_match = 1.0 if hotspot_sentiment.get("sentiment") == product_sentiment.get("sentiment") else 0.5
        sentiment_score = (hotspot_sentiment.get("score", 0.5) + product_sentiment.get("score", 0.5)) / 2
        logger.debug(f"🔍 [匹配Agent] 情感匹配: {sentiment_match:.3f}, 情感分数: {sentiment_score:.3f}")
        step_time = time.time() - step_start
        logger.info(f"✅ [匹配Agent] 步骤2完成: 情感匹配度={sentiment_score:.3f}, 耗时 {step_time:.2f}秒")
        
        # 3. 关键词匹配（如果有标签）
        step_start = time.time()
        logger.info(f"🔍 [匹配Agent] 步骤3: 计算关键词匹配度")
        keyword_score = 0.0
        hotspot_tags = input_data.get("hotspot_tags", [])
        product_category = input_data.get("product_category", "")
        
        logger.debug(f"🔍 [匹配Agent] 热点标签: {hotspot_tags}")
        logger.debug(f"🔍 [匹配Agent] 商品类目: {product_category}")
        
        if hotspot_tags and product_category:
            # 检查标签中是否包含类目关键词
            if product_category in hotspot_tags:
                keyword_score = 1.0
                logger.debug(f"🔍 [匹配Agent] 关键词完全匹配: {product_category} 在标签中")
            else:
                # 部分匹配
                keyword_score = 0.3
                logger.debug(f"🔍 [匹配Agent] 关键词部分匹配: {product_category} 不在标签中")
        else:
            logger.debug(f"🔍 [匹配Agent] 关键词匹配跳过: 缺少标签或类目信息")
        
        step_time = time.time() - step_start
        logger.info(f"✅ [匹配Agent] 步骤3完成: 关键词匹配度={keyword_score:.3f}, 耗时 {step_time:.2f}秒")
        
        # 4. 综合计算匹配度
        step_start = time.time()
        logger.info(f"🔍 [匹配Agent] 步骤4: 综合计算匹配度")
        relevance_score = (
            semantic_score * 0.6 +
            sentiment_score * 0.3 +
            keyword_score * 0.1
        )
        logger.debug(f"🔍 [匹配Agent] 综合匹配度计算: {relevance_score:.3f} = {semantic_score:.3f} * 0.6 + {sentiment_score:.3f} * 0.3 + {keyword_score:.3f} * 0.1")
        step_time = time.time() - step_start
        logger.info(f"✅ [匹配Agent] 步骤4完成: 综合匹配度={relevance_score:.3f}, 耗时 {step_time:.2f}秒")
        
        # 5. 生成分析报告
        analysis_prompt = f"""
请分析以下内容的关联度：

热点：{hotspot_text}
商品：{product_text}

计算结果：
- 语义相似度：{semantic_score:.2f}
- 情感匹配度：{sentiment_score:.2f}
- 关键词匹配：{keyword_score:.2f}
- 综合匹配度：{relevance_score:.2f}

请提供详细的分析报告，包括：
1. 关联度评估
2. 匹配原因
3. 改进建议
"""
        
        # 调用LLM生成分析报告
        step_start = time.time()
        logger.info(f"🔍 [匹配Agent] 步骤5: 生成分析报告")
        try:
            logger.debug(f"🔍 [匹配Agent] 调用LLM生成分析报告: temperature=0.7, max_tokens=500")
            response = await self.llm_client.generate(
                prompt=analysis_prompt,
                system_prompt=self._get_system_prompt(),
                temperature=0.7,
                max_tokens=500
            )
            analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.debug(f"🔍 [匹配Agent] LLM分析报告长度: {len(analysis)}")
        except Exception as e:
            logger.error(f"❌ [匹配Agent] 生成分析报告失败: {e}")
            analysis = f"匹配度分析：{relevance_score:.2f}（语义：{semantic_score:.2f}，情感：{sentiment_score:.2f}）"
        step_time = time.time() - step_start
        logger.info(f"✅ [匹配Agent] 步骤5完成: 分析报告生成成功, 耗时 {step_time:.2f}秒")
        
        result = {
            "status": "success",
            "relevance_score": relevance_score,
            "semantic_score": semantic_score,
            "sentiment_score": sentiment_score,
            "keyword_score": keyword_score,
            "analysis": analysis,
            "hotspot_sentiment": hotspot_sentiment,
            "product_sentiment": product_sentiment
        }
        
        total_time = time.time() - start_time
        logger.info(f"✅ [匹配Agent] 关联度分析完成, 总耗时 {total_time:.2f}秒")
        logger.info(f"✅ [匹配Agent] 最终匹配度: {relevance_score:.3f} (语义: {semantic_score:.3f}, 情感: {sentiment_score:.3f}, 关键词: {keyword_score:.3f})")
        logger.debug(f"🔍 [匹配Agent] 完整结果: {json.dumps(result, ensure_ascii=False, default=str)}")
        return result

