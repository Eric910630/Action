"""
视频拆解服务单元测试
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.analysis.service import VideoAnalysisService
from app.models.analysis import AnalysisReport


class TestVideoAnalysisService:
    """视频拆解服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return VideoAnalysisService()
    
    @pytest.mark.asyncio
    async def test_analyze_video_success(self, service: VideoAnalysisService):
        """测试成功分析视频"""
        mock_result = {
            "status": "success",
            "data": {
                "video_info": {"title": "测试视频"},
                "basic_info": {"theme": "测试主题"},
                "shot_table": []
            }
        }
        
        with patch.object(
            service.analyzer_client,
            'analyze',
            new_callable=AsyncMock,
            return_value=mock_result
        ):
            result = await service.analyze_video("https://test.com/video")
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_analyze_video_failure(self, service: VideoAnalysisService):
        """测试分析视频失败"""
        with patch.object(
            service.analyzer_client,
            'analyze',
            new_callable=AsyncMock,
            side_effect=Exception("分析失败")
        ):
            with pytest.raises(Exception):
                await service.analyze_video("https://test.com/video")
    
    def test_parse_report(self, service: VideoAnalysisService):
        """测试解析拆解报告"""
        raw_data = {
            "data": {
                "video_info": {"title": "测试视频"},
                "basic_info": {"theme": "测试主题"},
                "shot_table": [{"shot_number": 1}],
                "golden_3s": {"opening_line": "测试开头"},
                "highlights": [],
                "viral_formula": {},
                "keywords": {},
                "production_tips": {}
            }
        }
        
        parsed = service.parse_report(raw_data)
        
        assert "video_info" in parsed
        assert "basic_info" in parsed
        assert "shot_table" in parsed
        assert len(parsed["shot_table"]) == 1
    
    def test_extract_techniques(self, service: VideoAnalysisService):
        """测试提取爆款技巧"""
        report = {
            "shot_table": [
                {"viral_technique": "快速切换"}
            ],
            "golden_3s": {
                "hook_type": "悬念钩子",
                "opening_line": "测试开头"
            },
            "viral_formula": {
                "formula_name": "反转公式",
                "formula_structure": "测试结构",
                "application_method": "测试方法"
            },
            "production_tips": {
                "shooting_tips": ["拍摄技巧1"],
                "editing_tips": ["剪辑技巧1"]
            },
            "highlights": [
                {
                    "name": "亮点1",
                    "description": "描述",
                    "viral_reason": "原因"
                }
            ]
        }
        
        techniques = service.extract_techniques(report)
        
        assert len(techniques) > 0
        assert any(t["type"] == "shot" for t in techniques)
        assert any(t["type"] == "hook" for t in techniques)
        assert any(t["type"] == "formula" for t in techniques)
    
    def test_save_report_new(self, service: VideoAnalysisService, db_session):
        """测试保存新报告"""
        report_data = {
            "video_info": {"title": "测试视频"},
            "basic_info": {"theme": "测试主题"},
            "shot_table": [],
            "golden_3s": {},
            "highlights": [],
            "viral_formula": {},
            "keywords": {},
            "production_tips": {}
        }
        
        video_url = "https://test.com/new-video"
        report = service.save_report(db_session, video_url, report_data)
        
        assert report.id is not None
        assert report.video_url == video_url
        
        # 验证已保存
        saved = db_session.query(AnalysisReport).filter(
            AnalysisReport.video_url == video_url
        ).first()
        assert saved is not None
    
    def test_save_report_update_existing(
        self,
        service: VideoAnalysisService,
        db_session
    ):
        """测试更新已存在的报告"""
        import uuid
        from datetime import datetime
        
        video_url = "https://test.com/existing"
        
        # 先创建报告
        existing = AnalysisReport(
            id=str(uuid.uuid4()),
            video_url=video_url,
            video_info={"title": "旧标题"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(existing)
        db_session.commit()
        
        # 更新报告
        report_data = {
            "video_info": {"title": "新标题"},
            "basic_info": {},
            "shot_table": [],
            "golden_3s": {},
            "highlights": [],
            "viral_formula": {},
            "keywords": {},
            "production_tips": {}
        }
        
        report = service.save_report(db_session, video_url, report_data)
        
        # 验证已更新
        assert report.video_info["title"] == "新标题"

