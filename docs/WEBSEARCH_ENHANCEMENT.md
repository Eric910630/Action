# Web搜索增强功能说明

## 📋 功能概述

为RelevanceAnalysisAgent添加Web搜索功能，用于查找热点相关的代言、品牌等信息，提升匹配度分析的准确性。

## 🔄 更新：使用Open-WebSearch MCP Server

**2025-01-14更新**：从DuckDuckGo切换到Open-WebSearch MCP Server，原因：
- ✅ 免费，无需API Key
- ✅ 支持多引擎组合搜索（Bing、DuckDuckGo、百度、CSDN等）
- ✅ 避免单一引擎的速率限制
- ✅ 更好的中文搜索支持

**详细集成指南**：请参考 [Open-WebSearch集成指南](./OPEN_WEBSEARCH_INTEGRATION.md)

## 🎯 使用场景

### 场景1：运动员热点

**示例**：热点"王楚钦战胜林高远晋级半决赛"

**问题**：
- 热点本身是体育新闻，与女装直播间看似不相关
- 但如果王楚钦有运动品牌代言，这些品牌可能与直播间类目相关

**解决方案**：
- 使用`search_endorsements("王楚钦", "女装")`查找王楚钦的代言信息
- 如果找到相关品牌，提升匹配度评分

### 场景2：艺人/明星热点

**示例**：热点"某明星参加综艺节目"

**问题**：
- 热点是娱乐新闻，与美妆直播间看似不相关
- 但如果该明星有美妆品牌代言，则高度相关

**解决方案**：
- 使用`search_endorsements("明星名", "美妆")`查找代言信息
- 如果找到美妆品牌代言，大幅提升匹配度

### 场景3：综艺节目热点

**示例**：热点"某综艺节目播出"

**问题**：
- 热点是娱乐内容，与直播间类目看似不相关
- 但节目可能有赞助商和合作品牌

**解决方案**：
- 使用`web_search("节目名 赞助商")`查找节目赞助信息
- 如果找到相关品牌，提升匹配度

## ✅ 实现方案

### 1. 创建Web搜索工具

**文件**：`backend/app/tools/websearch_tools.py`

**功能**：
- `web_search(query, max_results=5)`: 通用网络搜索
- `search_endorsements(person_name, category=None)`: 搜索特定人物的代言信息

**实现**：
- 使用DuckDuckGo搜索（免费，无需API Key）
- 支持中文搜索
- 自动提取品牌和代言信息

### 2. 集成到RelevanceAnalysisAgent

**修改**：
- 在`_init_tools()`中添加`web_search`和`search_endorsements`工具
- 在`_get_system_prompt()`中添加使用说明
- 在`_execute_with_content_package()`中自动检测人物并搜索代言信息

**流程**：
1. 从热点标题中检测知名人物（运动员、艺人等）
2. 如果检测到人物，调用`search_endorsements`查找代言信息
3. 将代言信息加入匹配分析提示词
4. 如果找到匹配的代言品牌，提升匹配度评分（+10%）

### 3. 人物检测逻辑

**当前实现**（简单版本）：
```python
person_keywords = ["王楚钦", "林高远", "樊振东", "何杰", "张伟丽"]
```

**可以优化**：
- 使用NER（命名实体识别）自动提取人物名称
- 使用LLM识别热点中的人物
- 扩展人物关键词列表

## 📊 效果示例

### 示例1：王楚钦热点

**热点**："王楚钦战胜林高远晋级半决赛"

**搜索**：`search_endorsements("王楚钦", "女装")`

**结果**：
- 找到王楚钦的运动品牌代言
- 如果直播间是运动相关类目，匹配度提升

### 示例2：艺人热点

**热点**："某明星参加综艺节目"

**搜索**：`search_endorsements("明星名", "美妆")`

**结果**：
- 找到该明星的美妆品牌代言
- 如果直播间是美妆类目，匹配度大幅提升

## 🔧 配置说明

### 安装依赖

```bash
pip install duckduckgo-search
```

### 使用方式

**自动使用**：
- RelevanceAnalysisAgent会自动检测热点中的人物
- 如果检测到，自动搜索代言信息
- 无需手动调用

**手动调用**（如果需要）：
```python
from app.tools.websearch_tools import search_endorsements

# 搜索王楚钦的代言信息
result = search_endorsements("王楚钦", "女装")
print(result)
```

## ⚠️ 注意事项

### 1. 搜索限制

- DuckDuckGo搜索有速率限制
- 建议控制搜索频率，避免被封IP
- 可以考虑使用其他搜索引擎API（如Google Search API、Bing Search API）

### 2. 人物检测准确性

- 当前使用关键词匹配，可能不够准确
- 建议优化为NER或LLM识别
- 可以维护一个人物数据库

### 3. 代言信息准确性

- 搜索结果可能包含过时信息
- 需要验证信息的时效性
- 可以考虑使用专门的商业数据库

## 🚀 未来优化

### 1. 使用MCP WebSearch工具

如果系统配置了MCP WebSearch服务器，可以：
- 使用MCP协议调用WebSearch工具
- 获得更准确的搜索结果
- 支持更多搜索功能

### 2. 人物识别优化

- 使用NER模型自动识别人物
- 使用LLM提取热点中的人物信息
- 维护人物数据库，提高识别准确性

### 3. 代言数据库

- 维护一个代言数据库
- 定期更新代言信息
- 提供API查询接口

## 📝 更新日期

- **2025-01-14**：添加Web搜索功能，支持查找代言和品牌信息

