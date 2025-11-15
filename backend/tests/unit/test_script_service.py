"""
脚本生成服务单元测试
"""
import pytest
from unittest.mock import AsyncMock, patch
import json

from app.services.script.service import ScriptGeneratorService
from app.models.hotspot import Hotspot
from app.models.product import Product
from app.models.analysis import AnalysisReport


class TestScriptGeneratorService:
    """脚本生成服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return ScriptGeneratorService()
    
    @pytest.fixture
    def sample_hotspot(self, db_session):
        """创建示例热点"""
        import uuid
        from datetime import datetime
        
        # 使用唯一URL避免冲突
        hotspot = Hotspot(
            id=str(uuid.uuid4()),
            title="测试热点",
            url=f"https://test.com/hotspot-{uuid.uuid4()}",
            platform="douyin",
            tags=["测试", "热点"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        return hotspot
    
    @pytest.fixture
    def sample_product(self, db_session, sample_live_room_id: str):
        """创建示例商品"""
        import uuid
        from datetime import datetime
        
        product = Product(
            id=str(uuid.uuid4()),
            name="测试商品",
            brand="测试品牌",
            category="测试",
            live_room_id=sample_live_room_id,
            price=99.0,
            selling_points=["卖点1", "卖点2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(product)
        db_session.commit()
        return product
    
    @pytest.fixture
    def sample_analysis_report(self, db_session):
        """创建示例拆解报告"""
        import uuid
        from datetime import datetime
        
        report = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url="https://test.com/video",
            viral_formula={
                "formula_name": "反转公式",
                "formula_structure": "测试结构"
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
        return report
    
    def test_build_prompt(
        self,
        service: ScriptGeneratorService,
        sample_hotspot: Hotspot,
        sample_product: Product
    ):
        """测试构建提示词"""
        prompt = service.build_prompt(
            sample_hotspot,
            sample_product,
            None,
            duration=10
        )
        
        assert "测试热点" in prompt
        assert "测试商品" in prompt
        assert "10秒" in prompt
    
    def test_build_prompt_with_analysis(
        self,
        service: ScriptGeneratorService,
        sample_hotspot: Hotspot,
        sample_product: Product,
        sample_analysis_report: AnalysisReport
    ):
        """测试带拆解报告的提示词构建"""
        prompt = service.build_prompt(
            sample_hotspot,
            sample_product,
            sample_analysis_report,
            duration=10
        )
        
        assert "测试热点" in prompt
        assert "测试商品" in prompt
        assert "反转公式" in prompt or "爆款公式" in prompt
    
    @pytest.mark.asyncio
    async def test_generate_script_success(
        self,
        service: ScriptGeneratorService,
        sample_hotspot: Hotspot,
        sample_product: Product
    ):
        """测试成功生成脚本"""
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
                                "time_range": "0-10秒",
                                "shot_type": "中景",
                                "content": "商品展示",
                                "dialogue": "测试台词",
                                "action": "展示商品",
                                "music": "背景音乐",
                                "purpose": "吸引注意",
                                "shaping_point": "突出商品"
                            }
                        ],
                        "production_notes": {
                            "shooting_tips": ["注意光线"],
                            "editing_tips": ["快速切换"],
                            "key_points": ["突出价格"]
                        },
                        "tags": {
                            "recommended_tags": ["商品", "优惠"],
                            "recommended_topics": ["好物推荐"]
                        }
                    })
                }
            }]
        }
        
        # 如果使用Agent模式，需要Mock Agent的execute方法
        if hasattr(service, 'script_agent'):
            mock_result = {
                "video_info": {"title": "测试视频"},
                "script_content": "测试脚本",
                "shot_list": []
            }
            with patch.object(
                service.script_agent,
                'execute',
                new_callable=AsyncMock,
                return_value=mock_result
            ) as mock_execute:
                result = await service.generate_script(
                    sample_hotspot,
                    sample_product,
                    None,
                    duration=10
                )
                assert "video_info" in result
                assert "script_content" in result
                assert "shot_list" in result
                mock_execute.assert_called_once()
        else:
            # 传统模式：Mock DeepSeek API响应
            with patch.object(
                service.deepseek_client,
                'generate',
                new_callable=AsyncMock,
                return_value=mock_response
            ):
                result = await service.generate_script(
                    sample_hotspot,
                    sample_product,
                    None,
                    duration=10
                )
                
                assert "video_info" in result
                assert "script_content" in result
                assert "shot_list" in result
    
    def test_parse_script_response_valid_json(
        self,
        service: ScriptGeneratorService
    ):
        """测试解析有效的JSON响应"""
        content = json.dumps({
            "video_info": {"title": "测试"},
            "script_content": "测试内容",
            "shot_list": []
        })
        
        parsed = service.parse_script_response(content)
        
        assert "video_info" in parsed
        assert "script_content" in parsed
    
    def test_parse_script_response_invalid_json(
        self,
        service: ScriptGeneratorService
    ):
        """测试解析无效JSON（降级处理）"""
        content = "这不是JSON格式的内容"
        
        parsed = service.parse_script_response(content)
        
        # 应该返回默认结构
        assert "video_info" in parsed
        assert "script_content" in parsed
    
    def test_generate_shot_list(
        self,
        service: ScriptGeneratorService
    ):
        """测试生成分镜列表"""
        script_data = {
            "video_info": {"duration": 10},
            "script_content": "测试内容",
            "shot_list": [
                {
                    "shot_number": 1,
                    "time_range": "0-10秒",
                    "content": "测试"
                }
            ]
        }
        
        shot_list = service.generate_shot_list(script_data)
        
        assert len(shot_list) > 0
        assert shot_list[0]["shot_number"] == 1
    
    def test_generate_shot_list_empty(
        self,
        service: ScriptGeneratorService
    ):
        """测试生成空分镜列表（应该创建默认分镜）"""
        script_data = {
            "video_info": {"duration": 10},
            "script_content": "测试内容",
            "shot_list": []
        }
        
        shot_list = service.generate_shot_list(script_data)
        
        # 应该创建至少一个默认分镜
        assert len(shot_list) > 0
    
    def test_save_script(
        self,
        service: ScriptGeneratorService,
        db_session,
        sample_hotspot: Hotspot,
        sample_product: Product
    ):
        """测试保存脚本"""
        script_data = {
            "video_info": {"title": "测试视频"},
            "script_content": "测试脚本",
            "shot_list": [],
            "production_notes": {},
            "tags": {}
        }
        
        script = service.save_script(
            db_session,
            sample_hotspot.id,
            sample_product.id,
            None,
            script_data,
            status="draft"
        )
        
        assert script.id is not None
        assert script.status == "draft"
        assert script.hotspot_id == sample_hotspot.id
        assert script.product_id == sample_product.id
    
    def test_get_optimization_suggestions(
        self,
        service: ScriptGeneratorService,
        db_session,
        sample_product: Product
    ):
        """测试获取优化建议"""
        from app.models.script import Script
        import uuid
        from datetime import datetime
        
        # 创建脚本
        script = Script(
            id=str(uuid.uuid4()),
            product_id=sample_product.id,
            video_info={"duration": 3},  # 时长过短
            shot_list=[],  # 缺少分镜
            tags={},  # 缺少标签
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(script)
        db_session.commit()
        
        suggestions = service.get_optimization_suggestions(script)
        
        assert len(suggestions) > 0
        # 应该有时长警告
        assert any(s["type"] == "duration" for s in suggestions)

