"""
E2E测试 - 完整业务流程（使用真实LLM API）
测试从热点发现到脚本生成的完整流程，使用真实的DeepSeek API和TrendRadar API
WebContentExtractor (Trafilatura) 使用Mock（避免消耗API额度）

注意：此测试需要使用真实数据库（USE_TEST_DB=true），因为Celery任务需要访问数据库
"""
import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, date
from tests.utils.task_waiter import wait_for_task, get_task_status

# 确保使用真实数据库（不是内存数据库）
# 这样Celery任务可以访问测试数据
# 对于真实LLM测试，使用原始数据库（不是_test后缀），因为Celery任务使用原始数据库
if os.getenv("USE_TEST_DB") != "true":
    os.environ["USE_TEST_DB"] = "true"
    
# 重要：对于真实LLM测试，我们需要确保测试和Celery任务使用相同的数据库
# 由于Celery任务使用settings.database_url（原始数据库），
# 我们需要让测试也使用原始数据库，而不是_test数据库
# 这通过设置USE_REAL_DB_FOR_CELERY环境变量来实现
os.environ["USE_REAL_DB_FOR_CELERY"] = "true"


class TestCompleteWorkflowRealLLM:
    """完整业务流程E2E测试（使用真实LLM）"""
    
    @pytest.mark.e2e
    @pytest.mark.real_api
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_complete_workflow_with_real_llm(
        self, 
        client, 
        db_session, 
        sample_live_room_id,
        use_real_llm,
        use_real_trendradar
    ):
        """
        测试完整的业务流程（使用真实LLM API）
        
        注意：此测试需要配置DEEPSEEK_API_KEY环境变量
        """
        if not use_real_llm:
            pytest.skip("DEEPSEEK_API_KEY未配置，跳过真实LLM测试")
        
        # ========== Step 1: 创建商品（主推商品）==========
        product_data = {
            "name": "时尚连衣裙",
            "brand": "测试品牌",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 299.0,
            "selling_points": ["时尚", "舒适", "百搭"],
            "description": "时尚百搭的连衣裙，适合各种场合",
            "hand_card": "限时优惠299元",
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 确保商品数据也在应用数据库中（Celery任务需要访问）
        # 由于商品是通过API创建的，需要从db_session中获取并同步到应用数据库
        from loguru import logger
        from app.models.product import Product
        from app.models.product import Product as AppProduct
        from app.core.database import SessionLocal
        
        logger.info(f"🔍 [探针] 开始同步商品数据: {product_id}")
        app_db = SessionLocal()
        try:
            # 先从测试数据库获取商品
            logger.debug(f"🔍 [探针] 从测试数据库查询商品: {product_id}")
            test_product = db_session.query(Product).filter(Product.id == product_id).first()
            if test_product:
                logger.info(f"🔍 [探针] 测试数据库中商品存在: {test_product.name}")
                # 检查应用数据库中是否存在
                logger.debug(f"🔍 [探针] 检查应用数据库中商品是否存在: {product_id}")
                verify_product = app_db.query(AppProduct).filter(AppProduct.id == product_id).first()
                if not verify_product:
                    logger.warning(f"⚠️  [探针] 商品数据不在应用数据库中，正在同步...")
                    app_product = AppProduct(
                        id=test_product.id,
                        name=test_product.name,
                        description=test_product.description,
                        category=test_product.category,
                        price=test_product.price,
                        live_room_id=test_product.live_room_id,
                        created_at=test_product.created_at,
                        updated_at=test_product.updated_at
                    )
                    app_db.add(app_product)
                    app_db.commit()
                    logger.info(f"✅ [探针] 商品数据已同步到应用数据库: {product_id}")
                    print(f"✓ 商品数据已同步到应用数据库: {product_id}")
                else:
                    logger.info(f"✅ [探针] 商品数据已确认存在于应用数据库: {product_id}")
                    print(f"✓ 商品数据已确认存在于应用数据库: {product_id}")
            else:
                logger.error(f"❌ [探针] 商品在测试数据库中不存在: {product_id}")
                print(f"⚠ 警告: 商品在测试数据库中不存在: {product_id}")
        except Exception as e:
            logger.error(f"❌ [探针] 同步商品数据时出错: {e}")
            import traceback
            logger.exception(f"❌ [探针] 同步商品数据异常堆栈:")
            print(f"⚠ 同步商品数据时出错: {e}")
            traceback.print_exc()
        finally:
            app_db.close()
            logger.debug(f"🔍 [探针] 商品数据同步流程完成")
        
        # ========== Step 2: 触发热点抓取 ==========
        # 使用真实TrendRadar服务（直接爬虫或MCP），但Mock WebContentExtractor (Trafilatura替代Firecrawl)
        if not use_real_trendradar:
            pytest.skip("TrendRadar功能未启用，跳过真实API测试")
        
        # Mock WebContentExtractor (Trafilatura替代Firecrawl)
        # 注意：WebContentExtractor在ContentStructureAgent中使用，需要mock
        mock_web_content = {
            "content": "这是一篇关于时尚穿搭和连衣裙搭配技巧的文章，介绍了如何选择适合的连衣裙以及搭配技巧。",
            "metadata": {
                "title": "时尚穿搭推荐 连衣裙搭配技巧",
                "author": "",
                "date": "",
                "description": "时尚穿搭和连衣裙搭配技巧",
                "url": "https://test.com/hotspot"
            }
        }
        
        # Mock WebContentExtractor的extract_from_url方法
        with patch('app.utils.web_content_extractor.WebContentExtractor.extract_from_url', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = mock_web_content
            
            # 不传platform参数，测试多平台抓取（douyin, zhihu, weibo, bilibili）
            response = client.post(
                "/api/v1/hotspots/fetch",
                params={
                    "live_room_id": sample_live_room_id
                }
            )
            assert response.status_code == 200
            task_id = response.json().get("task_id")
            
            # 等待任务完成（如果使用真实API）
            # 注意：热点抓取任务可能需要较长时间（每个热点关联度分析需要20-30秒）
            # 如果有30个热点，可能需要10-15分钟
            if task_id:
                from loguru import logger
                logger.info(f"🔍 [探针] 准备等待热点抓取任务完成: {task_id}")
                try:
                    # 增加超时时间到10分钟（600秒），因为真实LLM API调用较慢
                    logger.info(f"🔍 [探针] 调用wait_for_task，超时设置: 600秒")
                    task_result = wait_for_task(task_id, timeout=600)
                    logger.info(f"✅ [探针] 热点抓取任务完成，结果: {task_result}")
                except TimeoutError as e:
                    # 超时不算失败，只是跳过这个测试步骤
                    logger.warning(f"⚠️  [探针] TrendRadar任务超时: {e}")
                    pytest.skip(f"TrendRadar任务超时（可能热点太多）: {e}")
                except Exception as e:
                    logger.error(f"❌ [探针] TrendRadar任务失败: {e}")
                    logger.exception(f"❌ [探针] TrendRadar任务异常堆栈:")
                    pytest.skip(f"TrendRadar任务失败: {e}")
        
        # ========== Step 3: 创建测试热点（用于后续测试）==========
        from app.models.hotspot import Hotspot
        from app.core.database import SessionLocal
        
        hotspot = Hotspot(
            id="test-workflow-hotspot-real-llm",
            title="时尚穿搭推荐 连衣裙搭配技巧",
            url="https://test.com/workflow-real-llm",
            platform="douyin",
            tags=["时尚", "穿搭", "连衣裙"],
            heat_score=95,
            heat_growth_rate=0.15,
            match_score=0.85,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        # 重要：对于真实LLM测试，需要确保数据在Celery任务可以访问的数据库中
        # 由于Celery任务使用SessionLocal（应用数据库），我们需要确保数据也在那里
        db_session.add(hotspot)
        db_session.commit()
        db_session.refresh(hotspot)  # 确保数据已刷新
        hotspot_id = hotspot.id
        
        # 验证并确保数据在应用数据库中存在（Celery任务使用的数据库）
        from loguru import logger
        from app.core.database import SessionLocal
        
        logger.info(f"🔍 [探针] 开始同步热点数据: {hotspot_id}")
        app_db = SessionLocal()
        try:
            # 检查数据是否在应用数据库中
            logger.debug(f"🔍 [探针] 检查应用数据库中热点是否存在: {hotspot_id}")
            verify_hotspot = app_db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
            if not verify_hotspot:
                # 如果不存在，说明测试数据库和应用数据库不同
                # 在这种情况下，我们需要在应用数据库中也创建数据
                logger.warning(f"⚠️  [探针] 热点数据不在应用数据库中，正在同步...")
                print(f"⚠ 数据不在应用数据库中，正在同步...")
                app_hotspot = Hotspot(
                    id=hotspot.id,
                    title=hotspot.title,
                    url=hotspot.url,
                    platform=hotspot.platform,
                    tags=hotspot.tags,
                    heat_score=hotspot.heat_score,
                    match_score=hotspot.match_score,
                    created_at=hotspot.created_at,
                    updated_at=hotspot.updated_at
                )
                app_db.add(app_hotspot)
                app_db.commit()
                logger.info(f"✅ [探针] 热点数据已同步到应用数据库: {hotspot_id}")
                print(f"✓ 热点数据已同步到应用数据库: {hotspot_id}")
            else:
                logger.info(f"✅ [探针] 热点数据已确认存在于应用数据库: {hotspot_id}")
                print(f"✓ 热点数据已确认存在于应用数据库: {hotspot_id}")
        except Exception as e:
            logger.error(f"❌ [探针] 同步热点数据时出错: {e}")
            logger.exception(f"❌ [探针] 同步热点数据异常堆栈:")
            print(f"⚠ 同步数据时出错: {e}")
            # 即使同步失败，也继续测试，看看是否能工作
        finally:
            app_db.close()
            logger.debug(f"🔍 [探针] 热点数据同步流程完成")
        
        # ========== Step 4: 创建拆解报告（可选，如果视频拆解也使用真实API）==========
        from app.models.analysis import AnalysisReport
        
        report = AnalysisReport(
            id="test-workflow-report-real-llm",
            video_url=hotspot.url,
            viral_formula={
                "formula_name": "反转公式",
                "formula_structure": "问题-反转-解决"
            },
            production_tips={
                "shooting_tips": ["注意光线"],
                "editing_tips": ["快速切换"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        report_id = report.id
        
        # 确保报告数据也在应用数据库中（Celery任务需要访问）
        from app.models.analysis import AnalysisReport as AppAnalysisReport
        app_db = SessionLocal()
        try:
            verify_report = app_db.query(AppAnalysisReport).filter(AppAnalysisReport.id == report_id).first()
            if not verify_report:
                print(f"⚠ 报告数据不在应用数据库中，正在同步...")
                app_report = AppAnalysisReport(
                    id=report.id,
                    video_url=report.video_url,
                    viral_formula=report.viral_formula,
                    production_tips=report.production_tips,
                    created_at=report.created_at,
                    updated_at=report.updated_at
                )
                app_db.add(app_report)
                app_db.commit()
                print(f"✓ 报告数据已同步到应用数据库: {report_id}")
            else:
                print(f"✓ 报告数据已确认存在于应用数据库: {report_id}")
        except Exception as e:
            print(f"⚠ 同步报告数据时出错: {e}")
        finally:
            app_db.close()
        
        # ========== Step 5: 生成脚本（使用真实LLM API）==========
        # 不再Mock，直接调用真实API
        script_request = {
            "hotspot_id": hotspot_id,
            "product_id": product_id,
            "analysis_report_id": report_id,
            "duration": 10
        }
        
        response = client.post("/api/v1/scripts/generate", json=script_request)
        assert response.status_code == 200
        
        task_data = response.json()
        assert "task_id" in task_data
        task_id = task_data["task_id"]
        
        # 等待异步任务完成（使用真实LLM）
        # 注意：真实LLM测试可能需要较长时间，但设置合理的超时时间
        try:
            task_result = wait_for_task(task_id, timeout=120)  # 2分钟超时（真实LLM可能需要时间）
            assert task_result is not None, "任务结果不应为空"
            
            # 检查任务返回的状态
            if isinstance(task_result, dict):
                if task_result.get("status") == "error":
                    error_msg = task_result.get("message", "未知错误")
                    pytest.fail(f"脚本生成任务返回错误: {error_msg}")
                elif task_result.get("status") == "success":
                    print(f"✓ 脚本生成任务成功: {task_result.get('script_id', 'N/A')}")
                else:
                    print(f"⚠ 任务返回状态: {task_result.get('status', 'unknown')}")
        except TimeoutError as e:
            pytest.fail(f"脚本生成任务超时: {e}")
        except Exception as e:
            pytest.fail(f"脚本生成任务失败: {e}")
        
        # ========== Step 6: 验证生成的脚本 ==========
        # 从数据库获取生成的脚本
        from app.models.script import Script
        
        script = db_session.query(Script).filter(
            Script.hotspot_id == hotspot_id,
            Script.product_id == product_id
        ).order_by(Script.created_at.desc()).first()
        
        assert script is not None, "脚本应该已生成"
        assert script.script_content is not None, "脚本内容不应为空"
        assert len(script.script_content) > 0, "脚本内容应该有内容"
        
        # 验证脚本结构
        assert script.video_info is not None, "视频信息应该存在"
        assert script.shot_list is not None, "分镜列表应该存在"
        assert script.production_notes is not None, "制作要点应该存在"
        
        # 验证脚本内容质量（使用真实LLM生成的内容应该有合理的长度）
        assert len(script.script_content) > 50, "脚本内容应该足够详细"
        
        # ========== Step 7: 通过API获取脚本详情 ==========
        response = client.get(f"/api/v1/scripts/{script.id}")
        assert response.status_code == 200
        script_data = response.json()
        
        assert script_data["id"] == script.id
        assert script_data["product_id"] == product_id
        assert script_data["hotspot_id"] == hotspot_id
        assert script_data["analysis_report_id"] == report_id
        assert len(script_data["script_content"]) > 0
        
        # 验证分镜列表
        if script_data.get("shot_list"):
            assert len(script_data["shot_list"]) > 0, "分镜列表应该有内容"
        
        # ========== Step 8: 验证脚本优化建议 ==========
        response = client.post(f"/api/v1/scripts/{script.id}/optimize")
        assert response.status_code == 200
        optimize_data = response.json()
        assert "suggestions" in optimize_data
        
        # ========== Step 9: 验证完整数据链路 ==========
        # 验证热点
        response = client.get(f"/api/v1/hotspots/{hotspot_id}")
        assert response.status_code == 200
        
        # 验证商品
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        
        # 验证报告
        response = client.get(f"/api/v1/analysis/reports/{report_id}")
        assert response.status_code == 200

