"""
网页内容提取工具
使用 Trafilatura 提取网页的主要内容和元数据
"""
from typing import Dict, Any, Optional
from loguru import logger

try:
    from trafilatura import fetch_url, extract, extract_metadata
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    logger.warning("Trafilatura未安装，网页内容提取功能将不可用。请运行: pip install trafilatura")


class WebContentExtractor:
    """网页内容提取器 - 使用 Trafilatura 提取网页主要内容"""
    
    def __init__(self):
        if not TRAFILATURA_AVAILABLE:
            logger.warning("Trafilatura未安装，WebContentExtractor将不可用")
            self.available = False
        else:
            self.available = True
    
    async def extract_from_url(
        self,
        url: str,
        include_metadata: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        从URL提取网页内容
        
        Args:
            url: 网页URL
            include_metadata: 是否包含元数据（标题、作者、日期等）
            timeout: 请求超时时间（秒）
            
        Returns:
            包含以下字段的字典：
                - content: 主要内容文本
                - metadata: 元数据（如果include_metadata=True）
                    - title: 标题
                    - author: 作者
                    - date: 发布日期
                    - description: 描述
                    - url: 原始URL
        """
        if not self.available:
            logger.warning("Trafilatura未安装，无法提取网页内容")
            return {
                "content": "",
                "metadata": {}
            }
        
        try:
            logger.info(f"开始提取网页内容: {url[:100]}")
            
            # 使用Trafilatura下载并提取内容
            # fetch_url会自动处理下载，extract会提取主要内容
            downloaded = fetch_url(url, timeout=timeout)
            
            if not downloaded:
                logger.warning(f"无法下载网页内容: {url}")
                return {
                    "content": "",
                    "metadata": {}
                }
            
            # 提取主要内容
            main_content = extract(downloaded)
            
            result = {
                "content": main_content or "",
                "metadata": {}
            }
            
            # 提取元数据（如果需要）
            if include_metadata:
                try:
                    metadata = extract_metadata(downloaded)
                    if metadata:
                        result["metadata"] = {
                            "title": metadata.get("title", ""),
                            "author": metadata.get("author", ""),
                            "date": metadata.get("date", ""),
                            "description": metadata.get("description", ""),
                            "url": url
                        }
                except Exception as e:
                    logger.warning(f"提取元数据失败: {e}")
            
            logger.info(f"成功提取网页内容: {url[:100]}, 内容长度={len(result['content'])}")
            return result
            
        except Exception as e:
            logger.error(f"提取网页内容失败: {url[:100]}, 错误: {e}")
            return {
                "content": "",
                "metadata": {}
            }
    
    async def extract_from_html(
        self,
        html: str,
        url: Optional[str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        从HTML字符串提取内容
        
        Args:
            html: HTML字符串
            url: 原始URL（可选，用于元数据）
            include_metadata: 是否包含元数据
            
        Returns:
            包含以下字段的字典：
                - content: 主要内容文本
                - metadata: 元数据（如果include_metadata=True）
        """
        if not self.available:
            logger.warning("Trafilatura未安装，无法提取网页内容")
            return {
                "content": "",
                "metadata": {}
            }
        
        try:
            logger.info(f"开始从HTML提取内容, HTML长度={len(html)}")
            
            # 提取主要内容
            main_content = extract(html)
            
            result = {
                "content": main_content or "",
                "metadata": {}
            }
            
            # 提取元数据（如果需要）
            if include_metadata:
                try:
                    metadata = extract_metadata(html)
                    if metadata:
                        result["metadata"] = {
                            "title": metadata.get("title", ""),
                            "author": metadata.get("author", ""),
                            "date": metadata.get("date", ""),
                            "description": metadata.get("description", ""),
                            "url": url or ""
                        }
                except Exception as e:
                    logger.warning(f"提取元数据失败: {e}")
            
            logger.info(f"成功从HTML提取内容, 内容长度={len(result['content'])}")
            return result
            
        except Exception as e:
            logger.error(f"从HTML提取内容失败: {e}")
            return {
                "content": "",
                "metadata": {}
            }

