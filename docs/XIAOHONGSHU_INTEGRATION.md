# 小红书平台集成说明

## 概述

参考 [BettaFish](https://github.com/666ghj/BettaFish) 项目的多平台支持架构，我们已经在热点检索系统中添加了小红书（Xiaohongshu）平台的支持。

## 实现细节

### 1. 后端支持

#### 1.1 爬虫支持
- **位置**: `backend/app/crawlers/trendradar_crawler.py`
- **平台ID映射**: 
  - `"xiaohongshu": "xiaohongshu"` - 小红书
  - `"xhs": "xiaohongshu"` - 小红书别名
- **API端点**: 通过 `newsnow.busiyi.world/api/s?id=xiaohongshu&latest` 获取热点数据

#### 1.2 默认平台列表
- **位置**: `backend/app/services/hotspot/tasks.py`
- **修改**: 将 `xiaohongshu` 添加到默认抓取平台列表
- **默认平台**: `["douyin", "zhihu", "weibo", "bilibili", "xiaohongshu"]`

#### 1.3 API文档更新
- **位置**: `backend/app/api/v1/endpoints/hotspots.py`
- **修改**: 更新API文档，说明支持小红书平台

### 2. 前端支持

#### 2.1 平台选择器
- **位置**: 
  - `frontend/src/views/HotspotsView.vue`
  - `frontend/src/components/HotspotSelectionDialog.vue`
- **修改**: 在所有平台选择下拉框中添加"小红书"选项

#### 2.2 平台名称映射
- **位置**: `frontend/src/views/HotspotsView.vue`
- **修改**: 
  ```typescript
  'xiaohongshu': '小红书',
  'xhs': '小红书'  // 别名
  ```

#### 2.3 平台标签类型
- **位置**: `frontend/src/views/HotspotsView.vue`
- **修改**: 小红书使用红色标签（`danger`类型），符合品牌色

#### 2.4 气泡图颜色配置
- **位置**: `frontend/src/components/HotspotBubbleChart.vue`
- **修改**: 
  - 小红书使用品牌红色 `RGB(255, 51, 51)` = `#FF3333`
  - 透明度设置为 80%，与其他平台区分

### 3. 数据格式

小红书热点数据格式与其他平台一致：

```json
{
  "title": "热点标题",
  "url": "热点链接",
  "mobileUrl": "移动端链接",
  "platform": "xiaohongshu",
  "rank": 1,
  "heat_score": 100,
  "tags": [],
  "timestamp": "2025-11-15T20:00:00"
}
```

## 使用方法

### 1. 自动抓取
当不指定平台时，系统会自动抓取包括小红书在内的5个平台：
```bash
# 后端API调用
POST /api/v1/hotspots/fetch
# 会自动抓取: douyin, zhihu, weibo, bilibili, xiaohongshu
```

### 2. 指定平台抓取
可以单独指定抓取小红书：
```bash
# 后端API调用
POST /api/v1/hotspots/fetch?platform=xiaohongshu
# 或使用别名
POST /api/v1/hotspots/fetch?platform=xhs
```

### 3. 前端筛选
在前端界面中，可以通过平台筛选器选择"小红书"来查看小红书的热点数据。

## 技术架构参考

参考了 [BettaFish](https://github.com/666ghj/BettaFish) 项目的多平台支持架构：

1. **统一爬虫接口**: 使用 `BaseCrawler` 抽象基类，所有平台实现统一的 `crawl_hotspots` 方法
2. **平台ID映射**: 通过 `PLATFORM_IDS` 字典映射平台标识到API平台ID
3. **异步抓取**: 支持多平台并发抓取，提高效率
4. **降级机制**: 如果直接爬虫失败，自动降级到MCP服务

## 注意事项

1. **API限制**: 小红书热点数据通过 `newsnow.busiyi.world` API获取，需要确保该API可用
2. **请求频率**: 系统已实现请求间隔控制，避免被限流
3. **数据格式**: 小红书热点数据格式与其他平台保持一致，便于统一处理
4. **别名支持**: 支持 `xiaohongshu` 和 `xhs` 两种标识，提高灵活性

## 未来扩展

参考 BettaFish 项目的架构，未来可以考虑：

1. **自定义爬虫**: 如果API不可用，可以实现直接爬取小红书网页的爬虫
2. **更多平台**: 可以继续添加其他平台支持（如：头条、百度等）
3. **平台特定处理**: 针对不同平台的特点，实现特定的数据处理逻辑

## 相关文件

- `backend/app/crawlers/trendradar_crawler.py` - 爬虫实现
- `backend/app/services/hotspot/tasks.py` - 定时任务
- `backend/app/api/v1/endpoints/hotspots.py` - API端点
- `frontend/src/views/HotspotsView.vue` - 前端主视图
- `frontend/src/components/HotspotSelectionDialog.vue` - 热点选择对话框
- `frontend/src/components/HotspotBubbleChart.vue` - 气泡图组件
