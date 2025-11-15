# 匹配度阈值调整说明

## 📋 问题描述

用户反馈：匹配度只有17.3%的热点仍然在气泡图中显示，匹配度太低，不应该显示。

## ✅ 修复方案

### 1. 添加匹配度阈值配置

在 `backend/app/core/config.py` 中添加了配置项：

```python
# 热点匹配度配置
MATCH_SCORE_THRESHOLD: float = 0.3  # 匹配度阈值（0-1），低于此值的热点将被过滤，默认30%
```

### 2. 后端过滤逻辑

在 `backend/app/api/v1/endpoints/hotspots.py` 的 `get_hotspots_visualization` 函数中：

**修复前**：
```python
# 只过滤匹配度为0的热点
filtered_scores = [item for item in hotspot_scores if item["match_score"] > 0]
```

**修复后**：
```python
# 使用配置的阈值过滤
from app.core.config import settings
match_threshold = settings.MATCH_SCORE_THRESHOLD

filtered_scores = [
    item for item in hotspot_scores 
    if item["match_score"] >= match_threshold
]
```

### 3. 前端过滤逻辑

在 `frontend/src/components/HotspotBubbleChart.vue` 中：

**修复前**：
- 所有匹配度 > 0 的热点都会显示

**修复后**：
```typescript
// 过滤低匹配度热点（阈值30%）
const MATCH_SCORE_THRESHOLD = 0.3
const filteredHotspots = platformHotspots.filter(
  (hotspot) => (hotspot.match_score || 0) >= MATCH_SCORE_THRESHOLD
)
```

## 📊 效果

### 修复前
- 匹配度 > 0 的热点都会显示
- 17.3% 匹配度的热点也会显示 ❌

### 修复后
- 只显示匹配度 >= 30% 的热点 ✅
- 17.3% 匹配度的热点会被过滤掉 ✅
- 提高数据质量，只显示真正相关的高匹配度热点 ✅

## ⚙️ 配置说明

### 默认阈值：30%

默认匹配度阈值为 **30%**（0.3），这意味着：
- 匹配度 < 30% 的热点：**不显示**
- 匹配度 >= 30% 的热点：**显示**

### 如何调整阈值

#### 方式1：修改配置文件

在 `backend/app/core/config.py` 中修改：

```python
MATCH_SCORE_THRESHOLD: float = 0.4  # 改为40%
```

#### 方式2：使用环境变量

在 `.env` 文件中设置：

```env
MATCH_SCORE_THRESHOLD=0.4
```

#### 方式3：前端调整（仅前端显示）

在 `frontend/src/components/HotspotBubbleChart.vue` 中修改：

```typescript
const MATCH_SCORE_THRESHOLD = 0.4  // 改为40%
```

**注意**：建议同时修改后端和前端，保持一致。

## 📈 阈值建议

| 阈值 | 说明 | 适用场景 |
|------|------|----------|
| 20% (0.2) | 宽松 | 初期测试，需要更多热点数据 |
| **30% (0.3)** | **推荐** | **默认值，平衡质量和数量** |
| 40% (0.4) | 中等 | 需要较高相关性 |
| 50% (0.5) | 严格 | 只显示高匹配度热点 |

## 🔍 筛选日志

后端会在筛选时输出日志：

```
[匹配度筛选] 阈值=30.0%, 筛选前=50个, 筛选后=15个
```

可以通过日志了解筛选效果。

## 📝 更新日期

- **2025-01-14**：添加匹配度阈值配置，默认30%

