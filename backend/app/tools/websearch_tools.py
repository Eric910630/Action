"""
Web搜索工具
用于在匹配度分析时查找热点相关的代言、品牌等信息

使用Open-WebSearch MCP Server（免费，无需API Key，支持多引擎）
"""
from typing import Dict, Any, Optional
from loguru import logger
import httpx
import os


def web_search(query: str, max_results: int = 5, engines: Optional[list] = None) -> Dict[str, Any]:
    """
    执行网络搜索，查找热点相关的代言、品牌等信息
    
    使用Open-WebSearch MCP Server，支持多引擎组合搜索，避免速率限制
    
    Args:
        query: 搜索关键词（如："王楚钦 代言"、"王楚钦 品牌"）
        max_results: 最大返回结果数，默认5
        engines: 搜索引擎列表，默认["bing", "duckduckgo"]，可选：
                 ["bing", "duckduckgo", "exa", "brave", "juejin", "csdn", "baidu", "linuxdo"]
        
    Returns:
        搜索结果字典，包含：
        - results: 搜索结果列表
        - total: 总结果数
        - query: 搜索关键词
    """
    try:
        # 使用Open-WebSearch MCP Server（免费，无需API Key）
        # 默认使用Bing和DuckDuckGo组合，避免单一引擎速率限制
        if engines is None:
            engines = ["bing", "duckduckgo"]
        
        # 获取MCP服务器URL（如果配置了）
        mcp_server_url = os.getenv("OPEN_WEBSEARCH_MCP_URL", "http://localhost:3000/mcp")
        
        # 构建MCP请求
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": query,
                    "limit": max_results,
                    "engines": engines
                }
            }
        }
        
        # 发送请求
        with httpx.Client(timeout=30.0) as client:
            try:
                response = client.post(
                    mcp_server_url,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析MCP响应
                if "result" in result:
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        # 提取文本内容（可能是JSON字符串）
                        text_content = content[0].get("text", "")
                        
                        # 尝试解析为JSON
                        try:
                            import json
                            search_results = json.loads(text_content)
                            
                            # 格式化结果
                            formatted_results = []
                            if isinstance(search_results, list):
                                for result in search_results:
                                    formatted_results.append({
                                        "title": result.get("title", ""),
                                        "url": result.get("url", ""),
                                        "description": result.get("description", ""),
                                        "source": result.get("source", ""),
                                        "engine": result.get("engine", "")
                                    })
                            
                            logger.info(f"Web搜索完成: query={query}, results={len(formatted_results)}, engines={engines}")
                            
                            return {
                                "results": formatted_results,
                                "total": len(formatted_results),
                                "query": query,
                                "engines": engines
                            }
                        except json.JSONDecodeError:
                            # 如果不是JSON，返回文本
                            logger.warning(f"搜索结果不是JSON格式: {text_content[:200]}")
                            return {
                                "results": [],
                                "total": 0,
                                "query": query,
                                "error": "搜索结果格式错误",
                                "raw_content": text_content[:500]
                            }
                
                return {
                    "results": [],
                    "total": 0,
                    "query": query,
                    "error": "未找到搜索结果"
                }
                
            except httpx.HTTPError as e:
                logger.warning(f"Open-WebSearch MCP服务器连接失败: {e}，尝试备用方案")
                # 备用方案：使用duckduckgo-search（如果安装了）
                return _fallback_search(query, max_results)
            except Exception as e:
                logger.error(f"Web搜索失败: {e}")
                return {
                    "results": [],
                    "total": 0,
                    "query": query,
                    "error": str(e)
                }
                
    except Exception as e:
        logger.error(f"Web搜索失败: {e}")
        return {
            "results": [],
            "total": 0,
            "query": query,
            "error": str(e)
        }


def _fallback_search(query: str, max_results: int) -> Dict[str, Any]:
    """备用搜索方案（使用duckduckgo-search）"""
    try:
        import duckduckgo_search
        
        search_results = duckduckgo_search.ddg(
            query,
            max_results=max_results
        )
        
        # 格式化结果
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "description": result.get("body", ""),
                "engine": "duckduckgo"
            })
        
        logger.info(f"备用搜索完成: query={query}, results={len(formatted_results)}")
        
        return {
            "results": formatted_results,
            "total": len(formatted_results),
            "query": query,
            "engines": ["duckduckgo"],
            "note": "使用备用搜索方案（duckduckgo-search）"
        }
        
    except ImportError:
        logger.warning("duckduckgo_search未安装，备用搜索不可用")
        return {
            "results": [],
            "total": 0,
            "query": query,
            "error": "搜索工具未配置，请安装Open-WebSearch MCP Server或duckduckgo-search",
            "suggestion": "推荐使用Open-WebSearch MCP Server（免费，支持多引擎）"
        }
    except Exception as e:
        logger.error(f"备用搜索失败: {e}")
        return {
            "results": [],
            "total": 0,
            "query": query,
            "error": str(e)
        }


def search_endorsements(person_name: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    搜索特定人物的代言和品牌信息
    
    Args:
        person_name: 人物名称（如："王楚钦"、"林高远"）
        category: 类目（可选，用于过滤相关品牌）
        
    Returns:
        代言和品牌信息字典
    """
    # 构建搜索关键词
    queries = [
        f"{person_name} 代言",
        f"{person_name} 品牌",
        f"{person_name} 合作",
    ]
    
    if category:
        queries.append(f"{person_name} {category} 代言")
        queries.append(f"{person_name} {category} 品牌")
    
    all_results = []
    # 使用多引擎组合搜索，避免速率限制
    engines = ["bing", "duckduckgo", "baidu"]  # 组合多个引擎
    
    for query in queries:
        try:
            results = web_search(query, max_results=3, engines=engines)
            all_results.extend(results.get("results", []))
        except Exception as e:
            logger.warning(f"搜索失败: {query}, {e}")
    
    # 提取品牌信息
    brands = []
    endorsements = []
    
    for result in all_results:
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        snippet = description or title
        
        # 简单的品牌提取（可以优化）
        if any(keyword in title or keyword in snippet for keyword in ["代言", "品牌", "合作", "签约"]):
            endorsements.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "engine": result.get("engine", "")
            })
    
    logger.info(f"代言搜索完成: person={person_name}, endorsements={len(endorsements)}")
    
    return {
        "person_name": person_name,
        "category": category,
        "endorsements": endorsements,
        "total": len(endorsements)
    }
