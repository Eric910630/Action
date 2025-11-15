# 爬虫集成方案分析

## 项目对比分析

### TrendRadar 项目特点

根据 [TrendRadar GitHub 仓库](https://github.com/sansan0/TrendRadar)：

**优势**：
- ✅ **完全开源**：GPL-3.0 许可证，所有源代码可查看
- ✅ **多平台支持**：支持 35+ 平台（抖音、知乎、B站、微博等）
- ✅ **热点聚合**：专门针对热点新闻和趋势监控
- ✅ **MCP 集成**：已提供 MCP 服务器，便于集成
- ✅ **关键词筛选**：内置关键词筛选和权重算法

**架构**：
- 爬虫代码：Python 实现，源代码完全可见
- 数据输出：`output` 目录存储爬取结果
- MCP 服务：提供 MCP 协议接口

**代码可获取性**：
- ✅ 所有爬虫代码都在 GitHub 仓库中
- ✅ 没有黑盒部分，所有实现都是开源的
- ✅ 可以 Fork 并修改

### Firecrawl 项目特点

根据 [Firecrawl GitHub 仓库](https://github.com/firecrawl/firecrawl)：

**优势**：
- ✅ **完全开源**：AGPL-3.0 许可证
- ✅ **通用爬虫**：适用于任何网站
- ✅ **高性能**：基于 Rust 构建，性能优秀
- ✅ **LLM 就绪**：输出格式适合 LLM 处理
- ✅ **结构化提取**：支持 AI 驱动的数据提取

**架构**：
- 核心引擎：Rust 实现（高性能）
- API 服务：TypeScript/Python
- SDK：提供多种语言 SDK

**代码可获取性**：
- ✅ 完全开源，所有代码可见
- ✅ 可以自托管部署
- ✅ 可以修改和定制

## 集成方案对比

### 方案 A：直接集成 TrendRadar 爬虫代码（推荐）

**优点**：
1. ✅ **专门针对热点**：TrendRadar 就是为热点监控设计的
2. ✅ **多平台支持**：已经实现了抖音、知乎、B站等平台
3. ✅ **代码完全可见**：没有黑盒，可以完全控制
4. ✅ **轻量级**：Python 实现，易于集成和维护
5. ✅ **已有筛选逻辑**：关键词筛选、权重算法都已实现

**实现步骤**：
1. 将 TrendRadar 的爬虫模块作为子模块或直接复制到 Action 项目
2. 在 Action 的 Celery 任务中直接调用爬虫代码
3. 将爬取结果直接保存到 Action 数据库
4. 移除对 MCP 服务的依赖

**代码结构**：
```
Action/
├── backend/
│   ├── app/
│   │   ├── crawlers/          # 新增：爬虫模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # 爬虫基类
│   │   │   ├── douyin.py      # 抖音爬虫（来自TrendRadar）
│   │   │   ├── zhihu.py       # 知乎爬虫（来自TrendRadar）
│   │   │   ├── weibo.py       # 微博爬虫（来自TrendRadar）
│   │   │   └── ...
│   │   └── services/
│   │       └── hotspot/
│   │           └── tasks.py   # 直接调用爬虫
```

### 方案 B：使用 Firecrawl 作为通用爬虫引擎

**优点**：
1. ✅ **高性能**：Rust 实现，性能优秀
2. ✅ **通用性强**：可以爬取任何网站
3. ✅ **LLM 就绪**：输出格式适合 AI 处理

**缺点**：
1. ❌ **需要适配**：需要为每个平台（抖音、知乎等）编写适配器
2. ❌ **复杂度高**：需要理解 Firecrawl 的架构
3. ❌ **可能过度设计**：对于热点监控可能过于复杂

### 方案 C：混合方案（推荐用于扩展）

**架构**：
- **主要使用 TrendRadar**：用于热点平台（抖音、知乎、B站等）
- **辅助使用 Firecrawl**：用于通用网站爬取（如果需要）

## 推荐方案：直接集成 TrendRadar 爬虫

### 为什么选择 TrendRadar？

1. **专门针对热点**：TrendRadar 就是为热点监控设计的，功能匹配度高
2. **代码完全开源**：所有爬虫代码都在 GitHub 上，没有黑盒
3. **易于集成**：Python 实现，可以直接集成到 Action 项目
4. **已有筛选逻辑**：关键词筛选、权重算法都已实现
5. **多平台支持**：已经实现了 35+ 平台

### 实施步骤

#### 步骤 1：分析 TrendRadar 代码结构

```bash
# 克隆 TrendRadar 项目（用于分析）
cd /tmp
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar

# 查看爬虫相关代码
find . -name "*crawl*" -o -name "*spider*" -o -name "*scraper*"
ls -la  # 查看项目结构
```

#### 步骤 2：提取爬虫模块

从 TrendRadar 项目中提取：
- 爬虫实现代码
- 平台适配器（抖音、知乎、B站等）
- 数据解析逻辑
- 关键词筛选算法

#### 步骤 3：集成到 Action 项目

1. 创建 `backend/app/crawlers/` 目录
2. 将 TrendRadar 的爬虫代码迁移过来
3. 修改数据输出：直接保存到 Action 数据库，而不是文件
4. 在 Celery 任务中调用爬虫

#### 步骤 4：移除 MCP 依赖

- 移除对 TrendRadar MCP 服务的依赖
- 直接调用爬虫代码
- 简化架构，提高可靠性

### 代码示例

```python
# backend/app/crawlers/douyin.py
"""抖音热点爬虫（基于TrendRadar实现）"""
from app.crawlers.base import BaseCrawler

class DouyinCrawler(BaseCrawler):
    """抖音热点爬虫"""
    
    async def crawl_hotspots(self) -> List[Dict[str, Any]]:
        """爬取抖音热点"""
        # 使用TrendRadar的爬虫逻辑
        # 返回热点列表
        pass

# backend/app/services/hotspot/tasks.py
@celery_app.task
def fetch_daily_hotspots(platform: str = "douyin", live_room_id: str = None):
    """每日自动抓取热点"""
    from app.crawlers.douyin import DouyinCrawler
    
    crawler = DouyinCrawler()
    hotspots = await crawler.crawl_hotspots()
    
    # 直接保存到数据库
    service = HotspotMonitorService()
    db = SessionLocal()
    try:
        filtered = await service.filter_hotspots_with_semantic(
            db, hotspots, live_room_id=live_room_id
        )
        service.save_hotspots(db, filtered, platform)
    finally:
        db.close()
```

## Firecrawl MCP Server 详细分析

根据 [Firecrawl MCP Server GitHub 仓库](https://github.com/firecrawl/firecrawl-mcp-server)：

### 核心功能

Firecrawl MCP Server 提供了 8 个核心工具：

1. **`firecrawl_scrape`** - 单页内容抓取
   - 支持 Markdown、HTML 格式
   - 可提取主内容（`onlyMainContent`）
   - 支持标签过滤（`includeTags`、`excludeTags`）
   - 支持移动端模拟

2. **`firecrawl_batch_scrape`** - 批量抓取
   - 内置速率限制和并行处理
   - 返回操作 ID，支持状态查询

3. **`firecrawl_map`** - 网站 URL 映射
   - 发现网站所有索引的 URL
   - 用于爬取前的网站结构分析

4. **`firecrawl_crawl`** - 异步网站爬取
   - 支持深度限制（`maxDepth`）
   - 支持页面数量限制（`limit`）
   - 支持去重（`deduplicateSimilarURLs`）

5. **`firecrawl_search`** - 网络搜索
   - 支持语言和地区设置
   - 可对搜索结果进行内容提取

6. **`firecrawl_extract`** - AI 驱动结构化提取
   - 使用 LLM 提取结构化数据
   - 支持自定义 Schema
   - 支持自定义 Prompt

7. **`firecrawl_check_crawl_status`** - 爬取状态查询
8. **`firecrawl_check_batch_status`** - 批量操作状态查询

### MCP 协议实现

Firecrawl MCP Server 完全遵循 MCP 协议标准：
- 使用 JSON-RPC 2.0 格式
- 支持 SSE（Server-Sent Events）和 HTTP 传输
- 提供完整的错误处理和重试机制
- 支持信用额度监控

### 配置方式

```json
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR-API-KEY"
      }
    }
  }
}
```

## Firecrawl 的借鉴点

虽然推荐使用 TrendRadar，但 Firecrawl 有一些值得借鉴的设计：

### 1. MCP 协议标准化实现
- ✅ Firecrawl 提供了完整的 MCP 服务器实现参考
- ✅ 可以借鉴其工具定义、错误处理、状态查询机制
- ✅ 可以参考其配置方式和部署方案

### 2. 异步爬取架构
- Firecrawl 使用异步架构，可以并发爬取多个页面
- 可以借鉴其并发控制机制和任务队列设计

### 3. AI 驱动数据提取
- Firecrawl 的 `extract` 工具使用 LLM 提取结构化数据
- **可以用于从热点页面提取更详细的信息**（标题、摘要、标签、热度等）

### 4. 错误处理和重试
- Firecrawl 有完善的错误处理和重试机制
- 支持指数退避（exponential backoff）
- 可以借鉴其容错设计

### 5. 缓存机制
- Firecrawl 支持缓存（`maxAge` 参数）
- 可以用于热点数据的去重和缓存

### 6. 批量处理能力
- Firecrawl 的 `batch_scrape` 工具支持批量处理
- 可以用于同时抓取多个热点详情页面

### 7. 状态查询机制
- Firecrawl 提供了完善的状态查询 API
- 可以借鉴其任务跟踪和进度报告机制

## 最终推荐方案：混合架构

基于对两个项目的深入分析，推荐采用**混合架构**：

### 方案：TrendRadar 爬虫 + Firecrawl 增强

**架构设计**：
```
Action 项目
├── 核心爬虫：TrendRadar（直接集成代码）
│   ├── 抖音热点爬虫
│   ├── 知乎热点爬虫
│   ├── 微博热点爬虫
│   └── ...（35+ 平台）
│
└── 增强工具：Firecrawl MCP（可选）
    ├── 热点详情深度提取（extract）
    ├── 批量抓取热点内容（batch_scrape）
    └── 通用网站爬取（如果需要）
```

### 实施步骤

#### 阶段 1：集成 TrendRadar 爬虫（核心）

1. **分析 TrendRadar 代码结构**
   ```bash
   # 克隆 TrendRadar 项目（用于分析）
   cd /tmp
   git clone https://github.com/sansan0/TrendRadar.git
   cd TrendRadar
   
   # 查看爬虫相关代码
   find . -name "*crawl*" -o -name "*spider*" -o -name "*scraper*"
   ls -la  # 查看项目结构
   ```

2. **提取爬虫模块**
   - 从 TrendRadar 项目中提取爬虫实现代码
   - 提取平台适配器（抖音、知乎、B站等）
   - 提取数据解析逻辑
   - 提取关键词筛选算法

3. **集成到 Action 项目**
   - 创建 `backend/app/crawlers/` 目录
   - 将 TrendRadar 的爬虫代码迁移过来
   - 修改数据输出：直接保存到 Action 数据库
   - 在 Celery 任务中直接调用爬虫

4. **移除 MCP 依赖**
   - 移除对 TrendRadar MCP 服务的依赖
   - 直接调用爬虫代码
   - 简化架构，提高可靠性

#### 阶段 2：集成 Firecrawl 增强功能（可选）

如果需要更强大的数据提取能力，可以集成 Firecrawl MCP Server：

1. **配置 Firecrawl MCP Server**
   ```json
   {
     "mcpServers": {
       "firecrawl-mcp": {
         "command": "npx",
         "args": ["-y", "firecrawl-mcp"],
         "env": {
           "FIRECRAWL_API_KEY": "YOUR-API-KEY"
         }
       }
     }
   }
   ```

2. **使用 Firecrawl 增强功能**
   - **热点详情提取**：使用 `firecrawl_extract` 从热点页面提取结构化信息
   - **批量内容抓取**：使用 `firecrawl_batch_scrape` 批量抓取热点详情
   - **通用网站爬取**：如果需要爬取其他网站，使用 Firecrawl

3. **创建 Firecrawl 客户端**
   ```python
   # backend/app/utils/firecrawl.py
   class FirecrawlClient:
       """Firecrawl MCP 客户端（用于增强功能）"""
       
       async def extract_hotspot_details(self, url: str) -> Dict[str, Any]:
           """使用 Firecrawl 提取热点详情"""
           # 调用 firecrawl_extract 工具
           pass
   ```

### 代码结构

```
Action/
├── backend/
│   ├── app/
│   │   ├── crawlers/              # 核心爬虫（来自 TrendRadar）
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # 爬虫基类
│   │   │   ├── douyin.py          # 抖音爬虫
│   │   │   ├── zhihu.py           # 知乎爬虫
│   │   │   ├── weibo.py           # 微博爬虫
│   │   │   └── ...
│   │   │
│   │   ├── utils/
│   │   │   ├── trendradar.py      # TrendRadar 客户端（保留，用于过渡）
│   │   │   └── firecrawl.py       # Firecrawl 客户端（可选，用于增强）
│   │   │
│   │   └── services/
│   │       └── hotspot/
│   │           ├── service.py     # 热点监控服务
│   │           └── tasks.py       # Celery 任务（直接调用爬虫）
```

### 优势对比

| 特性 | TrendRadar（核心） | Firecrawl（增强） |
|------|-------------------|------------------|
| **热点爬取** | ✅ 专门针对热点，35+ 平台 | ❌ 通用爬虫，需要适配 |
| **代码控制** | ✅ 完全开源，可完全控制 | ⚠️ 开源但依赖 API |
| **数据提取** | ⚠️ 基础提取 | ✅ AI 驱动结构化提取 |
| **批量处理** | ⚠️ 需要自己实现 | ✅ 内置批量处理 |
| **性能** | ✅ Python，易于维护 | ✅ Rust 核心，高性能 |
| **依赖** | ✅ 无外部依赖 | ⚠️ 需要 API Key |

## 结论

**推荐方案**：**混合架构** - TrendRadar 爬虫（核心）+ Firecrawl 增强（可选）

### 核心理由

1. ✅ **TrendRadar 代码完全开源，没有黑盒**
   - 所有爬虫代码都在 GitHub 仓库中
   - 可以完全控制，不依赖外部服务
   - Python 实现，易于集成和维护

2. ✅ **专门针对热点监控**
   - TrendRadar 就是为热点监控设计的
   - 已有 35+ 平台支持
   - 内置关键词筛选和权重算法

3. ✅ **Firecrawl 作为增强工具**
   - 可以用于热点详情深度提取
   - 可以用于批量内容抓取
   - 可以用于通用网站爬取（如果需要）

### 实施优先级

**阶段 1（必须）**：
1. 分析 TrendRadar 代码结构
2. 提取爬虫模块到 Action 项目
3. 修改数据输出为直接保存到数据库
4. 移除 MCP 服务依赖
5. 测试和优化

**阶段 2（可选）**：
1. 配置 Firecrawl MCP Server
2. 实现热点详情深度提取功能
3. 实现批量内容抓取功能

这样 Action 项目就可以：
- ✅ 独立运行，不依赖 TrendRadar MCP 服务的生命周期
- ✅ 完全控制爬虫逻辑，可以根据需求定制
- ✅ 可选增强功能，提升数据提取能力

