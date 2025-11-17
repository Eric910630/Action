# 小红书热点抓取问题诊断报告

## 问题现象

- **数据库状态**: 小红书热点数量为 0 个
- **其他平台**: douyin(30), zhihu(20), weibo(30), bilibili(30) - 共110个热点
- **代码状态**: 已添加小红书平台支持，平台列表包含 `xiaohongshu`

## 根本原因

### 1. API返回500错误

**测试结果**:
```
请求 xiaohongshu 失败: Server error '500 Internal Server Error' 
for url 'https://newsnow.busiyi.world/api/s?id=xiaohongshu&latest'
```

**分析**:
- API端点存在（不是404）
- 服务器内部错误（500），可能是：
  1. 小红书平台ID不正确
  2. API服务端对小红书平台的支持有问题
  3. API服务端临时故障

### 2. 其他平台也出现403错误

**测试结果**:
```
❌ douyin (douyin): HTTP 403
❌ weibo (weibo): HTTP 403
❌ bilibili (bilibili-hot-search): HTTP 403
❌ xiaohongshu (xiaohongshu): HTTP 403
```

**分析**:
- 所有平台都返回403（禁止访问）
- 可能是API访问受限或需要认证
- 但之前成功抓取了110个热点，说明：
  1. 之前API可用，现在不可用了
  2. 或者使用了其他数据源（Mock数据、MCP服务等）

### 3. 降级机制未生效

**代码分析**:
- `TrendRadarCrawler` 在API失败时直接返回空列表
- 没有降级到 `TrendRadarClient` 的Mock数据
- 没有使用MCP服务作为降级方案

**相关代码** (`backend/app/crawlers/trendradar_crawler.py`):
```python
async def crawl_hotspots(self, platform: str = "douyin", ...):
    data, _ = await self._fetch_data_async(platform_id)
    if not data:
        logger.warning(f"未能获取 {platform} 的热点数据")
        return []  # 直接返回空列表，没有降级
```

## 解决方案

### 方案1：检查API服务状态（推荐）

1. **验证API是否可用**:
   ```bash
   curl "https://newsnow.busiyi.world/api/s?id=xiaohongshu&latest"
   ```

2. **检查平台ID是否正确**:
   - 当前使用: `xiaohongshu`
   - 可能需要: `xhs` 或其他ID

3. **联系API提供方**:
   - 确认小红书平台是否支持
   - 确认是否需要特殊配置或认证

### 方案2：添加降级机制

修改 `TrendRadarCrawler`，在API失败时降级到 `TrendRadarClient`:

```python
async def crawl_hotspots(self, platform: str = "douyin", ...):
    # 方案1：直接爬虫
    data, _ = await self._fetch_data_async(platform_id)
    if not data:
        logger.warning(f"直接爬虫失败，降级到TrendRadarClient")
        # 降级到TrendRadarClient（可能使用MCP或Mock数据）
        from app.utils.trendradar import TrendRadarClient
        client = TrendRadarClient()
        return await client.get_hotspots(platform, date)
    # ... 正常处理
```

### 方案3：实现小红书专用爬虫

参考 BettaFish 项目，实现直接爬取小红书网页的爬虫：

1. **分析小红书热搜页面结构**
2. **实现专用爬虫类**（继承 `BaseCrawler`）
3. **处理反爬虫机制**（User-Agent、Cookie等）

### 方案4：使用Mock数据（临时方案）

在 `TrendRadarCrawler` 中添加Mock数据支持：

```python
async def crawl_hotspots(self, platform: str = "douyin", ...):
    # ... 尝试API
    if not data:
        logger.warning(f"未能获取 {platform} 的热点数据，使用Mock数据")
        return self._get_mock_hotspots(platform)

def _get_mock_hotspots(self, platform: str) -> List[Dict[str, Any]]:
    """返回Mock数据用于测试"""
    if platform == "xiaohongshu":
        return [
            {
                "title": "小红书热点1",
                "url": "https://www.xiaohongshu.com/...",
                "platform": "xiaohongshu",
                "rank": 1,
                "heat_score": 100,
                "tags": [],
                "timestamp": datetime.now().isoformat(),
            },
            # ... 更多Mock数据
        ]
    return []
```

## 当前状态

### 代码修改状态
✅ **已完成**:
- 后端平台列表已包含 `xiaohongshu`
- 前端平台选择器已添加"小红书"选项
- 平台颜色和标签配置已完成

❌ **未完成**:
- API返回500错误，无法获取真实数据
- 降级机制未实现，失败时返回空列表

### 日志监控

**建议监控的日志位置**:
```bash
# Celery Worker日志
tail -f logs/celery-worker.log | grep -i xiaohongshu

# 后端日志
tail -f logs/backend.log | grep -i xiaohongshu
```

**关键日志信息**:
- `开始爬取 xiaohongshu` - 开始抓取
- `请求 xiaohongshu 失败` - API请求失败
- `未能获取 xiaohongshu 的热点数据` - 最终失败
- `平台 xiaohongshu 保存了 X 个热点` - 成功保存

## 下一步行动

1. **立即行动**:
   - 监控日志，确认API错误是否持续
   - 测试其他平台ID（如 `xhs`）

2. **短期方案**:
   - 实现降级机制，API失败时使用Mock数据
   - 或实现小红书专用爬虫

3. **长期方案**:
   - 联系API提供方，确认小红书支持情况
   - 或参考BettaFish实现独立的小红书爬虫

## 相关文件

- `backend/app/crawlers/trendradar_crawler.py` - 爬虫实现
- `backend/app/services/hotspot/tasks.py` - 抓取任务
- `backend/app/utils/trendradar.py` - TrendRadar客户端（有Mock数据支持）
- `logs/celery-worker.log` - Celery任务日志

