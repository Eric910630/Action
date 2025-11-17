# 小红书爬虫测试指南

## 当前状态

✅ **代码已完成**:
- `XiaohongshuCrawler` 类已创建
- 已集成到 `HotspotMonitorService`
- 实现了基于搜索关键词的热点发现机制

⚠️ **待测试**:
- API端点是否正确
- 响应格式是否匹配
- 是否需要登录或特殊处理

## 测试方法

### 方法1：通过API测试（推荐）

```bash
# 1. 确保后端服务运行
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 在另一个终端，触发小红书热点抓取
curl -X POST "http://localhost:8000/api/v1/hotspots/fetch?platform=xiaohongshu"
```

### 方法2：通过Celery任务测试

```bash
# 1. 启动Celery Worker
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info

# 2. 在Python中触发任务
python3 << 'EOF'
from app.services.hotspot.tasks import fetch_daily_hotspots
result = fetch_daily_hotspots.delay("xiaohongshu")
print(f"任务ID: {result.id}")
EOF
```

### 方法3：直接测试爬虫类

```python
# 创建测试脚本
python3 << 'EOF'
import asyncio
from app.crawlers.xiaohongshu_crawler import XiaohongshuCrawler

async def test():
    crawler = XiaohongshuCrawler()
    hotspots = await crawler.crawl_hotspots("xiaohongshu")
    print(f"获取到 {len(hotspots)} 个热点")
    for i, h in enumerate(hotspots[:5], 1):
        print(f"{i}. {h.get('title')} (热度: {h.get('heat_score')})")

asyncio.run(test())
EOF
```

## 可能遇到的问题

### 问题1：API返回403或401

**原因**: 可能需要登录或特殊认证

**解决方案**:
1. 检查是否需要Cookie
2. 检查是否需要特殊的请求头
3. 考虑实现登录机制

### 问题2：API返回404

**原因**: API端点不正确

**解决方案**:
1. 使用浏览器开发者工具，查看实际的小红书搜索API端点
2. 更新 `search_api_url` 配置

### 问题3：响应格式不匹配

**原因**: 实际API响应格式与代码中的解析逻辑不匹配

**解决方案**:
1. 打印实际响应数据：`print(json.dumps(data, indent=2, ensure_ascii=False))`
2. 根据实际格式调整 `_parse_search_results` 方法

### 问题4：返回空列表

**原因**: 
- 搜索关键词不合适
- API需要特殊参数
- 被反爬虫机制拦截

**解决方案**:
1. 检查日志，查看具体错误信息
2. 尝试不同的关键词
3. 检查请求参数是否正确

## 调试技巧

### 1. 查看详细日志

```python
# 在代码中添加详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 打印实际响应

在 `_fetch_from_search` 方法中添加：

```python
response = await client.get(self.search_api_url, params=search_params)
print(f"状态码: {response.status_code}")
print(f"响应头: {response.headers}")
if response.status_code == 200:
    data = response.json()
    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
```

### 3. 测试单个关键词

```python
# 只测试一个关键词
crawler = XiaohongshuCrawler()
crawler.hot_keywords = ["热门"]  # 只测试一个关键词
hotspots = await crawler._fetch_from_search()
```

## 预期结果

### 成功情况

- 返回热点列表（可能为空，但不会报错）
- 日志显示"成功爬取小红书 X 个热点"
- 每个热点包含：title, url, platform, rank, heat_score, tags, timestamp

### 失败情况

- 返回空列表
- 日志显示错误信息
- 需要根据错误信息调整代码

## 下一步

根据测试结果：

1. **如果成功**: 
   - 优化数据质量
   - 调整关键词列表
   - 优化热度计算

2. **如果失败**:
   - 查看日志，找出具体问题
   - 根据实际API调整代码
   - 考虑是否需要登录机制

## 相关文件

- `backend/app/crawlers/xiaohongshu_crawler.py` - 爬虫实现
- `backend/app/services/hotspot/service.py` - 服务集成
- `docs/XIAOHONGSHU_IMPLEMENTATION_ANALYSIS.md` - 实现分析

## 提示

⚠️ **重要**: 
- 小红书的反爬虫机制可能比较严格
- 如果遇到403/401错误，可能需要实现登录机制
- 建议先用浏览器开发者工具分析实际API请求

✅ **建议**:
- 先测试单个关键词，确认API可用
- 查看日志，了解具体问题
- 根据实际情况逐步调整代码

