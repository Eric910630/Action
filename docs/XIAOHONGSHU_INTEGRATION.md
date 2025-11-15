# 小红书平台集成指南

## 概述

本文档说明如何将小红书（Xiaohongshu）平台集成到 Action 项目中，用于抓取小红书热点内容。

## 当前状态

### ✅ 已完成的集成

1. **平台ID配置**：已在 `PLATFORM_IDS` 中添加小红书支持
   - `xiaohongshu` → `xiaohongshu`
   - `xhs` → `xiaohongshu`（别名）

2. **代码支持**：爬虫代码已支持小红书平台标识

### ❌ API不支持（测试结果）

**测试日期**：2025-01-14  
**测试结果**：❌ TrendRadar API (`newsnow.busiyi.world`) **目前不支持小红书平台**

**测试详情**：
- 测试了以下平台ID：`xiaohongshu`、`xhs`、`redbook`、`xiaohongshu-hot`
- 所有ID均返回 `500 Internal Server Error`
- 说明API服务端暂不支持小红书平台

**结论**：虽然代码已支持小红书，但API服务端暂不支持，需要等待TrendRadar更新或使用其他方案。

## 集成步骤

### 步骤1：测试API支持

运行测试脚本验证小红书是否被API支持：

```bash
cd backend
python scripts/test_xiaohongshu_platform.py
```

**测试脚本功能**：
- 尝试多个可能的平台ID
- 验证API是否返回数据
- 显示测试结果和建议

**预期结果**：
- ✅ 如果API支持：会显示获取到的热点数量和示例
- ⚠️ 如果API不支持：会显示错误信息和建议

### 步骤2：确认平台ID

根据测试结果，确认正确的平台ID：

1. **如果测试成功**：
   - 使用测试脚本推荐的平台ID
   - 更新 `PLATFORM_IDS` 配置（如需要）

2. **如果测试失败**：
   - 查看 TrendRadar GitHub 仓库文档
   - 检查 `newsnow.busiyi.world` API 文档
   - 尝试其他可能的平台ID（见下方"可能的平台ID"）

### 步骤3：使用小红书平台

一旦确认API支持，就可以在代码中使用：

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService()

# 方式1：使用 xiaohongshu
hotspots = await service.fetch_hotspots(platform="xiaohongshu")

# 方式2：使用别名 xhs
hotspots = await service.fetch_hotspots(platform="xhs")
```

### 步骤4：批量抓取

在 Celery 任务中添加小红书：

```python
# 在 backend/app/services/hotspot/tasks.py 中
platforms = ["douyin", "zhihu", "weibo", "bilibili", "xiaohongshu"]
```

## 可能的平台ID

如果默认的 `xiaohongshu` 不工作，可以尝试以下ID：

1. **xiaohongshu** - 最可能的ID
2. **xhs** - 常见缩写
3. **redbook** - 英文名
4. **xiaohongshu-hot** - 带hot后缀
5. **xhs-hot** - 缩写+hot后缀

## 验证方法

### 方法1：使用测试脚本（推荐）

```bash
cd backend
python scripts/test_xiaohongshu_platform.py
```

### 方法2：直接调用API

```bash
# 测试不同的平台ID
curl "https://newsnow.busiyi.world/api/s?id=xiaohongshu&latest"
curl "https://newsnow.busiyi.world/api/s?id=xhs&latest"
curl "https://newsnow.busiyi.world/api/s?id=redbook&latest"
```

### 方法3：在代码中测试

```python
import asyncio
from app.crawlers.trendradar_crawler import TrendRadarCrawler

async def test():
    crawler = TrendRadarCrawler()
    hotspots = await crawler.crawl_hotspots("xiaohongshu")
    print(f"获取到 {len(hotspots)} 个热点")
    if hotspots:
        print("前3个热点：")
        for h in hotspots[:3]:
            print(f"  - {h['title']}")

asyncio.run(test())
```

## 解决方案（API不支持小红书）

由于 `newsnow.busiyi.world` API 目前不支持小红书，有以下选项：

### 选项1：使用TrendRadar原始代码

如果 TrendRadar GitHub 仓库中有小红书爬虫代码：

1. 克隆 TrendRadar 仓库
2. 查找小红书爬虫实现
3. 集成到 Action 项目中

```bash
# 克隆TrendRadar
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar

# 查找小红书相关代码
find . -name "*xiaohongshu*" -o -name "*xhs*" -o -name "*redbook*"
```

### 选项2：自行开发爬虫

如果需要自行开发小红书爬虫：

1. 创建 `backend/app/crawlers/xiaohongshu_crawler.py`
2. 实现 `BaseCrawler` 接口
3. 在 `HotspotMonitorService` 中集成

参考其他爬虫实现：
- `backend/app/crawlers/trendradar_crawler.py`

### 选项3：等待API更新

如果 TrendRadar 计划支持小红书但尚未实现：
- 关注 TrendRadar GitHub 仓库更新
- 提交 Issue 请求支持
- 参与贡献代码

## 使用示例

### 示例1：单独抓取小红书热点

```python
from app.services.hotspot.service import HotspotMonitorService

service = HotspotMonitorService()
hotspots = await service.fetch_hotspots(platform="xiaohongshu")

print(f"获取到 {len(hotspots)} 个小红书热点")
for hotspot in hotspots[:5]:
    print(f"- {hotspot['title']} (热度: {hotspot['heat_score']})")
```

### 示例2：多平台抓取（包含小红书）

```python
from app.crawlers.trendradar_crawler import TrendRadarCrawler

crawler = TrendRadarCrawler()
platforms = ["douyin", "zhihu", "weibo", "xiaohongshu"]
results = await crawler.crawl_multiple_platforms(platforms)

for platform, hotspots in results.items():
    print(f"{platform}: {len(hotspots)} 个热点")
```

### 示例3：在Celery任务中使用

```python
# backend/app/services/hotspot/tasks.py
@celery_app.task
def fetch_daily_hotspots(platform: str = None, live_room_id: str = None):
    """每日自动抓取热点"""
    service = HotspotMonitorService()
    
    # 如果未指定平台，抓取所有平台（包括小红书）
    if platform is None:
        platforms = ["douyin", "zhihu", "weibo", "bilibili", "xiaohongshu"]
    else:
        platforms = [platform]
    
    for platform in platforms:
        hotspots = await service.fetch_hotspots(platform)
        # ... 处理热点
```

## 故障排查

### 问题1：API返回空结果

**可能原因**：
- API不支持该平台ID
- 当前时间点没有热点数据
- 平台ID不正确

**解决方案**：
1. 尝试其他平台ID
2. 检查API文档
3. 查看TrendRadar GitHub仓库

### 问题2：API返回错误

**可能原因**：
- 平台ID不存在
- API服务异常
- 网络问题

**解决方案**：
1. 检查网络连接
2. 验证API服务状态
3. 查看错误日志

### 问题3：数据格式异常

**可能原因**：
- API返回格式变化
- 平台数据结构不同

**解决方案**：
1. 检查API返回的原始数据
2. 调整数据解析逻辑
3. 添加异常处理

## 相关文档

- [爬虫架构升级文档](./CRAWLER_UPGRADE.md)
- [爬虫集成方案分析](./CRAWLER_INTEGRATION_ANALYSIS.md)
- [TrendRadar GitHub仓库](https://github.com/sansan0/TrendRadar)

## 更新日志

- **2025-01-14**: 初始版本，添加小红书平台配置和测试脚本

