"""
直播间配置服务
负责加载和管理直播间配置文件
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.database import SessionLocal
from app.models.product import LiveRoom


class LiveRoomConfigService:
    """直播间配置服务"""
    
    def __init__(self, config_dir: str = "config/live_rooms"):
        """
        初始化配置服务
        
        Args:
            config_dir: 配置文件目录路径（相对于项目根目录）
        """
        # 获取项目根目录（backend目录的父目录）
        # __file__ 是 backend/app/services/config/live_room_config.py
        # 需要回到项目根目录（Action目录）
        backend_dir = Path(__file__).parent.parent.parent.parent  # backend目录
        project_root = backend_dir.parent  # 项目根目录
        self.config_dir = project_root / config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"配置目录: {self.config_dir}")
    
    def load_live_room_config(self, live_room_name: str) -> Dict[str, Any]:
        """
        加载直播间配置
        
        Args:
            live_room_name: 直播间名称
            
        Returns:
            配置字典
        """
        config_file = self.config_dir / f"{live_room_name}.json"
        
        if not config_file.exists():
            # 如果配置文件不存在，从数据库读取并创建默认配置
            logger.warning(f"配置文件不存在: {config_file}，从数据库读取")
            return self._get_default_config_from_db(live_room_name)
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"已加载配置文件: {config_file}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，从数据库读取")
            return self._get_default_config_from_db(live_room_name)
    
    def _get_default_config_from_db(self, live_room_name: str) -> Dict[str, Any]:
        """
        从数据库读取默认配置
        
        Args:
            live_room_name: 直播间名称
            
        Returns:
            配置字典
        """
        db = SessionLocal()
        try:
            live_room = db.query(LiveRoom).filter(LiveRoom.name == live_room_name).first()
            if not live_room:
                raise ValueError(f"直播间不存在: {live_room_name}")
            
            # 构建默认配置
            config = {
                "basic_info": {
                    "name": live_room.name,
                    "category": live_room.category,
                    "ip_character": live_room.ip_character or "交个朋友",
                    "style": live_room.style or ""
                },
                "keywords": live_room.keywords or [],
                "audience_profile": {
                    "follower_count": "未知",
                    "gender_ratio": {
                        "female": 0.5,
                        "male": 0.5
                    },
                    "age_distribution": {},
                    "fan_structure": {}
                },
                "product_categories": {
                    "primary": [live_room.category],
                    "secondary": [],
                    "occasional": []
                },
                "content_style": {
                    "tone": "",
                    "format": [],
                    "key_elements": []
                },
                "live_streaming_style": {
                    "duration": "2-3小时",
                    "peak_hours": [],
                    "interaction_style": ""
                }
            }
            
            # 保存为配置文件（便于后续编辑）
            self.save_live_room_config(live_room_name, config)
            return config
        finally:
            db.close()
    
    def save_live_room_config(self, live_room_name: str, config: Dict[str, Any]):
        """
        保存直播间配置
        
        Args:
            live_room_name: 直播间名称
            config: 配置字典
        """
        config_file = self.config_dir / f"{live_room_name}.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存配置文件: {config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def get_live_room_profile(self, live_room_name: str) -> str:
        """
        获取直播间完整画像（用于Agent输入）
        
        Args:
            live_room_name: 直播间名称
            
        Returns:
            直播间画像描述文本
        """
        config = self.load_live_room_config(live_room_name)
        
        # 构建完整的直播间画像描述
        basic_info = config.get("basic_info", {})
        audience = config.get("audience_profile", {})
        products = config.get("product_categories", {})
        content = config.get("content_style", {})
        
        profile = f"""直播间名称：{basic_info.get('name', '')}
主营类目：{basic_info.get('category', '')}
IP人设：{basic_info.get('ip_character', '')}
风格定位：{basic_info.get('style', '')}

关键词：{', '.join(config.get('keywords', []))}

受众画像：
- 粉丝体量：{audience.get('follower_count', '未知')}
- 性别比例：女性{audience.get('gender_ratio', {}).get('female', 0.5)*100:.0f}%，男性{audience.get('gender_ratio', {}).get('male', 0.5)*100:.0f}%
- 年龄分布：{self._format_age_distribution(audience.get('age_distribution', {}))}
- 粉丝结构：{self._format_fan_structure(audience.get('fan_structure', {}))}

产品类目：
- 主营：{', '.join(products.get('primary', []))}
- 次营：{', '.join(products.get('secondary', []))}

内容风格：
- 调性：{content.get('tone', '')}
- 格式：{', '.join(content.get('format', []))}
- 关键要素：{', '.join(content.get('key_elements', []))}
"""
        return profile
    
    def _format_age_distribution(self, age_dist: Dict[str, float]) -> str:
        """格式化年龄分布"""
        if not age_dist:
            return "未知"
        return ", ".join([f"{age}: {ratio*100:.0f}%" for age, ratio in age_dist.items()])
    
    def _format_fan_structure(self, fan_struct: Dict[str, float]) -> str:
        """格式化粉丝结构"""
        if not fan_struct:
            return "未知"
        return ", ".join([f"{k}: {v*100:.0f}%" for k, v in fan_struct.items()])
    
    def list_all_configs(self) -> List[str]:
        """
        列出所有配置文件
        
        Returns:
            直播间名称列表
        """
        config_files = list(self.config_dir.glob("*.json"))
        return [f.stem for f in config_files]

