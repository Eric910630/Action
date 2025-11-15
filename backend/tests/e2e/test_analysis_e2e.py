"""
E2E测试 - 视频拆解模块
测试视频拆解的完整流程
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestVideoAnalysisE2E:
    """视频拆解E2E测试"""
    
    @pytest.mark.asyncio
    async def test_video_analysis_workflow(self, client, db_session):
        """测试视频拆解的完整流程"""
        
        # 1. 创建测试热点
        from app.models.hotspot import Hotspot
        
        hotspot = Hotspot(
            id="test-analysis-hotspot",
            title="测试视频",
            url="https://www.douyin.com/video/test123",
            platform="douyin",
            tags=["测试"],
            heat_score=90,
            match_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(hotspot)
        db_session.commit()
        
        # 2. 调用拆解API（Mock外部服务）
        with patch('app.services.analysis.tasks.analyze_video_async.delay') as mock_analyze:
            mock_task = MagicMock()
            mock_task.id = "test-analysis-task-id"
            mock_analyze.return_value = mock_task
            
            response = client.post(
                "/api/v1/analysis/analyze",
                json={
                    "video_url": "https://www.douyin.com/video/test123",
                    "options": {}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "task_id" in data
        
        # 3. 模拟拆解完成，创建拆解报告
        from app.models.analysis import AnalysisReport
        
        report = AnalysisReport(
            id="test-report-id",
            video_url="https://www.douyin.com/video/test123",
            video_info={
                "title": "测试视频",
                "duration": 10
            },
            basic_info={
                "theme": "测试主题",
                "content_type": "推广"
            },
            shot_table=[],
            golden_3s={
                "opening_line": "测试开头",
                "hook_type": "悬念钩子"
            },
            highlights=[],
            viral_formula={
                "formula_name": "反转公式",
                "formula_structure": "问题-反转-解决"
            },
            keywords={},
            production_tips={
                "shooting_tips": ["注意光线"],
                "editing_tips": ["快速切换"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        db_session.commit()
        
        # 4. 获取拆解报告列表
        response = client.get("/api/v1/analysis/reports")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        
        # 5. 获取拆解报告详情
        response = client.get(f"/api/v1/analysis/reports/{report.id}")
        assert response.status_code == 200
        report_data = response.json()
        assert report_data["id"] == report.id
        assert "shot_table" in report_data
        assert "viral_formula" in report_data
        assert "techniques" in report_data  # 应该包含提取的技巧
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, client):
        """测试批量拆解"""
        
        video_urls = [
            "https://www.douyin.com/video/test1",
            "https://www.douyin.com/video/test2",
            "https://www.douyin.com/video/test3"
        ]
        
        with patch('app.services.analysis.tasks.analyze_video_async.delay') as mock_analyze:
            mock_task = MagicMock()
            mock_task.id = "test-task-id"
            mock_analyze.return_value = mock_task
            
            response = client.post(
                "/api/v1/analysis/batch",
                json=video_urls
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "task_ids" in data
            assert len(data["task_ids"]) == 3  # 最多10个，这里3个


class TestAnalysisTechniques:
    """测试爆款技巧提取"""
    
    def test_extract_techniques(self, client, db_session):
        """测试从拆解报告中提取爆款技巧"""
        
        from app.models.analysis import AnalysisReport
        from app.services.analysis.service import VideoAnalysisService
        
        # 创建测试报告
        report = AnalysisReport(
            id="test-techniques-report",
            video_url="https://test.com/video",
            shot_table=[
                {
                    "shot_number": 1,
                    "viral_technique": "快速切换"
                }
            ],
            golden_3s={
                "hook_type": "悬念钩子",
                "psychology_trigger": "好奇心"
            },
            viral_formula={
                "formula_name": "反转公式"
            },
            production_tips={
                "shooting_tips": ["注意光线"],
                "editing_tips": ["快速切换"]
            },
            highlights=[
                {
                    "name": "快速节奏",
                    "viral_reason": "吸引注意力"
                }
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(report)
        db_session.commit()
        
        # 提取技巧
        service = VideoAnalysisService()
        techniques = service.extract_techniques({
            "shot_table": report.shot_table or [],
            "golden_3s": report.golden_3s or {},
            "viral_formula": report.viral_formula or {},
            "production_tips": report.production_tips or {},
            "highlights": report.highlights or []
        })
        
        # 验证技巧提取
        assert len(techniques) > 0
        assert any("快速" in str(t) for t in techniques)  # 应该包含快速切换
        assert any("反转" in str(t) for t in techniques)  # 应该包含反转公式

