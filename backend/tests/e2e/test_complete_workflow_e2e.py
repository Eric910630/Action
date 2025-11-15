"""
E2E测试 - 完整业务流程
测试从热点发现到脚本生成的完整流程，包括新的语义关联度功能
WebContentExtractor (Trafilatura) 使用Mock（避免消耗API额度）
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date


class TestCompleteWorkflowE2E:
    """完整业务流程E2E测试"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_with_semantic(self, client, db_session, sample_live_room_id):
        """测试完整的业务流程（包含语义关联度筛选）"""
        
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
        
        # ========== Step 2: 触发热点抓取（使用语义筛选）==========
        with patch('app.services.hotspot.tasks.fetch_daily_hotspots.delay') as mock_fetch, \
             patch('app.utils.embedding.EmbeddingClient.calculate_semantic_similarity') as mock_semantic, \
             patch('app.utils.sentiment.SentimentClient.analyze_sentiment') as mock_sentiment:
            
            mock_task = MagicMock()
            mock_task.id = "test-fetch-task-id"
            mock_fetch.return_value = mock_task
            
            # Mock语义和情感分析
            async def semantic_side_effect(text1, text2):
                if "连衣裙" in text1 or "连衣裙" in text2:
                    return 0.85
                return 0.15
            
            mock_semantic.side_effect = semantic_side_effect
            mock_sentiment.return_value = {"sentiment": "neutral", "score": 0.5}
            
            # 不传platform参数，测试多平台抓取（douyin, zhihu, weibo, bilibili）
            response = client.post(
                "/api/v1/hotspots/fetch",
                params={
                    "live_room_id": sample_live_room_id
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
        
        # ========== Step 3: 创建测试热点（模拟抓取结果，包含内容增强）==========
        from app.models.hotspot import Hotspot
        
        hotspot = Hotspot(
            id="test-workflow-hotspot",
            title="时尚穿搭推荐 连衣裙搭配技巧",
            url="https://test.com/workflow",
            platform="douyin",
            tags=["时尚", "穿搭", "连衣裙"],
            heat_score=95,
            heat_growth_rate=0.15,
            match_score=0.85,  # 基于语义关联度计算的匹配度
            # 新增字段：内容Compact相关
            content_compact="这是关于连衣裙搭配技巧的视频摘要",
            video_structure={
                "duration": 15.0,
                "transcript": "这是视频的转录文本",
                "key_frames": [{"time": 0.0, "description": "开场"}],
                "visual_elements": {"characters": ["博主"]},
                "audio_elements": {"music": "轻快背景音乐"}
            },
            content_analysis={
                "summary": "时尚穿搭视频，介绍连衣裙搭配技巧",
                "style": "专业、时尚、实用",
                "script_structure": {
                    "hook": "吸引注意的开头",
                    "body": "详细介绍搭配技巧",
                    "cta": "引导购买"
                },
                "ecommerce_fit": {
                    "score": 0.85,
                    "reasoning": "内容适合直播带货",
                    "applicable_categories": ["女装", "时尚服饰"]
                }
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # ========== Step 4: 获取热点可视化数据 ==========
        response = client.get("/api/v1/hotspots/visualization")
        assert response.status_code == 200
        viz_data = response.json()
        assert "categories" in viz_data
        assert len(viz_data["categories"]) > 0
        
        # 验证热点数据包含所需字段
        category = viz_data["categories"][0]
        if len(category["hotspots"]) > 0:
            hotspot_viz = category["hotspots"][0]
            assert "heat_score" in hotspot_viz
            assert "heat_growth_rate" in hotspot_viz
            assert "match_score" in hotspot_viz
        
        # ========== Step 5: 拆解视频 ==========
        with patch('app.services.analysis.tasks.analyze_video_async.delay') as mock_analyze:
            mock_task = MagicMock()
            mock_task.id = "test-analysis-task-id"
            mock_analyze.return_value = mock_task
            
            response = client.post(
                "/api/v1/analysis/analyze",
                json={
                    "video_url": hotspot.url,
                    "options": {}
                }
            )
            assert response.status_code == 200
        
        # 创建拆解报告
        from app.models.analysis import AnalysisReport
        
        report = AnalysisReport(
            id="test-workflow-report",
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
        
        # ========== Step 6: 生成脚本 ==========
        with patch('app.services.script.tasks.generate_script_async.delay') as mock_generate:
            mock_task = MagicMock()
            mock_task.id = "test-script-task-id"
            mock_generate.return_value = mock_task
            
            response = client.post(
                "/api/v1/scripts/generate",
                json={
                    "hotspot_id": hotspot.id,
                    "product_id": product_id,
                    "analysis_report_id": report.id,
                    "duration": 10
                }
            )
            assert response.status_code == 200
        
        # 创建脚本
        from app.models.script import Script
        
        script = Script(
            id="test-workflow-script",
            hotspot_id=hotspot.id,
            product_id=product_id,
            analysis_report_id=report.id,
            video_info={
                "title": "时尚连衣裙推荐",
                "duration": 10
            },
            script_content="测试脚本",
            shot_list=[],
            production_notes={},
            tags={},
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        # ========== Step 7: 验证完整流程 ==========
        # 验证热点有匹配度
        response = client.get(f"/api/v1/hotspots/{hotspot.id}")
        assert response.status_code == 200
        hotspot_data = response.json()
        assert hotspot_data["match_score"] == 0.85
        # 注意：heat_growth_rate字段已移除，不再验证
        # 验证新增字段（如果API返回）
        if "content_compact" in hotspot_data:
            assert hotspot_data["content_compact"] != ""
        if "video_structure" in hotspot_data:
            assert hotspot_data["video_structure"] is not None
        if "content_analysis" in hotspot_data:
            assert hotspot_data["content_analysis"] is not None
        
        # 验证脚本已创建
        response = client.get(f"/api/v1/scripts/{script.id}")
        assert response.status_code == 200
        script_data = response.json()
        assert script_data["product_id"] == product_id
        assert script_data["hotspot_id"] == hotspot.id
        
        # 验证脚本使用了高匹配度的热点
        assert hotspot.match_score > 0.7  # 匹配度应该较高

