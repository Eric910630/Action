"""
端到端测试（E2E）
通过HTTP API测试完整的业务流程，模拟真实用户操作
"""
import pytest
from unittest.mock import AsyncMock, patch
import json
from datetime import datetime, date


class TestE2EFullWorkflow:
    """端到端完整业务流程测试"""
    
    @pytest.mark.asyncio
    async def test_e2e_hotspot_to_script_workflow(self, client, db_session, sample_live_room_id):
        """E2E测试：从热点发现到脚本生成的完整流程（通过API）"""
        
        # ========== Step 1: 获取直播间列表 ==========
        response = client.get("/api/v1/live-rooms")
        assert response.status_code == 200
        live_rooms = response.json()["items"]
        # 使用fixture提供的直播间ID
        live_room_id = sample_live_room_id
        
        # ========== Step 2: 创建商品 ==========
        product_data = {
            "name": "E2E测试商品",
            "brand": "测试品牌",
            "category": "女装",
            "live_room_id": live_room_id,
            "price": 199.0,
            "selling_points": ["时尚", "舒适", "性价比高"],
            "hand_card": "限时优惠，仅需199元",
            "live_date": "2024-12-15"
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        assert product_id is not None
        
        # 验证商品已创建
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert product["name"] == "E2E测试商品"
        
        # ========== Step 3: 触发热点抓取（Mock外部服务，测试多平台抓取）==========
        with patch('app.services.hotspot.tasks.fetch_daily_hotspots.delay') as mock_fetch:
            mock_fetch.return_value.id = "test-task-id"
            
            # 不传platform参数，测试多平台抓取（douyin, zhihu, weibo, bilibili）
            response = client.post("/api/v1/hotspots/fetch")
            assert response.status_code == 200
            assert "task_id" in response.json()
        
        # ========== Step 4: 手动创建热点数据（模拟已抓取的热点）==========
        from app.models.hotspot import Hotspot
        import uuid
        
        # 使用fixture提供的db_session
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="E2E测试热点-女装穿搭",
            url="https://test.com/e2e-hotspot",
            platform="douyin",
            tags=["女装", "穿搭", "时尚"],
            heat_score=95,
            match_score=0.85,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        hotspot_id = hotspot.id
        
        # 验证热点可通过API获取
        response = client.get(f"/api/v1/hotspots/{hotspot_id}")
        assert response.status_code == 200
        hotspot_data = response.json()
        assert hotspot_data["title"] == "E2E测试热点-女装穿搭"
        
        # ========== Step 5: 分析视频（Mock外部服务）==========
        with patch('app.services.analysis.tasks.analyze_video_async.delay') as mock_analyze:
            mock_analyze.return_value.id = "test-analyze-task-id"
            
            analyze_request = {
                "video_url": "https://test.com/e2e-video",
                "options": {}
            }
            response = client.post("/api/v1/analysis/analyze", json=analyze_request)
            assert response.status_code == 200
            assert "task_id" in response.json()
        
        # ========== Step 6: 手动创建拆解报告（模拟已分析的报告）==========
        from app.models.analysis import AnalysisReport
        
        report = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url="https://test.com/e2e-video",
            video_info={"title": "E2E测试视频"},
            basic_info={"theme": "时尚穿搭"},
            shot_table=[
                {
                    "shot_number": 1,
                    "viral_technique": "快速切换"
                }
            ],
            golden_3s={
                "hook_type": "悬念钩子",
                "opening_line": "这件衣服太美了"
            },
            viral_formula={
                "formula_name": "反转公式",
                "formula_structure": "测试结构",
                "application_method": "测试方法"
            },
            highlights=[],
            keywords={},
            production_tips={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        db_session.commit()
        report_id = report.id
        
        # 验证报告可通过API获取
        response = client.get(f"/api/v1/analysis/reports/{report_id}")
        assert response.status_code == 200
        report_data = response.json()
        assert "techniques" in report_data
        assert len(report_data["techniques"]) > 0
        
        # ========== Step 7: 生成脚本（Mock外部服务）==========
        with patch('app.services.script.tasks.generate_script_async.delay') as mock_generate:
            mock_generate.return_value.id = "test-script-task-id"
            
            script_request = {
                "hotspot_id": hotspot_id,
                "product_id": product_id,
                "analysis_report_id": report_id,
                "duration": 10
            }
            response = client.post("/api/v1/scripts/generate", json=script_request)
            assert response.status_code == 200
            assert "task_id" in response.json()
        
        # ========== Step 8: 手动创建脚本（模拟已生成的脚本）==========
        from app.models.script import Script
        
        script = Script(
            id=str(uuid.uuid4()),
            hotspot_id=hotspot_id,
            product_id=product_id,
            analysis_report_id=report_id,
            video_info={
                "title": "E2E测试脚本",
                "duration": 10,
                "theme": "时尚穿搭",
                "core_selling_point": "限时优惠199元"
            },
            script_content="E2E测试脚本内容：结合热点展示商品",
            shot_list=[
                {
                    "shot_number": 1,
                    "time_range": "0-5秒",
                    "shot_type": "中景",
                    "content": "展示商品",
                    "dialogue": "这件连衣裙太美了",
                    "action": "展示商品",
                    "music": "轻快背景音乐",
                    "purpose": "吸引注意",
                    "shaping_point": "突出商品"
                },
                {
                    "shot_number": 2,
                    "time_range": "5-10秒",
                    "shot_type": "特写",
                    "content": "价格展示",
                    "dialogue": "限时优惠，仅需199元",
                    "action": "展示价格",
                    "music": "轻快背景音乐",
                    "purpose": "突出优惠",
                    "shaping_point": "价格优势"
                }
            ],
            production_notes={
                "shooting_tips": ["注意光线", "突出商品特点"],
                "editing_tips": ["快速切换", "节奏紧凑"],
                "key_points": ["突出价格", "强调优惠"]
            },
            tags={
                "recommended_tags": ["女装", "连衣裙", "优惠"],
                "recommended_topics": ["好物推荐", "限时优惠"]
            },
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        script_id = script.id
        
        # ========== Step 9: 通过API获取脚本详情 ==========
        response = client.get(f"/api/v1/scripts/{script_id}")
        assert response.status_code == 200
        script_data = response.json()
        assert script_data["id"] == script_id
        assert script_data["hotspot_id"] == hotspot_id
        assert script_data["product_id"] == product_id
        assert script_data["analysis_report_id"] == report_id
        assert script_data["status"] == "draft"
        assert len(script_data["shot_list"]) == 2
        
        # ========== Step 10: 获取脚本优化建议 ==========
        response = client.post(f"/api/v1/scripts/{script_id}/optimize")
        assert response.status_code == 200
        optimize_data = response.json()
        assert "suggestions" in optimize_data
        
        # ========== Step 11: 审核脚本 ==========
        review_request = {
            "action": "approve",
            "comment": "E2E测试审核通过"
        }
        response = client.post(f"/api/v1/scripts/{script_id}/review", json=review_request)
        assert response.status_code == 200
        review_data = response.json()
        assert review_data["status"] == "approved"
        
        # ========== Step 12: 验证脚本状态已更新 ==========
        response = client.get(f"/api/v1/scripts/{script_id}")
        assert response.status_code == 200
        updated_script = response.json()
        assert updated_script["status"] == "approved"
        
        # ========== Step 13: 验证完整数据链路 ==========
        # 验证热点
        response = client.get(f"/api/v1/hotspots/{hotspot_id}")
        assert response.status_code == 200
        
        # 验证商品
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        
        # 验证报告
        response = client.get(f"/api/v1/analysis/reports/{report_id}")
        assert response.status_code == 200
        
        # 验证脚本列表（按商品筛选）
        response = client.get(f"/api/v1/scripts?product_id={product_id}")
        assert response.status_code == 200
        scripts_list = response.json()
        assert scripts_list["total"] >= 1
        assert any(s["id"] == script_id for s in scripts_list["items"])
        
        # ========== Step 14: 验证关联关系 ==========
        # 通过商品获取脚本
        response = client.get(f"/api/v1/scripts?product_id={product_id}&status=approved")
        assert response.status_code == 200
        approved_scripts = response.json()
        assert approved_scripts["total"] >= 1


class TestE2EHotspotWorkflow:
    """E2E测试：热点监控完整流程"""
    
    def test_e2e_hotspot_discovery_workflow(self, client, db_session, sample_live_room_id):
        """E2E测试：热点发现完整流程（通过API）"""
        
        # 1. 获取直播间
        response = client.get("/api/v1/live-rooms")
        assert response.status_code == 200
        live_rooms = response.json()["items"]
        # 使用fixture提供的直播间ID
        live_room_id = sample_live_room_id
        
        # 2. 触发热点抓取（测试多平台抓取）
        with patch('app.services.hotspot.tasks.fetch_daily_hotspots.delay') as mock_fetch:
            mock_fetch.return_value.id = "test-task-id"
            
            # 不传platform参数，测试多平台抓取
            response = client.post("/api/v1/hotspots/fetch")
            assert response.status_code == 200
        
        # 3. 创建测试热点
        from app.models.hotspot import Hotspot
        import uuid
        
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="E2E热点测试",
            url="https://test.com/e2e-hotspot-discovery",
            platform="douyin",
            tags=["测试"],
            heat_score=90,
            match_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        hotspot_id = hotspot.id
        
        # 4. 通过API获取热点列表
        response = client.get("/api/v1/hotspots")
        assert response.status_code == 200
        hotspots_list = response.json()
        assert hotspots_list["total"] >= 1
        
        # 5. 通过API获取热点详情
        response = client.get(f"/api/v1/hotspots/{hotspot_id}")
        assert response.status_code == 200
        hotspot_data = response.json()
        assert hotspot_data["id"] == hotspot_id
        
        # 6. 通过API筛选热点
        filter_request = {
            "keywords": ["测试"],
            "live_room_id": live_room_id
        }
        response = client.post("/api/v1/hotspots/filter", json=filter_request)
        assert response.status_code == 200
        filtered_data = response.json()
        assert "filtered_count" in filtered_data
        assert "items" in filtered_data


class TestE2EProductWorkflow:
    """E2E测试：商品管理完整流程"""
    
    def test_e2e_product_management_workflow(self, client, sample_live_room_id):
        """E2E测试：商品管理完整流程（通过API）"""
        
        # 1. 获取直播间
        response = client.get("/api/v1/live-rooms")
        assert response.status_code == 200
        live_rooms = response.json()["items"]
        # 使用fixture提供的直播间ID
        live_room_id = sample_live_room_id
        
        # 2. 创建商品
        product_data = {
            "name": "E2E商品管理测试",
            "brand": "测试品牌",
            "category": "测试",
            "live_room_id": live_room_id,
            "price": 99.0,
            "selling_points": ["卖点1", "卖点2"],
            "live_date": "2024-12-15"
        }
        
        response = client.post("/api/v1/products", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]
        
        # 3. 获取商品列表
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        products_list = response.json()
        assert products_list["total"] >= 1
        
        # 4. 按直播间筛选商品
        response = client.get(f"/api/v1/products?live_room_id={live_room_id}")
        assert response.status_code == 200
        filtered_products = response.json()
        assert filtered_products["total"] >= 1
        
        # 5. 获取商品详情
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert product["name"] == "E2E商品管理测试"
        
        # 6. 更新商品
        update_data = {
            "name": "E2E商品管理测试-已更新",
            "price": 199.0
        }
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 200
        
        # 7. 验证更新
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        updated_product = response.json()
        assert updated_product["name"] == "E2E商品管理测试-已更新"
        assert updated_product["price"] == 199.0

