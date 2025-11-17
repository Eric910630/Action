# BettaFish 小红书功能集成方案

## 背景

参考 [BettaFish](https://github.com/666ghj/BettaFish) 项目的多平台支持架构，我们需要将其小红书信息检索功能嫁接到我们的 TrendRadar 爬虫系统中。

## BettaFish 架构分析

根据 BettaFish 项目文档和搜索结果，其架构特点：

1. **多引擎架构**:
   - `MindSpider`: 数据采集模块，支持对小红书等平台的实时监控
   - `MediaEngine`: 媒体平台数据抓取
   - `ForumEngine`: 论坛数据抓取
   - `InsightEngine`: 深度分析和搜索

2. **统一接口设计**:
   - 各引擎实现统一的接口
   - 支持多平台并发抓取
   - 支持自定义工具集成

3. **灵活配置**:
   - 支持不同LLM模型
   - 支持自定义数据库接入
   - 支持多种情感分析模型

## 集成方案

### 方案1：创建独立的小红书爬虫类（推荐）

**架构设计**:
```
BaseCrawler (抽象基类)
  ├── TrendRadarCrawler (现有，用于API调用)
  └── XiaohongshuCrawler (新增，参考BettaFish的MindSpider实现)
```

**实现步骤**:

1. **创建 `XiaohongshuCrawler` 类**
   - 继承 `BaseCrawler`
   - 实现 `crawl_hotspots` 方法
   - 参考 BettaFish 的 MindSpider 模块实现

2. **修改 `HotspotMonitorService`**
   - 检测到小红书平台时，使用 `XiaohongshuCrawler`
   - 其他平台继续使用 `TrendRadarCrawler`

3. **处理反爬虫机制**
   - User-Agent 轮换
   - Cookie 管理
   - 请求频率控制
   - 代理支持（可选）

### 方案2：集成到 TrendRadarCrawler（简化方案）

**实现方式**:
- 在 `TrendRadarCrawler` 中添加小红书专用逻辑
- API失败时，自动切换到直接爬取模式

**优点**:
- 代码改动小
- 保持现有架构

**缺点**:
- 代码耦合度高
- 不利于扩展

## 技术实现细节

### 1. 小红书数据源分析

根据 BettaFish 的 MindSpider 模块，小红书数据可能来自：

1. **小红书热搜页面**:
   - 网页版热搜
   - 移动端API（如果有）

2. **小红书内容搜索**:
   - 关键词搜索
   - 话题/标签搜索

3. **第三方数据源**:
   - 数据聚合平台
   - API服务

### 2. 反爬虫处理

参考 BettaFish 的实现，需要处理：

1. **请求头伪装**:
   ```python
   headers = {
       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
       "Referer": "https://www.xiaohongshu.com/",
       "Accept": "application/json, text/html",
       "Cookie": "...",  # 如果需要
   }
   ```

2. **请求频率控制**:
   - 随机延迟（1-3秒）
   - 避免过于频繁的请求

3. **Session管理**:
   - 使用 httpx.AsyncClient 保持会话
   - Cookie 自动管理

### 3. 数据解析

**可能的页面结构**:
- HTML页面：需要解析DOM
- JSON API：直接解析JSON
- 混合模式：部分数据在HTML，部分通过API

**解析工具选择**:
- `beautifulsoup4`: HTML解析
- `lxml`: 快速XML/HTML解析
- `json`: JSON数据解析

## 代码实现框架

### 1. 创建 XiaohongshuCrawler 基础框架

```python
# backend/app/crawlers/xiaohongshu_crawler.py
"""
小红书爬虫实现
参考 BettaFish 项目的 MindSpider 模块架构
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger

from app.crawlers.base import BaseCrawler


class XiaohongshuCrawler(BaseCrawler):
    """小红书爬虫（参考BettaFish的MindSpider实现）"""
    
    def __init__(
        self,
        base_url: str = "https://www.xiaohongshu.com",
        request_interval: int = 2000,  # 2秒间隔
        max_retries: int = 2,
    ):
        self.base_url = base_url
        self.request_interval = request_interval
        self.max_retries = max_retries
        
    async def crawl_hotspots(
        self,
        platform: str = "xiaohongshu",
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        爬取小红书热点数据
        
        参考 BettaFish MindSpider 的实现方式
        
        Args:
            platform: 平台标识（固定为 "xiaohongshu"）
            date: 目标日期，None 表示最新数据
            
        Returns:
            热点列表
        """
        logger.info(f"开始爬取小红书热点数据（参考BettaFish实现）")
        
        # TODO: 实现具体爬取逻辑
        # 1. 分析小红书热搜页面结构
        # 2. 实现数据提取
        # 3. 处理反爬虫机制
        
        # 临时返回空列表，等待实现
        logger.warning("小红书爬虫实现中，当前返回空列表")
        return []
```

### 2. 修改 HotspotMonitorService

```python
# backend/app/services/hotspot/service.py
# 在 __init__ 方法中添加：
from app.crawlers.xiaohongshu_crawler import XiaohongshuCrawler

class HotspotMonitorService:
    def __init__(self, ...):
        # ... 现有代码
        
        # 小红书专用爬虫（参考BettaFish）
        self.xiaohongshu_crawler = XiaohongshuCrawler()
    
    async def fetch_hotspots(self, platform: str = "douyin", ...):
        # 如果是小红书平台，使用专用爬虫
        if platform.lower() in ["xiaohongshu", "xhs"]:
            logger.info(f"使用小红书专用爬虫获取热点（参考BettaFish实现）")
            return await self.xiaohongshu_crawler.crawl_hotspots(platform, date)
        
        # 其他平台使用现有逻辑
        # ... 现有代码
```

## 实施步骤

### 阶段1：调研 BettaFish 实现（1-2天）

1. **分析 BettaFish 的 MindSpider 模块**:
   - 查看 GitHub 仓库中的 MindSpider 代码
   - 理解其小红书数据采集逻辑
   - 学习其反爬虫处理方式

2. **分析小红书实际页面**:
   - 访问小红书热搜页面
   - 分析页面结构（HTML/JSON）
   - 确定数据提取方法

3. **研究反爬虫机制**:
   - 测试是否需要登录
   - 测试是否需要Cookie
   - 测试请求频率限制

### 阶段2：基础实现（2-3天）

1. **创建 XiaohongshuCrawler 类**
2. **实现基础爬取逻辑**（参考BettaFish）
3. **实现数据解析**
4. **添加错误处理和重试**

### 阶段3：集成测试（1-2天）

1. **集成到 HotspotMonitorService**
2. **测试完整流程**
3. **处理边界情况**
4. **优化性能**

### 阶段4：优化和完善（持续）

1. **处理反爬虫升级**
2. **优化请求频率**
3. **添加缓存机制**
4. **监控和日志**

## 技术挑战

### 1. 反爬虫机制

⚠️ **小红书可能有较强的反爬虫机制**:
- 需要动态Cookie
- 可能需要验证码
- 请求频率限制严格

**解决方案**:
- 参考 BettaFish 的处理方式
- 使用浏览器自动化（Playwright/Selenium）作为备选
- 实现智能重试和降级

### 2. 页面结构变化

⚠️ **小红书可能频繁更新页面结构**:
- 需要维护解析逻辑
- 需要版本兼容处理

**解决方案**:
- 使用灵活的CSS选择器
- 实现多版本解析逻辑
- 添加结构变化检测

### 3. 数据准确性

⚠️ **确保提取的数据准确**:
- 处理数据格式变化
- 验证数据完整性

**解决方案**:
- 实现数据验证逻辑
- 添加数据清洗步骤
- 记录解析失败的情况

## 替代方案

如果直接爬取困难，可以考虑：

### 方案A：使用浏览器自动化

```python
from playwright.async_api import async_playwright

async def crawl_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.xiaohongshu.com/explore")
        # 提取数据
        await browser.close()
```

### 方案B：使用第三方API

- 寻找提供小红书数据的API服务
- 评估成本和可用性

### 方案C：等待 TrendRadar API 支持

- 联系 API 提供方
- 等待官方支持

## 合规性考虑

⚠️ **重要**: 参考 BettaFish 的免责声明，需要：

1. **遵守使用条款**:
   - 遵守小红书的使用条款
   - 遵守 robots.txt 协议

2. **控制请求频率**:
   - 避免对服务器造成压力
   - 实现合理的延迟机制

3. **用途限制**:
   - 仅用于学习和研究目的
   - 不用于商业用途

## 参考资源

1. **BettaFish 项目**: https://github.com/666ghj/BettaFish
   - MindSpider 模块：数据采集
   - MediaEngine 模块：媒体平台处理

2. **小红书开发者文档**（如果有）

3. **相关爬虫技术文档**

## 结论

✅ **可行性**: 
- 技术上可行
- 参考 BettaFish 的 MindSpider 模块可以实现
- 我们的 `BaseCrawler` 架构支持扩展

⚠️ **挑战**: 
- 需要分析 BettaFish 的实际实现代码
- 需要处理小红书的反爬虫机制
- 需要维护解析逻辑

📋 **建议**: 
1. **第一步**: 深入研究 BettaFish 的 MindSpider 模块代码
2. **第二步**: 分析小红书实际页面结构
3. **第三步**: 实现基础版本，逐步优化
4. **第四步**: 考虑合规性和可持续性

## 下一步行动

1. **查看 BettaFish 源码**:
   - 访问 https://github.com/666ghj/BettaFish
   - 查看 MindSpider 目录下的代码
   - 分析小红书相关的实现

2. **创建基础框架**:
   - 创建 `XiaohongshuCrawler` 类
   - 实现基础结构
   - 添加占位逻辑

3. **逐步实现**:
   - 先实现简单的数据提取
   - 逐步完善反爬虫处理
   - 优化性能和稳定性
