"""
视频拆解服务
"""
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.analysis import AnalysisReport
from app.utils.video_analyzer import VideoAnalyzerClient


class VideoAnalysisService:
    """视频拆解服务"""
    
    def __init__(self):
        self.analyzer_client = VideoAnalyzerClient()
    
    async def analyze_video(
        self,
        video_url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """调用拆解工具分析视频"""
        logger.info(f"开始分析视频: {video_url}")
        
        try:
            # 检查是否已存在拆解报告
            # 这里需要在调用时传入db，暂时先调用API
            
            # 调用拆解工具
            result = await self.analyzer_client.analyze(video_url, options)
            
            logger.info(f"视频分析完成: {video_url}")
            return result
            
        except Exception as e:
            logger.error(f"视频分析失败: {e}")
            raise
    
    def parse_report(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析拆解工具返回的数据，生成结构化报告"""
        try:
            # 如果返回的数据已经是结构化格式，直接使用
            if "data" in raw_data:
                report_data = raw_data["data"]
            elif "report" in raw_data:
                report_data = raw_data["report"]
            else:
                report_data = raw_data
            
            # 构建结构化报告
            structured_report = {
                "video_info": report_data.get("video_info", {}),
                "basic_info": report_data.get("basic_info", {}),
                "shot_table": report_data.get("shot_table", []),
                "golden_3s": report_data.get("golden_3s", {}),
                "highlights": report_data.get("highlights", []),
                "viral_formula": report_data.get("viral_formula", {}),
                "keywords": report_data.get("keywords", {}),
                "production_tips": report_data.get("production_tips", {})
            }
            
            return structured_report
            
        except Exception as e:
            logger.error(f"解析拆解报告失败: {e}")
            raise
    
    def extract_techniques(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从拆解报告中提取可复制的爆款技巧"""
        techniques = []
        
        # 从shot_table中提取镜头技巧
        shot_table = report.get("shot_table", [])
        for shot in shot_table:
            viral_technique = shot.get("viral_technique")
            if viral_technique:
                techniques.append({
                    "type": "shot",
                    "name": "镜头技巧",
                    "description": viral_technique,
                    "source": "shot_table"
                })
        
        # 从golden_3s中提取黄金3秒技巧
        golden_3s = report.get("golden_3s", {})
        if golden_3s.get("hook_type"):
            techniques.append({
                "type": "hook",
                "name": "黄金3秒钩子",
                "description": f"{golden_3s.get('hook_type')}: {golden_3s.get('opening_line', '')}",
                "source": "golden_3s"
            })
        
        # 从viral_formula中提取爆款公式
        viral_formula = report.get("viral_formula", {})
        if viral_formula.get("formula_name"):
            techniques.append({
                "type": "formula",
                "name": viral_formula.get("formula_name"),
                "description": viral_formula.get("formula_structure"),
                "application": viral_formula.get("application_method"),
                "source": "viral_formula"
            })
        
        # 从production_tips中提取制作技巧
        production_tips = report.get("production_tips", {})
        for tip_type, tips in production_tips.items():
            if isinstance(tips, list):
                for tip in tips:
                    techniques.append({
                        "type": tip_type,
                        "name": f"{tip_type}技巧",
                        "description": tip,
                        "source": "production_tips"
                    })
        
        # 从highlights中提取亮点
        highlights = report.get("highlights", [])
        for highlight in highlights:
            if isinstance(highlight, dict):
                techniques.append({
                    "type": "highlight",
                    "name": highlight.get("name", "亮点"),
                    "description": highlight.get("description", ""),
                    "reason": highlight.get("viral_reason", ""),
                    "source": "highlights"
                })
        
        logger.info(f"提取了 {len(techniques)} 个爆款技巧")
        return techniques
    
    def save_report(
        self,
        db: Session,
        video_url: str,
        report_data: Dict[str, Any]
    ) -> AnalysisReport:
        """保存拆解报告到数据库"""
        # 检查是否已存在
        existing = db.query(AnalysisReport).filter(
            AnalysisReport.video_url == video_url
        ).first()
        
        if existing:
            # 更新现有报告
            existing.video_info = report_data.get("video_info")
            existing.basic_info = report_data.get("basic_info")
            existing.shot_table = report_data.get("shot_table")
            existing.golden_3s = report_data.get("golden_3s")
            existing.highlights = report_data.get("highlights")
            existing.viral_formula = report_data.get("viral_formula")
            existing.keywords = report_data.get("keywords")
            existing.production_tips = report_data.get("production_tips")
            existing.updated_at = datetime.now()
            
            logger.info(f"更新拆解报告: {video_url}")
            db.commit()
            return existing
        else:
            # 创建新报告
            new_report = AnalysisReport(
                id=str(uuid.uuid4()),
                video_url=video_url,
                video_info=report_data.get("video_info"),
                basic_info=report_data.get("basic_info"),
                shot_table=report_data.get("shot_table"),
                golden_3s=report_data.get("golden_3s"),
                highlights=report_data.get("highlights"),
                viral_formula=report_data.get("viral_formula"),
                keywords=report_data.get("keywords"),
                production_tips=report_data.get("production_tips"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(new_report)
            db.commit()
            logger.info(f"保存拆解报告: {video_url}")
            return new_report
    
    async def analyze_and_save(
        self,
        db: Session,
        video_url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisReport:
        """分析视频并保存报告（完整流程）"""
        # 调用拆解工具
        raw_data = await self.analyze_video(video_url, options)
        
        # 解析报告
        structured_report = self.parse_report(raw_data)
        
        # 保存到数据库
        report = self.save_report(db, video_url, structured_report)
        
        return report

