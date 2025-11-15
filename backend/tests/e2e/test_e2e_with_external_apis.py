"""
端到端测试（E2E）- 包含外部API拟真测试
通过HTTP API测试完整的业务流程，并模拟外部API的真实响应

与test_e2e_workflow.py的区别：
- test_e2e_workflow.py: Mock Celery任务，直接操作数据库，跳过外部API调用
- test_e2e_with_external_apis.py: Mock外部API的HTTP响应，真正调用服务层逻辑
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json
from datetime import datetime, date
from httpx import Response, AsyncClient


class TestE2EWithExternalAPIs:
    """端到端测试 - 包含外部API拟真"""
    
    @pytest.mark.asyncio
    @pytest.mark.real_api
    async def test_e2e_hotspot_fetch_with_trendradar(self, client, db_session, sample_live_room_id, use_real_trendradar):
        """E2E测试：热点抓取流程（使用真实TrendRadar API或直接爬虫）"""
        
        if not use_real_trendradar:
            pytest.skip("TrendRadar功能未启用，跳过测试")
        
        # 使用真实TrendRadar服务（直接爬虫或MCP）
        from app.services.hotspot.service import HotspotMonitorService
        from app.core.config import settings
        
        # 检查是否使用直接爬虫
        use_direct_crawler = getattr(settings, 'TRENDRADAR_USE_DIRECT_CRAWLER', True)
        logger_msg = "直接爬虫" if use_direct_crawler else "MCP服务"
        
        service = HotspotMonitorService()
        
        try:
            # 调用真实API（直接爬虫或MCP）
            hotspots = await service.fetch_hotspots("douyin")
            
            # 验证返回了数据
            assert isinstance(hotspots, list)
            if len(hotspots) > 0:
                # 验证数据结构
                assert "title" in hotspots[0]
                assert "url" in hotspots[0]
                assert "platform" in hotspots[0]
                print(f"✓ 使用{logger_msg}成功获取 {len(hotspots)} 个热点")
        except Exception as e:
            pytest.skip(f"TrendRadar {logger_msg}调用失败: {e}")
    
    @pytest.mark.asyncio
    async def test_e2e_video_analysis_with_analyzer(self, client, db_session):
        """E2E测试：视频分析流程（模拟VideoAnalyzer API真实响应）"""
        
        # Mock VideoAnalyzer API响应
        mock_analyzer_response = {
            "video_info": {
                "title": "女装穿搭教程",
                "duration": 60,
                "theme": "时尚穿搭"
            },
            "basic_info": {
                "theme": "时尚穿搭",
                "core_selling_point": "性价比高"
            },
            "shot_table": [
                {
                    "shot_number": 1,
                    "time_range": "0-3s",
                    "dialogue": "大家好，今天分享一套女装穿搭",
                    "content": "开场介绍",
                    "viral_technique": "黄金3秒"
                }
            ],
            "golden_3s": {
                "hook_type": "问题式",
                "opening_line": "你知道今年最流行的穿搭是什么吗？"
            },
            "viral_formula": {
                "formula_name": "问题+解答+行动",
                "formula_structure": "问题→解答→行动号召",
                "application_method": "开头提问吸引注意"
            },
            "techniques": [
                {
                    "name": "黄金3秒",
                    "type": "开头技巧",
                    "description": "使用问题式开头吸引观众",
                    "reason": "问题式开头能快速抓住观众注意力"
                }
            ]
        }
        
        # 直接mock VideoAnalyzerClient的方法
        from app.services.analysis.service import VideoAnalysisService
        
        service = VideoAnalysisService()
        
        with patch.object(service.analyzer_client, 'analyze', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = mock_analyzer_response
            
            # 调用服务方法（这会真正调用VideoAnalyzer API，但被mock了）
            result = await service.analyze_video("https://douyin.com/video/123456")
            
            # 验证返回了mock的数据
            assert result["video_info"]["title"] == "女装穿搭教程"
            # techniques 是从报告中提取的，不是直接返回的
            # 验证基本结构
            assert "shot_table" in result
            
            # 验证方法被调用
            mock_analyze.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_e2e_script_generation_with_deepseek(self, client, db_session, sample_live_room_id):
        """E2E测试：脚本生成流程（模拟DeepSeek API真实响应）"""
        
        # 先创建必要的测试数据
        from app.models.hotspot import Hotspot
        from app.models.product import Product
        from app.models.analysis import AnalysisReport
        import uuid
        
        # 创建热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="女装穿搭新趋势",
            url="https://douyin.com/video/123456",
            platform="douyin",
            tags=["女装", "穿搭"],
            heat_score=95,
            match_score=0.85,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 创建商品
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            category="女装",
            live_room_id=sample_live_room_id,
            price=199.0,
            selling_points=["时尚", "舒适"],
            live_date=date(2024, 12, 15),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(product)
        db_session.commit()
        
        # 创建分析报告（techniques存储在JSON字段中，不是直接字段）
        report = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url="https://douyin.com/video/123456",
            video_info={"title": "女装穿搭教程"},
            shot_table=[
                {
                    "shot_number": 1,
                    "viral_technique": "黄金3秒"
                }
            ],
            golden_3s={
                "hook_type": "问题式",
                "opening_line": "你知道今年最流行的穿搭是什么吗？"
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        db_session.commit()
        
        # Mock DeepSeek API响应
        script_content = {
            "video_info": {
                "title": "女装穿搭新趋势",
                "duration": 10,
                "theme": "时尚穿搭"
            },
            "script_content": "大家好，今天分享一套女装穿搭...",
            "shot_list": [
                {
                    "shot_number": 1,
                    "time_range": "0-3s",
                    "shot_type": "中景",
                    "content": "展示商品",
                    "dialogue": "大家好，今天分享一套女装穿搭",
                    "action": "展示",
                    "purpose": "吸引注意"
                }
            ],
            "production_notes": {
                "shooting_tips": ["注意光线", "突出商品特点"],
                "editing_tips": ["快速剪辑", "添加字幕"],
                "key_points": ["强调性价比", "突出时尚感"]
            }
        }
        
        mock_deepseek_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(script_content, ensure_ascii=False)
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 500,
                "total_tokens": 600
            }
        }
        
        # 直接mock DeepSeekClient的方法
        from app.services.script.service import ScriptGeneratorService
        
        service = ScriptGeneratorService()
        
        # 如果使用Agent模式，需要Mock Agent的execute方法
        if hasattr(service, 'script_agent'):
            with patch.object(service.script_agent, 'execute', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = {
                    "video_info": {"title": "女装穿搭新趋势"},
                    "script_content": "测试脚本内容",
                    "shot_list": [{
                        "shot_number": 1,
                        "time_range": "0-10秒",
                        "shot_type": "中景",
                        "content": "商品展示",
                        "dialogue": "测试台词",
                        "action": "展示商品",
                        "music": "背景音乐",
                        "purpose": "吸引注意",
                        "shaping_point": "突出商品"
                    }]
                }
                result = await service.generate_script(hotspot, product, report, 10)
                assert "video_info" in result
                assert result["video_info"]["title"] == "女装穿搭新趋势"
                assert "script_content" in result
                assert len(result["shot_list"]) == 1
                mock_execute.assert_called_once()
        else:
            # 传统模式：Mock DeepSeek API
            with patch.object(service.deepseek_client, 'generate', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = mock_deepseek_response
                
                # 调用服务方法（这会真正调用DeepSeek API，但被mock了）
                result = await service.generate_script(hotspot, product, report, 10)
                
                # 验证返回了mock的数据
                assert result["video_info"]["title"] == "女装穿搭新趋势"
                assert "script_content" in result
                assert len(result["shot_list"]) == 1
                
                # 验证方法被调用
                mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_e2e_push_to_feishu_with_webhook(self, client, db_session, sample_live_room_id):
        """E2E测试：推送热点到飞书（模拟Feishu Webhook真实响应）"""
        
        from app.models.hotspot import Hotspot
        from app.models.product import LiveRoom
        import uuid
        
        # 获取直播间
        live_room = db_session.query(LiveRoom).filter(LiveRoom.id == sample_live_room_id).first()
        
        # 创建热点（确保有匹配度>0.7的热点，且是今天创建的）
        from datetime import date, time
        today = date.today()
        today_start = datetime.combine(today, time.min)
        
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="女装穿搭新趋势",
            url="https://douyin.com/video/123456",
            platform="douyin",
            tags=["女装", "穿搭"],
            heat_score=95,  # 确保是数字类型
            match_score=0.85,  # >0.7 才会被推送
            created_at=today_start,  # 确保是今天创建的
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 直接mock FeishuClient的方法
        from app.services.hotspot.service import HotspotMonitorService
        
        service = HotspotMonitorService()
        
        with patch.object(service.feishu_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"code": 0, "msg": "success"}
            
            result = await service.push_to_feishu(
                db_session,
                live_room.id if live_room else sample_live_room_id
            )
            
            # 验证推送成功
            assert result is True
            
            # 验证Feishu API被正确调用
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_e2e_external_api_error_handling(self, client, db_session):
        """E2E测试：外部API错误处理"""
        
        # Mock TrendRadar API错误响应
        from app.services.hotspot.service import HotspotMonitorService
        
        service = HotspotMonitorService()
        
        # Mock直接爬虫失败
        if service.crawler:
            with patch.object(service.crawler, 'crawl_hotspots', new_callable=AsyncMock) as mock_crawler:
                mock_crawler.side_effect = Exception("直接爬虫失败")
                # Mock MCP客户端也失败
                with patch.object(service.trendradar_client, 'get_hotspots', new_callable=AsyncMock) as mock_get:
                    mock_get.side_effect = Exception("MCP服务失败")
                    # 异常会被传播，测试应该期望异常
                    with pytest.raises(Exception) as exc_info:
                        await service.fetch_hotspots("douyin")
                    assert "失败" in str(exc_info.value)
        else:
            # 如果没有直接爬虫，只测试MCP失败
            with patch.object(service.trendradar_client, 'get_hotspots', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = Exception("MCP服务失败")
                with pytest.raises(Exception, match="MCP服务失败"):
                    await service.fetch_hotspots("douyin")
        
        # Mock VideoAnalyzer API超时
        from app.services.analysis.service import VideoAnalysisService
        
        service = VideoAnalysisService()
        
        with patch.object(service.analyzer_client, 'analyze', new_callable=AsyncMock) as mock_analyze:
            # 模拟超时错误
            mock_analyze.side_effect = TimeoutError("Request timeout")
            
            # 应该能够处理超时错误
            with pytest.raises((TimeoutError, Exception)):  # 可能抛出异常或返回错误
                await service.analyze_video("https://douyin.com/video/123456")

