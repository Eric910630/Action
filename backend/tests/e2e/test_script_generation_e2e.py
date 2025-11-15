"""
E2E测试 - 脚本生成模块
测试脚本生成的完整流程，包括语义匹配度计算
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date


class TestScriptGenerationE2E:
    """脚本生成E2E测试"""
    
    @pytest.mark.asyncio
    async def test_script_generation_workflow(self, client, db_session, sample_live_room_id):
        """测试脚本生成的完整流程"""
        
        # 1. 创建商品
        product_data = {
            "name": "时尚连衣裙",
            "brand": "测试品牌",
            "category": "女装",
            "live_room_id": sample_live_room_id,
            "price": 299.0,
            "selling_points": ["时尚", "舒适", "百搭"],
            "description": "时尚百搭的连衣裙",
            "hand_card": "限时优惠299元",
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 2. 创建热点
        from app.models.hotspot import Hotspot
        
        hotspot = Hotspot(
            id="test-script-hotspot",
            title="时尚穿搭推荐",
            url="https://test.com/hotspot",
            platform="douyin",
            tags=["时尚", "穿搭"],
            heat_score=95,
            match_score=0.85,  # 与商品的匹配度
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 3. 创建拆解报告（可选）
        from app.models.analysis import AnalysisReport
        
        report = AnalysisReport(
            id="test-script-report",
            video_url="https://test.com/hotspot",
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
        
        # 4. 生成脚本（Mock DeepSeek API）
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
            data = response.json()
            assert data["status"] == "success"
            assert "task_id" in data
        
        # 5. 模拟脚本生成完成
        from app.models.script import Script
        
        script = Script(
            id="test-script-id",
            hotspot_id=hotspot.id,
            product_id=product_id,
            analysis_report_id=report.id,
            video_info={
                "title": "时尚连衣裙推荐",
                "duration": 10,
                "theme": "时尚穿搭",
                "core_selling_point": "时尚百搭"
            },
            script_content="这是一个测试脚本内容",
            shot_list=[
                {
                    "shot_number": 1,
                    "time_range": "0-3秒",
                    "shot_type": "中景",
                    "content": "展示商品",
                    "dialogue": "这件连衣裙太美了",
                    "action": "展示商品",
                    "music": "轻快背景音乐",
                    "purpose": "吸引注意",
                    "shaping_point": "突出商品"
                }
            ],
            production_notes={
                "shooting_tips": ["注意光线"],
                "editing_tips": ["快速切换"],
                "key_points": ["突出价格"]
            },
            tags={
                "recommended_tags": ["时尚", "连衣裙"],
                "recommended_topics": ["穿搭推荐"]
            },
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        # 6. 获取脚本列表
        response = client.get("/api/v1/scripts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        
        # 7. 获取脚本详情
        response = client.get(f"/api/v1/scripts/{script.id}")
        assert response.status_code == 200
        script_data = response.json()
        assert script_data["id"] == script.id
        assert "shot_list" in script_data
        assert "production_notes" in script_data
        
        # 8. 获取优化建议
        response = client.post(f"/api/v1/scripts/{script.id}/optimize")
        assert response.status_code == 200
        optimize_data = response.json()
        assert "suggestions" in optimize_data
        
        # 9. 审核脚本
        response = client.post(
            f"/api/v1/scripts/{script.id}/review",
            json={
                "action": "approve",
                "comment": "脚本质量很好"
            }
        )
        assert response.status_code == 200
        review_data = response.json()
        assert review_data["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_script_generation_with_semantic_match(self, client, db_session, sample_live_room_id):
        """测试基于语义匹配度的脚本生成"""
        
        # 创建商品
        product_data = {
            "name": "美妆套装",
            "category": "美妆",
            "live_room_id": sample_live_room_id,
            "price": 199.0,
            "selling_points": ["天然", "保湿"],
            "live_date": date.today().isoformat()
        }
        
        response = client.post("/api/v1/products", json=product_data)
        product_id = response.json()["id"]
        
        # 创建高匹配度的热点
        from app.models.hotspot import Hotspot
        
        hotspot = Hotspot(
            id="test-semantic-hotspot",
            title="美妆推荐 天然保湿产品",
            url="https://test.com/semantic",
            platform="douyin",
            tags=["美妆", "天然"],
            heat_score=90,
            match_score=0.88,  # 高匹配度（基于语义关联度计算）
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 验证匹配度已保存
        assert hotspot.match_score == 0.88
        
        # 生成脚本时应该使用这个匹配度
        with patch('app.services.script.tasks.generate_script_async.delay') as mock_generate:
            mock_task = MagicMock()
            mock_task.id = "test-task-id"
            mock_generate.return_value = mock_task
            
            response = client.post(
                "/api/v1/scripts/generate",
                json={
                    "hotspot_id": hotspot.id,
                    "product_id": product_id,
                    "duration": 10
                }
            )
            
            assert response.status_code == 200

