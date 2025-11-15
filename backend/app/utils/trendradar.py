"""
TrendRadar客户端
支持通过MCP协议或HTTP API调用TrendRadar服务
"""
import httpx
import json
from loguru import logger
from app.core.config import settings
from typing import Optional, List, Dict, Any
from datetime import datetime


class TrendRadarClient:
    """TrendRadar客户端（支持MCP和HTTP API）"""
    
    def __init__(self, api_url: str = None, api_key: str = None, use_mcp: bool = None):
        self.api_url = api_url or settings.TRENDRADAR_API_URL
        self.api_key = api_key or settings.TRENDRADAR_API_KEY
        
        # 判断是否使用MCP模式
        # 如果URL包含/mcp或者明确指定use_mcp，则使用MCP协议
        if use_mcp is None:
            # 优先检查环境变量，然后检查URL
            self.use_mcp = getattr(settings, 'TRENDRADAR_USE_MCP', False) or (self.api_url and '/mcp' in self.api_url)
        else:
            self.use_mcp = use_mcp
        
        # 如果使用MCP但URL没有/mcp后缀，自动添加
        if self.use_mcp and self.api_url and '/mcp' not in self.api_url:
            if not self.api_url.endswith('/'):
                self.api_url += '/'
            self.api_url += 'mcp'
        
        # 如果API URL是localhost:3333（测试环境），视为未配置，使用Mock数据
        if self.api_url and ('localhost:3333' in self.api_url or '127.0.0.1:3333' in self.api_url) and not self.use_mcp:
            logger.info("检测到测试环境API地址，将使用Mock数据")
            self.api_url = None  # 强制使用Mock数据
    
    async def get_hotspots(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """获取热点列表"""
        if not self.api_url:
            logger.warning("TrendRadar API URL未配置，返回Mock数据用于测试")
            return self._get_mock_hotspots(platform)
        
        try:
            if self.use_mcp:
                # 使用MCP协议调用
                return await self._get_hotspots_via_mcp(platform, date)
            else:
                # 使用HTTP API调用
                return await self._get_hotspots_via_http(platform, date)
        except Exception as e:
            logger.error(f"获取TrendRadar热点失败: {e}，返回Mock数据用于测试")
            return self._get_mock_hotspots(platform)
    
    async def _get_hotspots_via_mcp(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """通过MCP协议获取热点列表"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # MCP协议调用格式
            # 根据TrendRadar的MCP服务器实现，可能需要调用特定的工具
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_hotspots",  # 工具名称，需要根据TrendRadar实际工具名调整
                    "arguments": {
                        "platform": platform
                    }
                }
            }
            
            if date:
                mcp_request["params"]["arguments"]["date"] = date.strftime("%Y-%m-%d")
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.post(
                self.api_url,
                json=mcp_request,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析MCP响应
            if "result" in result:
                # MCP响应格式：{"result": {"content": [{"type": "text", "text": "..."}]}}
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    # 尝试解析JSON格式的热点数据
                    text_content = content[0].get("text", "[]")
                    try:
                        hotspots = json.loads(text_content)
                        if isinstance(hotspots, list):
                            return hotspots
                        elif isinstance(hotspots, dict) and "hotspots" in hotspots:
                            return hotspots["hotspots"]
                    except json.JSONDecodeError:
                        logger.warning(f"MCP返回的数据不是JSON格式: {text_content}")
            
            return []
    
    async def _get_hotspots_via_http(
        self,
        platform: str = "douyin",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """通过HTTP API获取热点列表"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"platform": platform}
            if date:
                params["date"] = date.strftime("%Y-%m-%d")
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.get(
                f"{self.api_url}/api/hotspots",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("hotspots", [])
    
    def _get_mock_hotspots(self, platform: str = "douyin") -> List[Dict[str, Any]]:
        """返回Mock热点数据用于测试"""
        from datetime import datetime, timedelta
        
        mock_hotspots = [
            {
                "title": "时尚穿搭推荐 连衣裙搭配技巧",
                "url": "https://www.douyin.com/video/test1",
                "tags": ["时尚", "穿搭", "连衣裙", "女装"],
                "heat_score": 95,
                "publish_time": datetime.now() - timedelta(hours=2),
                "video_info": {
                    "duration": 15,
                    "views": 100000
                }
            },
            {
                "title": "美妆教程 自然裸妆画法",
                "url": "https://www.douyin.com/video/test2",
                "tags": ["美妆", "化妆", "教程"],
                "heat_score": 88,
                "publish_time": datetime.now() - timedelta(hours=1),
                "video_info": {
                    "duration": 20,
                    "views": 80000
                }
            },
            {
                "title": "童装推荐 春季新款",
                "url": "https://www.douyin.com/video/test3",
                "tags": ["童装", "春季", "新款"],
                "heat_score": 75,
                "publish_time": datetime.now() - timedelta(hours=3),
                "video_info": {
                    "duration": 12,
                    "views": 60000
                }
            },
            {
                "title": "家具推荐 北欧风格",
                "url": "https://www.douyin.com/video/test4",
                "tags": ["家具", "北欧", "装修"],
                "heat_score": 82,
                "publish_time": datetime.now() - timedelta(hours=4),
                "video_info": {
                    "duration": 18,
                    "views": 70000
                }
            },
            {
                "title": "家电测评 智能家居",
                "url": "https://www.douyin.com/video/test5",
                "tags": ["家电", "智能", "测评"],
                "heat_score": 70,
                "publish_time": datetime.now() - timedelta(hours=5),
                "video_info": {
                    "duration": 25,
                    "views": 50000
                }
            }
        ]
        
        logger.info(f"返回 {len(mock_hotspots)} 个Mock热点数据")
        return mock_hotspots
    
    async def get_hotspot_detail(self, hotspot_id: str) -> Optional[Dict[str, Any]]:
        """获取热点详情"""
        if not self.api_url:
            return None
        
        try:
            if self.use_mcp:
                # 使用MCP协议调用
                return await self._get_hotspot_detail_via_mcp(hotspot_id)
            else:
                # 使用HTTP API调用
                return await self._get_hotspot_detail_via_http(hotspot_id)
        except Exception as e:
            logger.error(f"获取热点详情失败: {e}")
            return None
    
    async def _get_hotspot_detail_via_mcp(self, hotspot_id: str) -> Optional[Dict[str, Any]]:
        """通过MCP协议获取热点详情"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_hotspot_detail",  # 工具名称，需要根据TrendRadar实际工具名调整
                    "arguments": {
                        "hotspot_id": hotspot_id
                    }
                }
            }
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.post(
                self.api_url,
                json=mcp_request,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析MCP响应
            if "result" in result:
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    text_content = content[0].get("text", "{}")
                    try:
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        logger.warning(f"MCP返回的数据不是JSON格式: {text_content}")
            
            return None
    
    async def _get_hotspot_detail_via_http(self, hotspot_id: str) -> Optional[Dict[str, Any]]:
        """通过HTTP API获取热点详情"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.get(
                f"{self.api_url}/api/hotspots/{hotspot_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

