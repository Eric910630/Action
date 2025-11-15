# 爬虫架构升级文档

## 概述

Action 项目已升级为**混合架构**，支持两种热点获取方案：

1. **直接爬虫（主要方案）**：直接调用 TrendRadar 的爬虫逻辑，通过 `newsnow.busiyi.world` API 获取热点数据
2. **MCP 服务（降级方案）**：通过 TrendRadar MCP 服务获取热点数据

## 架构设计

```
HotspotMonitorService
├── 方案1：直接爬虫（主要）
│   └── TrendRadarCrawler
│       └── 调用 newsnow.busiyi.world API
│
└── 方案2：MCP 服务（降级）
    └── TrendRadarClient
        └── 调用 TrendRadar MCP 服务
```

### 工作流程

1. **优先使用直接爬虫**：
   - 如果 `TRENDRADAR_USE_DIRECT_CRAWLER=true`（默认），尝试使用直接爬虫
   - 直接调用 `newsnow.busiyi.world/api/s?id={platform_id}&latest` API
   - 如果成功获取数据，直接返回

2. **自动降级到 MCP**：
   - 如果直接爬虫失败或返回空结果，自动降级到 MCP 服务
   - 调用 TrendRadar MCP 服务获取热点数据
   - 如果 MCP 也失败，抛出异常

## 配置说明

### 环境变量

在 `backend/.env` 文件中添加以下配置：

```env
# TrendRadar 爬虫配置
TRENDRADAR_USE_DIRECT_CRAWLER=true  # 是否优先使用直接爬虫（主要方案），默认true

# TrendRadar MCP 服务配置（降级方案）
TRENDRADAR_API_URL=http://localhost:3333/mcp  # MCP服务地址
TRENDRADAR_API_KEY=  # 如果MCP服务需要认证，填写API Key（通常不需要）
TRENDRADAR_USE_MCP=true  # 是否使用MCP协议（默认True）
```

### 配置选项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `TRENDRADAR_USE_DIRECT_CRAWLER` | bool | `true` | 是否优先使用直接爬虫（主要方案） |
| `TRENDRADAR_API_URL` | str | `""` | MCP 服务地址（降级方案） |
| `TRENDRADAR_API_KEY` | str | `""` | MCP 服务 API Key（如果需要） |
| `TRENDRADAR_USE_MCP` | bool | `true` | 是否使用 MCP 协议 |

## 代码结构

```
backend/
├── app/
│   ├── crawlers/              # 新增：爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py            # 爬虫基类
│   │   └── trendradar_crawler.py  # TrendRadar 爬虫实现
│   │
│   ├── services/
│   │   └── hotspot/
│   │       ├── service.py     # 热点监控服务（已更新，支持两种方案）
│   │       └── tasks.py        # Celery 任务（无需修改，自动使用新架构）
│   │
│   └── utils/
│       └── trendradar.py      # TrendRadar MCP 客户端（保留，用于降级）
```

## 使用方式

### 1. 默认使用（推荐）

直接使用 `HotspotMonitorService`，它会自动选择最佳方案：

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService()
hotspots = await service.fetch_hotspots(platform="douyin")
```

### 2. 强制使用直接爬虫

```python
service = HotspotMonitorService(use_direct_crawler=True)
hotspots = await service.fetch_hotspots(platform="douyin")
```

### 3. 强制使用 MCP 服务

```python
service = HotspotMonitorService(use_direct_crawler=False)
hotspots = await service.fetch_hotspots(platform="douyin")
```

## 平台支持

支持以下平台（基于 TrendRadar 的配置）：

- `douyin` - 抖音
- `zhihu` - 知乎
- `weibo` - 微博
- `toutiao` - 今日头条
- `baidu` - 百度热搜
- `bilibili` - B站热搜
- `tieba` - 贴吧
- `thepaper` - 澎湃新闻
- `ifeng` - 凤凰网
- `wallstreetcn` - 华尔街见闻
- `cls` - 财联社热门
- `xiaohongshu` / `xhs` - 小红书（需验证API支持）

## 错误处理

### 自动降级机制

系统会自动处理以下情况：

1. **直接爬虫失败**：
   - 网络错误
   - API 返回错误
   - 超时
   - → 自动降级到 MCP 服务

2. **直接爬虫返回空结果**：
   - API 返回空列表
   - → 自动降级到 MCP 服务

3. **MCP 服务也失败**：
   - 抛出异常，记录错误日志

### 日志示例

```
INFO: 开始获取热点，平台: douyin, 使用直接爬虫: True
INFO: 尝试使用直接爬虫获取 douyin 的热点
INFO: 直接爬虫成功获取 50 个热点
```

或（降级情况）：

```
INFO: 开始获取热点，平台: douyin, 使用直接爬虫: True
INFO: 尝试使用直接爬虫获取 douyin 的热点
WARNING: 直接爬虫失败: Connection timeout，降级到MCP服务
INFO: 使用MCP服务获取 douyin 的热点（降级方案）
INFO: MCP服务成功获取 50 个热点
```

## 优势

### 直接爬虫（主要方案）

✅ **独立运行**：不依赖 TrendRadar MCP 服务的生命周期  
✅ **完全控制**：可以完全控制爬虫逻辑，根据需求定制  
✅ **性能更好**：直接调用 API，减少中间层开销  
✅ **易于维护**：代码在 Action 项目内，便于调试和优化

### MCP 服务（降级方案）

✅ **高可用性**：作为备用方案，确保系统稳定运行  
✅ **向后兼容**：保留原有 MCP 集成，不影响现有功能  
✅ **灵活切换**：可以通过配置快速切换方案

## 测试

### 测试直接爬虫

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService(use_direct_crawler=True)
hotspots = await service.fetch_hotspots(platform="douyin")
assert len(hotspots) > 0
```

### 测试 MCP 降级

```python
from app.services.hotspot.service import HotspotMonitorService

# 模拟直接爬虫失败，测试降级
service = HotspotMonitorService(use_direct_crawler=False)
hotspots = await service.fetch_hotspots(platform="douyin")
assert len(hotspots) > 0
```

## 故障排查

### 问题1：直接爬虫失败

**检查步骤**：
1. 检查网络连接
2. 检查 `newsnow.busiyi.world` API 是否可访问
3. 查看日志中的错误信息

**解决方案**：
- 系统会自动降级到 MCP 服务
- 如果 MCP 服务配置正确，应该可以正常获取热点

### 问题2：MCP 服务也失败

**检查步骤**：
1. 确认 TrendRadar MCP 服务正在运行
2. 检查 `TRENDRADAR_API_URL` 配置是否正确
3. 查看日志中的错误信息

**解决方案**：
- 确保 TrendRadar MCP 服务正常运行
- 参考 `docs/TRENDRADAR_MCP_SETUP.md` 配置 MCP 服务

## 升级说明

### 向后兼容

✅ **完全向后兼容**：现有代码无需修改，自动使用新架构  
✅ **配置可选**：如果不配置 `TRENDRADAR_USE_DIRECT_CRAWLER`，默认使用直接爬虫  
✅ **MCP 保留**：MCP 服务作为降级方案，确保系统稳定运行

### 迁移建议

1. **立即生效**：新架构已集成，默认使用直接爬虫
2. **保留 MCP**：建议继续运行 TrendRadar MCP 服务作为降级方案
3. **监控日志**：观察日志，确认直接爬虫正常工作
4. **逐步切换**：如果直接爬虫稳定，可以考虑关闭 MCP 服务（不推荐）

## 阶段2：Firecrawl 增强功能（可选）

阶段2 已实施，提供了可选的 Firecrawl 增强功能：

- ✅ **热点详情深度提取**：使用 AI 驱动提取结构化信息
- ✅ **批量内容抓取**：支持批量处理多个热点
- ✅ **自动集成**：在 Celery 任务中自动增强热点信息

详细文档请参考：[Firecrawl 集成文档](./FIRECRAWL_INTEGRATION.md)

## 参考文档

- [爬虫集成方案分析](./CRAWLER_INTEGRATION_ANALYSIS.md)
- [TrendRadar MCP 服务配置指南](./TRENDRADAR_MCP_SETUP.md)
- [Firecrawl 集成文档](./FIRECRAWL_INTEGRATION.md)

