"""
Firecrawl MCP 客户端
用于热点详情深度提取、批量内容抓取等增强功能
"""
import json
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings


class FirecrawlClient:
    """Firecrawl MCP 客户端（用于增强功能）"""
    
    def __init__(
        self,
        api_key: str = None,
        mcp_server_url: str = None
    ):
        """
        初始化 Firecrawl 客户端
        
        Args:
            api_key: Firecrawl API Key（从环境变量或参数获取）
            mcp_server_url: MCP 服务器 URL（如果通过 MCP 调用）
        """
        self.api_key = api_key or getattr(settings, 'FIRECRAWL_API_KEY', '')
        self.mcp_server_url = mcp_server_url or getattr(settings, 'FIRECRAWL_MCP_SERVER_URL', '')
        
        # 如果配置了 MCP 服务器 URL，使用 MCP 协议
        # 否则使用 Firecrawl Cloud API
        self.use_mcp = bool(self.mcp_server_url)
        
        if not self.api_key and not self.use_mcp:
            logger.warning("Firecrawl API Key 未配置，部分功能可能不可用")
    
    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        通过 MCP 协议调用 Firecrawl 工具
        
        Args:
            tool_name: 工具名称（如 "firecrawl_scrape", "firecrawl_extract"）
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.mcp_server_url:
            raise ValueError("Firecrawl MCP 服务器 URL 未配置")
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    self.mcp_server_url,
                    json=mcp_request,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析 MCP 响应
                if "result" in result:
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        # 提取文本内容
                        text_content = content[0].get("text", "")
                        
                        # 尝试解析为 JSON
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            # 如果不是 JSON，返回文本
                            return {"content": text_content}
                
                return result.get("result", {})
                
            except Exception as e:
                logger.error(f"Firecrawl MCP 调用失败: {e}")
                raise
    
    async def _call_cloud_api(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用 Firecrawl Cloud API
        
        Args:
            endpoint: API 端点（如 "/v2/scrape", "/v2/extract"）
            data: 请求数据
            
        Returns:
            API 响应
        """
        if not self.api_key:
            raise ValueError("Firecrawl API Key 未配置")
        
        base_url = "https://api.firecrawl.dev"
        url = f"{base_url}{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Firecrawl Cloud API 调用失败: {e}")
                raise
    
    async def scrape_url(
        self,
        url: str,
        formats: List[str] = None,
        only_main_content: bool = True
    ) -> Dict[str, Any]:
        """
        抓取单个 URL 的内容
        
        Args:
            url: 目标 URL
            formats: 输出格式（如 ["markdown", "html"]）
            only_main_content: 是否只提取主内容
            
        Returns:
            抓取结果
        """
        if formats is None:
            formats = ["markdown"]
        
        if self.use_mcp:
            return await self._call_mcp_tool("firecrawl_scrape", {
                "url": url,
                "formats": formats,
                "onlyMainContent": only_main_content
            })
        else:
            return await self._call_cloud_api("/v2/scrape", {
                "url": url,
                "formats": formats,
                "onlyMainContent": only_main_content
            })
    
    async def extract_hotspot_details(
        self,
        url: str,
        prompt: str = None,
        schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        使用 AI 提取热点详情（结构化数据）
        
        Args:
            url: 热点 URL
            prompt: 自定义提取提示
            schema: JSON Schema 定义提取的数据结构
            
        Returns:
            提取的结构化数据
        """
        if prompt is None:
            prompt = """从热点页面提取以下信息：
1. 标题（title）
2. 摘要（summary）
3. 标签（tags）
4. 热度分数（heat_score）
5. 发布时间（publish_time）
6. 作者（author，如果有）
7. 关键内容（key_content）
"""
        
        if schema is None:
            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "heat_score": {"type": "number"},
                    "publish_time": {"type": "string"},
                    "author": {"type": "string"},
                    "key_content": {"type": "string"}
                },
                "required": ["title", "summary"]
            }
        
        if self.use_mcp:
            return await self._call_mcp_tool("firecrawl_extract", {
                "urls": [url],
                "prompt": prompt,
                "schema": schema
            })
        else:
            return await self._call_cloud_api("/v2/extract", {
                "urls": [url],
                "prompt": prompt,
                "schema": schema
            })
    
    async def batch_scrape_hotspots(
        self,
        urls: List[str],
        formats: List[str] = None,
        only_main_content: bool = True
    ) -> Dict[str, Any]:
        """
        批量抓取多个热点 URL
        
        Args:
            urls: URL 列表
            formats: 输出格式
            only_main_content: 是否只提取主内容
            
        Returns:
            批量抓取结果（包含操作 ID 用于状态查询）
        """
        if formats is None:
            formats = ["markdown"]
        
        if self.use_mcp:
            return await self._call_mcp_tool("firecrawl_batch_scrape", {
                "urls": urls,
                "options": {
                    "formats": formats,
                    "onlyMainContent": only_main_content
                }
            })
        else:
            return await self._call_cloud_api("/v2/batch/scrape", {
                "urls": urls,
                "formats": formats,
                "onlyMainContent": only_main_content
            })
    
    async def check_batch_status(
        self,
        batch_id: str
    ) -> Dict[str, Any]:
        """
        检查批量操作状态
        
        Args:
            batch_id: 批量操作 ID
            
        Returns:
            操作状态
        """
        if self.use_mcp:
            return await self._call_mcp_tool("firecrawl_check_batch_status", {
                "id": batch_id
            })
        else:
            # Cloud API 的状态查询端点
            base_url = "https://api.firecrawl.dev"
            url = f"{base_url}/v2/batch/scrape/{batch_id}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    logger.error(f"查询批量操作状态失败: {e}")
                    raise

