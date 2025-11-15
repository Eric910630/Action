"""
视频拆解工作流集成测试
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.analysis.service import VideoAnalysisService
from app.models.analysis import AnalysisReport


class TestAnalysisWorkflow:
    """视频拆解完整工作流测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return VideoAnalysisService()
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(
        self,
        service: VideoAnalysisService,
        db_session
    ):
        """测试完整拆解工作流：分析 -> 解析 -> 提取技巧 -> 保存"""
        video_url = "https://test.com/video"
        
        # 1. 模拟拆解工具返回
        mock_result = {
            "status": "success",
            "data": {
                "video_info": {"title": "测试视频", "duration": "10秒"},
                "basic_info": {"theme": "测试主题"},
                "shot_table": [
                    {
                        "shot_number": 1,
                        "viral_technique": "快速切换"
                    }
                ],
                "golden_3s": {
                    "hook_type": "悬念钩子",
                    "opening_line": "测试开头"
                },
                "viral_formula": {
                    "formula_name": "反转公式",
                    "formula_structure": "测试结构"
                },
                "highlights": [],
                "keywords": {},
                "production_tips": {}
            }
        }
        
        with patch.object(
            service.analyzer_client,
            'analyze',
            new_callable=AsyncMock,
            return_value=mock_result
        ):
            # 2. 分析并保存
            report = await service.analyze_and_save(db_session, video_url)
            
            assert report.id is not None
            assert report.video_url == video_url
            
            # 3. 提取技巧
            techniques = service.extract_techniques({
                "shot_table": report.shot_table or [],
                "golden_3s": report.golden_3s or {},
                "viral_formula": report.viral_formula or {},
                "production_tips": report.production_tips or {},
                "highlights": report.highlights or []
            })
            
            assert len(techniques) > 0
            
            # 4. 验证保存的报告
            saved = db_session.query(AnalysisReport).filter(
                AnalysisReport.video_url == video_url
            ).first()
            assert saved is not None

