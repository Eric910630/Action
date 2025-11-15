"""
热点监控定时任务
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.hotspot.service import HotspotMonitorService
from loguru import logger


@celery_app.task(bind=True)
def fetch_daily_hotspots(self, platform: str = None, live_room_id: str = None):
    """
    每日8:00自动抓取热点（使用语义筛选）
    
    Args:
        platform: 平台标识，如果为None则抓取多个平台
        live_room_id: 直播间ID
    """
    # 定义要抓取的平台列表（每个平台30个热点）
    if platform:
        platforms = [platform]
    else:
        # 默认抓取多个主流平台
        platforms = ["douyin", "zhihu", "weibo", "bilibili"]
    
    logger.info(f"开始抓取每日热点，平台: {platforms}, 直播间: {live_room_id}")
    
    # 更新状态：开始抓取
    self.update_state(
        state='PROGRESS',
        meta={
            'current': 0,
            'total': len(platforms),
            'status': f'开始抓取 {len(platforms)} 个平台的热点...'
        }
    )
    
    try:
        service = HotspotMonitorService()
        db = SessionLocal()
        
        try:
            # 异步获取所有平台的热点
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            all_hotspots = []
            platform_counts = {}
            
            # 并发抓取多个平台
            fetched_count = 0
            fetch_lock = asyncio.Lock()
            
            async def fetch_platform(platform_name):
                nonlocal fetched_count
                try:
                    hotspots = await service.fetch_hotspots(platform=platform_name)
                    
                    # 使用锁保护计数器更新
                    async with fetch_lock:
                        fetched_count += 1
                        current_count = fetched_count
                    
                    logger.info(f"平台 {platform_name} 抓取到 {len(hotspots)} 个热点")
                    
                    # 更新进度：抓取平台进度
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': current_count,
                            'total': len(platforms),
                            'status': f'已抓取 {current_count}/{len(platforms)} 个平台，{platform_name} 抓取到 {len(hotspots)} 个热点'
                        }
                    )
                    
                    return platform_name, hotspots
                except Exception as e:
                    # 使用锁保护计数器更新
                    async with fetch_lock:
                        fetched_count += 1
                        current_count = fetched_count
                    
                    logger.error(f"平台 {platform_name} 抓取失败: {e}")
                    
                    # 更新进度：抓取失败
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': current_count,
                            'total': len(platforms),
                            'status': f'已抓取 {current_count}/{len(platforms)} 个平台，{platform_name} 抓取失败'
                        }
                    )
                    
                    return platform_name, []
            
            # 并发抓取所有平台
            results = loop.run_until_complete(
                asyncio.gather(*[fetch_platform(p) for p in platforms])
            )
            
            # 汇总所有平台的热点
            for platform_name, hotspots in results:
                all_hotspots.extend(hotspots)
                platform_counts[platform_name] = len(hotspots)
            
            logger.info(f"总共抓取到 {len(all_hotspots)} 个热点（来自 {len(platforms)} 个平台）")
            
            # 更新状态：抓取完成，开始语义筛选
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': len(platforms),
                    'total': len(platforms) + 1,
                    'status': f'抓取完成！共抓取 {len(all_hotspots)} 个热点，开始语义筛选...'
                }
            )
            
            # 使用语义关联度筛选热点
            from datetime import datetime
            filtered_hotspots = loop.run_until_complete(
                service.filter_hotspots_with_semantic(
                    db, all_hotspots, live_room_id=live_room_id, target_date=datetime.now()
                )
            )
            
            # 更新状态：语义筛选完成
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': len(platforms) + 1,
                    'total': len(platforms) + 1 + (1 if filtered_hotspots else 0),
                    'status': f'语义筛选完成，剩余 {len(filtered_hotspots)} 个热点'
                }
            )
            
            # 调试日志：检查filtered_hotspots的实际返回值
            logger.info(f"[DEBUG] filter_hotspots_with_semantic返回: type={type(filtered_hotspots)}, len={len(filtered_hotspots) if filtered_hotspots else 'N/A'}, bool={bool(filtered_hotspots)}")
            if filtered_hotspots:
                logger.info(f"[DEBUG] filtered_hotspots前3个: {filtered_hotspots[:3] if len(filtered_hotspots) >= 3 else filtered_hotspots}")
            else:
                logger.warning(f"[DEBUG] filtered_hotspots为空或None，无法执行增强逻辑")
            
            # 新增：使用ContentStructureAgent和ContentAnalysisAgent增强热点信息
            if filtered_hotspots:
                logger.info("[ENRICH] 使用ContentStructureAgent和ContentAnalysisAgent增强热点信息...")
                try:
                    from app.agents import get_content_structure_agent, get_content_analysis_agent
                    
                    structure_agent = get_content_structure_agent()
                    analysis_agent = get_content_analysis_agent()
                    logger.info(f"[ENRICH] Agent初始化成功，准备增强 {len(filtered_hotspots)} 个热点（使用本地视频分析工具包）")
                except Exception as e:
                    logger.error(f"[ENRICH] Agent初始化失败: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
                
                # 增强所有热点（使用本地工具包，无API成本限制）
                # 注意：增强所有筛选后的热点，不限制数量
                hotspots_to_enrich = filtered_hotspots
                logger.info(f"[ENRICH] 准备增强 {len(hotspots_to_enrich)} 个热点（全部筛选后的热点）")
                
                # 更新状态：开始增强
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': len(platforms) + 1,
                        'total': len(platforms) + 1 + len(hotspots_to_enrich),
                        'status': f'开始解析 {len(hotspots_to_enrich)} 个热点...'
                    }
                )
                
                enriched_count = 0
                enrich_lock = asyncio.Lock()
                
                async def enrich_hotspot(hotspot):
                    """增强单个热点"""
                    import time
                    hotspot_start = time.time()
                    
                    url = hotspot.get("url")
                    title = hotspot.get("title", "")
                    hotspot_id = hotspot.get("id") or hotspot.get("title", "unknown")[:50]
                    
                    logger.info(f"🔍 [探针] enrich_hotspot 开始: {hotspot_id}")
                    logger.debug(f"🔍 [探针] 热点信息: url={url[:100] if url else 'N/A'}, title={title[:50] if title else 'N/A'}")
                    
                    try:
                        if not url:
                            logger.warning(f"⚠️  [探针] 热点无URL，跳过增强: {hotspot_id}")
                            hotspot["enrichment_skipped"] = True
                            hotspot["enrichment_reason"] = "无URL"
                            return hotspot
                        
                        # 1. 使用ContentStructureAgent提取视频结构
                        step_start = time.time()
                        logger.info(f"🔍 [探针] 步骤1: 提取视频结构 - {hotspot_id}")
                        logger.debug(f"提取视频结构: {title[:50]}")
                        structure_result = await structure_agent.execute({
                            "url": url,
                            "title": title
                        })
                        step_time = time.time() - step_start
                        logger.info(f"✅ [探针] 步骤1完成: 视频结构提取成功, 耗时 {step_time:.2f}秒 - {hotspot_id}")
                        
                        video_structure = structure_result.get("video_structure", {})
                        hotspot["video_structure"] = video_structure
                        logger.debug(f"🔍 [探针] 视频结构摘要: duration={video_structure.get('duration')}, scenes={len(video_structure.get('scenes', []))}, transcript_len={len(video_structure.get('transcript', ''))}")
                        
                        # 2. 使用ContentAnalysisAgent分析内容
                        step_start = time.time()
                        logger.info(f"🔍 [探针] 步骤2: 分析视频内容 - {hotspot_id}")
                        logger.debug(f"分析视频内容: {title[:50]}")
                        analysis_result = await analysis_agent.execute({
                            "video_structure": video_structure,
                            "title": title,
                            "url": url
                        })
                        step_time = time.time() - step_start
                        logger.info(f"✅ [探针] 步骤2完成: 内容分析成功, 耗时 {step_time:.2f}秒 - {hotspot_id}")
                        
                        content_analysis = analysis_result.get("content_analysis", {})
                        hotspot["content_analysis"] = content_analysis
                        logger.debug(f"🔍 [探针] 内容分析摘要: summary_len={len(content_analysis.get('summary', ''))}")
                        
                        # 3. 提取内容摘要（用于content_compact字段）
                        step_start = time.time()
                        logger.info(f"🔍 [探针] 步骤3: 提取内容摘要 - {hotspot_id}")
                        summary = content_analysis.get("summary", "")
                        if summary:
                            hotspot["content_compact"] = summary
                            logger.debug(f"🔍 [探针] 使用分析摘要作为content_compact: 长度={len(summary)}")
                        elif video_structure.get("transcript"):
                            hotspot["content_compact"] = video_structure.get("transcript", "")[:500]
                            logger.debug(f"🔍 [探针] 使用转录文本作为content_compact: 长度={len(hotspot['content_compact'])}")
                        else:
                            logger.warning(f"⚠️  [探针] 无可用内容作为content_compact - {hotspot_id}")
                        
                        step_time = time.time() - step_start
                        total_time = time.time() - hotspot_start
                        logger.info(f"✅ [探针] 步骤3完成: 内容摘要提取成功, 耗时 {step_time:.4f}秒 - {hotspot_id}")
                        logger.info(f"✅ [探针] enrich_hotspot 完成, 总耗时 {total_time:.2f}秒 - {hotspot_id}")
                        logger.debug(f"热点增强完成: {title[:50]}")
                        return hotspot
                    except Exception as e:
                        total_time = time.time() - hotspot_start
                        logger.error(f"❌ [探针] enrich_hotspot 失败, 耗时 {total_time:.2f}秒 - {hotspot_id}: {e}")
                        import traceback
                        logger.debug(f"❌ [探针] 错误堆栈:\n{traceback.format_exc()}")
                        logger.warning(f"热点增强失败: {e}，返回原始热点")
                        return hotspot
                
                # 并发增强热点（限制并发数）
                semaphore = asyncio.Semaphore(3)  # 最多3个并发
                
                async def enrich_with_semaphore(hotspot):
                    nonlocal enriched_count
                    async with semaphore:
                        result = await enrich_hotspot(hotspot)
                        
                        # 使用锁保护计数器更新
                        async with enrich_lock:
                            enriched_count += 1
                            current_count = enriched_count
                        
                        # 更新进度：增强进度
                        self.update_state(
                            state='PROGRESS',
                            meta={
                                'current': len(platforms) + 1 + current_count,
                                'total': len(platforms) + 1 + len(hotspots_to_enrich),
                                'status': f'正在解析热点: {current_count}/{len(hotspots_to_enrich)}'
                            }
                        )
                        
                        return result
                
                enriched_hotspots = loop.run_until_complete(
                    asyncio.gather(*[enrich_with_semaphore(h) for h in hotspots_to_enrich])
                )
                
                # 合并增强后的热点（替换所有热点）
                filtered_hotspots = enriched_hotspots
                logger.info(f"[ENRICH] 成功增强 {len(enriched_hotspots)} 个热点（共 {len(filtered_hotspots)} 个）")
                
                # 更新状态：增强完成
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': len(platforms) + 1 + len(enriched_hotspots),
                        'total': len(platforms) + 1 + len(hotspots_to_enrich),
                        'status': f'解析完成！已解析 {len(enriched_hotspots)} 个热点，正在保存...'
                    }
                )
                # 调试：检查增强后的数据
                for i, h in enumerate(enriched_hotspots[:3], 1):
                    logger.debug(f"[ENRICH] 热点#{i}: video_structure={'有' if h.get('video_structure') else '无'}, content_analysis={'有' if h.get('content_analysis') else '无'}, content_compact={'有' if h.get('content_compact') else '无'}")
                
                # 保存agents输出结果到upgrade.md
                try:
                    save_agents_output_to_upgrade_md(enriched_hotspots)
                    logger.info("[ENRICH] 已保存agents输出结果到upgrade.md")
                except Exception as e:
                    logger.error(f"[ENRICH] 保存agents输出到upgrade.md失败: {e}")
            
            # Firecrawl增强已移除：不需要Firecrawl，ContentStructureAgent和ContentAnalysisAgent已经足够
            # 如果将来需要，可以通过配置FIRECRAWL_ENABLED重新启用
            
            try:
                loop.close()
            except:
                pass
            
            if filtered_hotspots:
                # 按平台分组保存
                from collections import defaultdict
                hotspots_by_platform = defaultdict(list)
                for hotspot in filtered_hotspots:
                    platform_name = hotspot.get("platform", "unknown")
                    hotspots_by_platform[platform_name].append(hotspot)
                
                # 更新状态：开始保存
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': len(platforms) + 1 + len(enriched_hotspots) if filtered_hotspots and any(h.get('video_structure') or h.get('content_analysis') for h in filtered_hotspots) else len(platforms) + 1,
                        'total': len(platforms) + 1 + len(hotspots_to_enrich) if filtered_hotspots and any(h.get('video_structure') or h.get('content_analysis') for h in filtered_hotspots) else len(platforms) + 1,
                        'status': f'正在保存 {len(filtered_hotspots)} 个热点到数据库...'
                    }
                )
                
                # 保存每个平台的热点
                total_saved = 0
                for platform_name, platform_hotspots in hotspots_by_platform.items():
                    saved = service.save_hotspots(db, platform_hotspots, platform_name)
                    total_saved += saved
                    logger.info(f"平台 {platform_name} 保存了 {saved} 个热点")
                
                logger.info(f"成功抓取并保存 {total_saved} 个热点（来自 {len(platforms)} 个平台，语义筛选后）")
                
                # 更新状态：保存完成
                final_total = len(platforms) + 1 + len(hotspots_to_enrich) if filtered_hotspots and any(h.get('video_structure') or h.get('content_analysis') for h in filtered_hotspots) else len(platforms) + 1
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': final_total,
                        'total': final_total,
                        'status': f'保存完成！共保存 {total_saved} 个热点'
                    }
                )
            else:
                logger.warning(f"语义筛选后没有热点（原始热点数: {len(all_hotspots)}）")
            
            # 任务完成，返回SUCCESS状态
            return {
                "status": "success",
                "message": f"热点抓取任务已完成（{len(platforms)} 个平台，语义筛选后）",
                "count": len(filtered_hotspots) if filtered_hotspots else 0,
                "platforms": platform_counts
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"热点抓取失败: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@celery_app.task
def push_hotspots_to_feishu(live_room_id: str = None):
    """每日9:00推送热点到飞书"""
    logger.info("开始推送热点到飞书")
    
    try:
        service = HotspotMonitorService()
        db = SessionLocal()
        
        try:
            # 异步推送
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                service.push_to_feishu(db, live_room_id)
            )
            loop.close()
            
            if success:
                logger.info("热点推送完成")
                return {"status": "success", "message": "热点推送任务已完成"}
            else:
                logger.warning("热点推送失败")
                return {"status": "error", "message": "热点推送失败"}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"推送热点到飞书失败: {e}")
        return {"status": "error", "message": str(e)}


def save_agents_output_to_upgrade_md(enriched_hotspots: list):
    """
    保存agents输出结果到upgrade.md文件
    
    Args:
        enriched_hotspots: 增强后的热点列表
    """
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        upgrade_md_path = project_root / "upgrade.md"
        
        if not upgrade_md_path.exists():
            logger.warning(f"upgrade.md文件不存在: {upgrade_md_path}")
            return
        
        # 读取现有内容
        with open(upgrade_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找"## 二、30个热点详细列表"部分，如果不存在则创建
        section_marker = "## 二、30个热点详细列表"
        if section_marker not in content:
            # 如果不存在，在文件末尾添加
            new_section = f"\n\n{section_marker}\n\n"
            content += new_section
        
        # 生成新的agents输出内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agents_output = f"\n\n### Agents输出结果（更新时间: {timestamp}）\n\n"
        agents_output += f"本次共处理 {len(enriched_hotspots)} 个热点\n\n"
        
        for idx, hotspot in enumerate(enriched_hotspots, 1):
            title = hotspot.get("title", "未知标题")
            url = hotspot.get("url", "")
            platform = hotspot.get("platform", "unknown")
            
            agents_output += f"#### {idx}. {title}\n"
            agents_output += f"- **URL**: {url}\n"
            agents_output += f"- **平台**: {platform}\n"
            
            # ContentStructureAgent输出
            video_structure = hotspot.get("video_structure", {})
            if video_structure:
                agents_output += f"- **ContentStructureAgent输出**:\n"
                agents_output += f"  - 视频时长: {video_structure.get('duration', 0.0)}秒\n"
                agents_output += f"  - 场景数: {len(video_structure.get('scenes', []))}\n"
                agents_output += f"  - 关键帧数: {len(video_structure.get('key_frames', []))}\n"
                agents_output += f"  - 转录文本长度: {len(video_structure.get('transcript', ''))}\n"
                agents_output += f"  - 视觉元素: {json.dumps(video_structure.get('visual_elements', {}), ensure_ascii=False)[:200]}...\n"
                agents_output += f"  - 音频元素: {json.dumps(video_structure.get('audio_elements', {}), ensure_ascii=False)[:200]}...\n"
            else:
                agents_output += f"- **ContentStructureAgent输出**: 无\n"
            
            # ContentAnalysisAgent输出
            content_analysis = hotspot.get("content_analysis", {})
            if content_analysis:
                agents_output += f"- **ContentAnalysisAgent输出**:\n"
                agents_output += f"  - 内容摘要: {content_analysis.get('summary', '无')}\n"
                agents_output += f"  - 视频风格: {content_analysis.get('style', '无')}\n"
                ecommerce_fit = content_analysis.get("ecommerce_fit", {})
                if ecommerce_fit:
                    agents_output += f"  - 电商适配性评分: {ecommerce_fit.get('score', 0.0)}\n"
                    agents_output += f"  - 适配性原因: {ecommerce_fit.get('reasoning', '无')}\n"
                    agents_output += f"  - 适用类目: {', '.join(ecommerce_fit.get('applicable_categories', []))}\n"
                script_structure = content_analysis.get("script_structure", {})
                if script_structure:
                    agents_output += f"  - 脚本结构: {json.dumps(script_structure, ensure_ascii=False)}\n"
            else:
                agents_output += f"- **ContentAnalysisAgent输出**: 无\n"
            
            agents_output += "\n"
        
        # 查找并替换或追加内容
        # 如果存在"### Agents输出结果"部分，则替换；否则追加
        agents_section_marker = "### Agents输出结果"
        if agents_section_marker in content:
            # 找到最后一个"### Agents输出结果"的位置
            last_pos = content.rfind(agents_section_marker)
            # 找到下一个"##"或文件末尾
            next_section_pos = content.find("\n## ", last_pos)
            if next_section_pos == -1:
                # 没有下一个章节，替换到文件末尾
                content = content[:last_pos] + agents_output
            else:
                # 替换到下一个章节之前
                content = content[:last_pos] + agents_output + content[next_section_pos:]
        else:
            # 追加到"## 二、30个热点详细列表"部分之后
            section_pos = content.find(section_marker)
            if section_pos != -1:
                # 找到该章节的结束位置（下一个"##"或文件末尾）
                next_section_pos = content.find("\n## ", section_pos + len(section_marker))
                if next_section_pos == -1:
                    # 没有下一个章节，追加到文件末尾
                    content = content + agents_output
                else:
                    # 插入到下一个章节之前
                    content = content[:next_section_pos] + agents_output + content[next_section_pos:]
            else:
                # 如果找不到章节，追加到文件末尾
                content = content + agents_output
        
        # 写回文件
        with open(upgrade_md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"已更新upgrade.md文件: {upgrade_md_path}")
        
    except Exception as e:
        logger.error(f"保存agents输出到upgrade.md失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

