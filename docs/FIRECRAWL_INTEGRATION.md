# Firecrawl 增强功能集成文档

## 概述

Firecrawl 增强功能是阶段2的可选功能，用于从热点页面提取更详细的结构化信息，提升热点数据的质量和可用性。

## 功能特性

### 1. 热点详情深度提取

使用 Firecrawl 的 AI 驱动数据提取功能，从热点页面提取：

- **标题**（title）
- **摘要**（summary）
- **标签**（tags）
- **热度分数**（heat_score）
- **发布时间**（publish_time）
- **作者**（author，如果有）
- **关键内容**（key_content）

### 2. 批量内容抓取

支持批量处理多个热点 URL，提高处理效率。

### 3. 通用网站爬取

如果需要爬取其他网站，可以使用 Firecrawl 的通用爬取功能。

## 配置说明

### 方式1：使用 Firecrawl Cloud API（推荐）

#### 获取 API Key

1. 访问 [Firecrawl 官网](https://www.firecrawl.dev/)
2. 注册并登录账户
3. 访问 [Dashboard](https://www.firecrawl.dev/dashboard)
4. 在 "API Keys" 部分复制您的 API Key（格式：`fc-xxxxxxxxxxxxx`）

**免费额度**：新用户提供 500 个免费抓取页面（500 credits）

详细步骤请参考：[Firecrawl API Key 获取指南](./FIRECRAWL_API_KEY_GUIDE.md)

#### 配置到 Action 项目

在 `backend/.env` 文件中添加：

```env
# 启用 Firecrawl 增强功能
FIRECRAWL_ENABLED=true

# Firecrawl Cloud API Key（从 https://firecrawl.dev 获取）
FIRECRAWL_API_KEY=fc-YOUR_API_KEY
```

### 方式2：使用 Firecrawl MCP Server

#### 2.1 配置 Firecrawl MCP Server

在 Cursor/Claude Desktop 中配置 Firecrawl MCP Server：

**Cursor 配置**（`.cursor/mcp.json` 或用户设置）：

```json
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-YOUR_API_KEY"
      }
    }
  }
}
```

**Claude Desktop 配置**（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "mcp-server-firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-YOUR_API_KEY"
      }
    }
  }
}
```

#### 2.2 配置 Action 项目

在 `backend/.env` 文件中添加：

```env
# 启用 Firecrawl 增强功能
FIRECRAWL_ENABLED=true

# Firecrawl MCP 服务器 URL（如果通过 MCP 调用）
# 注意：如果使用 MCP，通常不需要配置这个，因为 MCP 是通过 Cursor/Claude Desktop 调用的
# 但如果需要直接通过 HTTP 调用 MCP 服务器，可以配置：
FIRECRAWL_MCP_SERVER_URL=http://localhost:8080  # MCP HTTP 服务器地址
```

## 使用方式

### 1. 自动增强（推荐）

在 Celery 任务中，系统会自动使用 Firecrawl 增强热点信息（如果启用）：

```python
# 在 fetch_daily_hotspots 任务中
# 系统会自动增强前10个热点（避免过多API调用）
```

### 2. 手动增强单个热点

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService()
enriched_hotspot = await service.enrich_hotspot_with_firecrawl(hotspot)
```

### 3. 批量增强热点

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService()
enriched_hotspots = await service.enrich_hotspots_batch(
    hotspots,
    max_concurrent=5  # 最大并发数
)
```

## API 参考

### FirecrawlClient

#### `extract_hotspot_details(url, prompt=None, schema=None)`

提取热点详情（结构化数据）

**参数**：
- `url`: 热点 URL
- `prompt`: 自定义提取提示（可选）
- `schema`: JSON Schema 定义（可选）

**返回**：
```python
{
    "title": "热点标题",
    "summary": "热点摘要",
    "tags": ["标签1", "标签2"],
    "heat_score": 95,
    "publish_time": "2025-01-01T10:00:00",
    "author": "作者名",
    "key_content": "关键内容"
}
```

#### `scrape_url(url, formats=None, only_main_content=True)`

抓取单个 URL 的内容

**参数**：
- `url`: 目标 URL
- `formats`: 输出格式（如 `["markdown", "html"]`）
- `only_main_content`: 是否只提取主内容

#### `batch_scrape_hotspots(urls, formats=None, only_main_content=True)`

批量抓取多个热点 URL

**参数**：
- `urls`: URL 列表
- `formats`: 输出格式
- `only_main_content`: 是否只提取主内容

**返回**：
包含操作 ID 的字典，用于后续状态查询

#### `check_batch_status(batch_id)`

检查批量操作状态

**参数**：
- `batch_id`: 批量操作 ID

## 工作流程

```
1. 获取热点列表（通过直接爬虫或 MCP）
   ↓
2. 语义筛选热点
   ↓
3. [可选] 使用 Firecrawl 增强热点信息
   ├── 提取结构化数据（标题、摘要、标签等）
   └── 合并到热点数据
   ↓
4. 保存到数据库
```

## 成本考虑

### Firecrawl Cloud API

- **免费额度**：通常有免费额度
- **付费计划**：根据使用量计费
- **建议**：只增强重要热点（如前10个），避免过多API调用

### Firecrawl MCP Server

- **自托管**：如果自托管，无额外费用
- **Cloud API**：如果 MCP Server 使用 Cloud API，会产生费用

## 故障排查

### 问题1：Firecrawl 未启用

**检查步骤**：
1. 确认 `FIRECRAWL_ENABLED=true` 已设置
2. 确认 `FIRECRAWL_API_KEY` 或 `FIRECRAWL_MCP_SERVER_URL` 已配置
3. 查看日志中的初始化信息

**解决方案**：
- 检查配置是否正确
- 查看日志确认 Firecrawl 客户端是否成功初始化

### 问题2：API 调用失败

**检查步骤**：
1. 确认 API Key 是否有效
2. 检查网络连接
3. 查看日志中的错误信息

**解决方案**：
- 验证 API Key 是否正确
- 检查 Firecrawl 服务状态
- 如果使用 MCP，确认 MCP 服务器正在运行

### 问题3：提取结果为空

**可能原因**：
1. 页面结构不支持提取
2. 提取 Schema 不匹配
3. API 限制

**解决方案**：
- 调整提取 Prompt 和 Schema
- 检查目标 URL 是否可访问
- 查看 Firecrawl 的响应日志

## 最佳实践

1. **选择性增强**：只增强重要热点（如前10个），避免过多API调用
2. **并发控制**：使用 `max_concurrent` 参数控制并发数，避免过载
3. **错误处理**：增强失败时保留原始数据，不影响主流程
4. **成本控制**：监控 API 使用量，合理设置增强范围

## 参考文档

- [Firecrawl 官方文档](https://docs.firecrawl.dev/)
- [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server)
- [爬虫架构升级文档](./CRAWLER_UPGRADE.md)

