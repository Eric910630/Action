"""
脚本生成工作流集成测试
"""
import pytest
from unittest.mock import AsyncMock, patch
import json

from app.services.script.service import ScriptGeneratorService
from app.models.hotspot import Hotspot
from app.models.product import Product
from app.models.analysis import AnalysisReport
from app.models.script import Script


class TestScriptWorkflow:
    """脚本生成完整工作流测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return ScriptGeneratorService()
    
    @pytest.fixture
    def complete_test_data(self, db_session, sample_live_room_id: str):
        """创建完整的测试数据（热点+商品+拆解报告）"""
        import uuid
        from datetime import datetime
        
        # 创建热点
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url="https://test.com/hotspot",
            platform="douyin",
            tags=["测试"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        
        # 创建商品
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            category="测试",
            live_room_id=sample_live_room_id,
            price=99.0,
            selling_points=["卖点1", "卖点2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(product)
        
        # 创建拆解报告
        report = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url="https://test.com/video",
            viral_formula={
                "formula_name": "反转公式",
                "formula_structure": "测试结构",
                "application_method": "测试方法"
            },
            golden_3s={
                "hook_type": "悬念钩子",
                "opening_line": "测试开头"
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        
        db_session.commit()
        
        return {
            "hotspot": hotspot,
            "product": product,
            "report": report
        }
    
    @pytest.mark.asyncio
    async def test_complete_script_generation_workflow(
        self,
        service: ScriptGeneratorService,
        db_session,
        complete_test_data: dict
    ):
        """测试完整脚本生成工作流：构建提示词 -> 生成 -> 解析 -> 保存"""
        hotspot = complete_test_data["hotspot"]
        product = complete_test_data["product"]
        report = complete_test_data["report"]
        
        # 1. 构建提示词
        prompt = service.build_prompt(hotspot, product, report, duration=10)
        assert "测试热点" in prompt
        assert "测试商品" in prompt
        
        # 2. 模拟DeepSeek返回
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "video_info": {
                            "title": "测试视频",
                            "duration": 10,
                            "theme": "测试主题",
                            "core_selling_point": "价格优惠"
                        },
                        "script_content": "测试脚本内容",
                        "shot_list": [
                            {
                                "shot_number": 1,
                                "time_range": "0-5秒",
                                "shot_type": "中景",
                                "content": "商品展示",
                                "dialogue": "测试台词",
                                "action": "展示商品",
                                "music": "背景音乐",
                                "purpose": "吸引注意",
                                "shaping_point": "突出商品"
                            },
                            {
                                "shot_number": 2,
                                "time_range": "5-10秒",
                                "shot_type": "特写",
                                "content": "价格展示",
                                "dialogue": "仅需99元",
                                "action": "展示价格",
                                "music": "背景音乐",
                                "purpose": "突出优惠",
                                "shaping_point": "价格优势"
                            }
                        ],
                        "production_notes": {
                            "shooting_tips": ["注意光线", "突出商品特点"],
                            "editing_tips": ["快速切换", "节奏紧凑"],
                            "key_points": ["突出价格", "强调优惠"]
                        },
                        "tags": {
                            "recommended_tags": ["商品", "优惠", "好物"],
                            "recommended_topics": ["好物推荐", "限时优惠"]
                        }
                    })
                }
            }]
        }
        
        with patch.object(
            service.deepseek_client,
            'generate',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            # 3. 生成脚本
            script_data = await service.generate_script(
                hotspot, product, report, duration=10
            )
            
            assert "video_info" in script_data
            assert "script_content" in script_data
            assert len(script_data["shot_list"]) == 2
            
            # 4. 生成分镜列表
            shot_list = service.generate_shot_list(script_data)
            assert len(shot_list) == 2
            
            # 5. 保存脚本
            script = service.save_script(
                db_session,
                hotspot.id,
                product.id,
                report.id,
                script_data,
                status="draft"
            )
            
            assert script.id is not None
            assert script.hotspot_id == hotspot.id
            assert script.product_id == product.id
            assert script.analysis_report_id == report.id
            
            # 6. 获取优化建议
            suggestions = service.get_optimization_suggestions(script)
            # 应该有优化建议（至少检查时长、分镜等）
            assert isinstance(suggestions, list)

