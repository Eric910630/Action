# TrendRadar API 403/500 错误诊断报告

## 问题总结

### 1. 403错误分析

**测试结果**:
- ✅ API本身可用（测试时返回200）
- ✅ 其他平台（douyin, weibo, bilibili）正常返回200
- ❌ 小红书平台返回500错误

**403错误可能原因**:
1. **请求头问题**: 缺少必要的请求头（如Referer、Origin）
2. **请求频率限制**: 请求过于频繁被限流
3. **IP限制**: 某些IP被临时封禁
4. **User-Agent检测**: User-Agent被识别为爬虫

**解决方案**:
- ✅ 已确认：添加Referer和Origin头后，API返回200
- 建议：在代码中始终包含这些请求头

### 2. 小红书500错误分析

**错误信息**:
```json
{
  "error": true,
  "statusCode": 500,
  "statusMessage": "Server Error",
  "message": "Invalid source id"
}
```

**根本原因**:
- ❌ **API服务端不支持小红书平台**
- ❌ 平台ID `xiaohongshu` 不正确
- ❌ API服务端可能未实现小红书数据源

**测试结果**:
- 测试了多个可能的平台ID：
  - `xiaohongshu` → 500 "Invalid source id"
  - `xhs` → 500 "Invalid source id"
  - `redbook` → 500 "Invalid source id"
  - `xiaohongshu-hot` → 500 "Invalid source id"

## 解决方案

### 方案1：修复请求头（解决403问题）

**修改位置**: `backend/app/crawlers/trendradar_crawler.py`

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://newsnow.busiyi.world/",  # 添加Referer
    "Origin": "https://newsnow.busiyi.world",     # 添加Origin
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}
```

### 方案2：处理小红书平台不支持的问题

**选项A：从平台列表中移除（临时方案）**
- 如果API不支持，暂时不抓取小红书
- 等待API更新支持

**选项B：实现降级机制**
- API失败时，使用Mock数据
- 或实现独立的小红书爬虫

**选项C：联系API提供方**
- 确认是否支持小红书
- 确认正确的平台ID

### 方案3：实现独立的小红书爬虫

参考 BettaFish 项目，实现直接爬取小红书网页的爬虫：

1. **分析小红书热搜页面**
2. **实现专用爬虫类**
3. **处理反爬虫机制**

## 当前状态

### ✅ 已确认
- API本身可用（其他平台正常）
- 请求头配置正确后，API返回200
- 小红书平台ID不被API支持

### ❌ 待解决
- 小红书平台无法通过API获取数据
- 需要实现降级机制或独立爬虫

## 建议的代码修改

### 1. 增强请求头（防止403）

```python
# backend/app/crawlers/trendradar_crawler.py
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://newsnow.busiyi.world/",  # 新增
    "Origin": "https://newsnow.busiyi.world",     # 新增
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}
```

### 2. 处理小红书平台不支持的情况

```python
# backend/app/crawlers/trendradar_crawler.py
async def crawl_hotspots(self, platform: str = "douyin", ...):
    platform_id = self._get_platform_id(platform)
    
    # 检查是否支持该平台
    if platform_id == "xiaohongshu":
        logger.warning(f"API不支持小红书平台，跳过抓取")
        return []  # 或返回Mock数据
    
    # ... 正常抓取逻辑
```

### 3. 添加降级机制

```python
# backend/app/crawlers/trendradar_crawler.py
async def crawl_hotspots(self, platform: str = "douyin", ...):
    data, _ = await self._fetch_data_async(platform_id)
    if not data:
        logger.warning(f"直接爬虫失败，降级到TrendRadarClient")
        # 降级到TrendRadarClient（可能使用MCP或Mock数据）
        from app.utils.trendradar import TrendRadarClient
        client = TrendRadarClient()
        return await client.get_hotspots(platform, date)
    # ... 正常处理
```

## 监控建议

1. **持续监控日志**:
   ```bash
   ./monitor_xiaohongshu.sh
   ```

2. **定期测试API**:
   - 检查API是否开始支持小红书
   - 测试新的平台ID

3. **跟踪错误率**:
   - 统计403/500错误频率
   - 分析错误模式

## 相关文件

- `backend/app/crawlers/trendradar_crawler.py` - 爬虫实现
- `backend/app/utils/trendradar.py` - TrendRadar客户端
- `docs/XIAOHONGSHU_API_DIAGNOSIS.md` - 小红书API诊断
- `logs/celery-worker.log` - Celery任务日志


## 最终诊断结论

### 403错误
- **原因**: 缺少Referer和Origin请求头
- **状态**: ✅ 已修复（添加了Referer和Origin头）

### 小红书500错误
- **原因**: API服务端不支持小红书平台（返回"Invalid source id"）
- **状态**: ✅ 已处理（添加了平台检查，跳过不支持的平台）
- **解决方案**: 
  1. 当前：跳过小红书平台，避免错误日志
  2. 未来：实现独立的小红书爬虫或等待API更新

### 代码修改
1. ✅ 增强了请求头（添加Referer和Origin）
2. ✅ 添加了平台支持检查
3. ✅ 实现了降级机制（API失败时降级到TrendRadarClient）

