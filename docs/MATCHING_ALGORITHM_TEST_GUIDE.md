# 匹配算法优化测试指南

## 测试前准备

### 1. 确认修改已应用

所有匹配算法优化已完成：

✅ **预筛选逻辑优化** (`hotspots.py`)
- 信任LLM判断：电商适配性 >= 0.3 就进入匹配计算
- 不再要求标题中必须包含关键词或类目词

✅ **匹配算法权重调整** (`hotspots.py` 和 `service.py`)
- 内容迁移潜力：60%（最高权重）
- 语义关联：25%
- 直接关联：10%（降低）
- 适用类目匹配：5%

✅ **适用类目匹配增强** (`service.py`)
- 使用embedding计算语义相似度
- 支持同义词匹配（如"奢侈品"和"轻奢"）
- 语义相似度阈值：>= 0.7

### 2. 重启服务（如果需要）

如果服务正在运行，需要重启以应用更改：

```bash
# 停止本地开发服务
./stop_local_dev.sh

# 重新启动
./start_local_dev.sh
```

## 测试步骤

### 测试1：验证易烊千玺热点匹配

**目标**：验证"易烊千玺"相关热点能否匹配上"轻奢真惠选"直播间

**步骤**：
1. 查看数据库中是否有易烊千玺相关热点
2. 检查这些热点的 `content_analysis` 和 `ecommerce_fit`
3. 查看可视化数据，确认匹配分数

**预期结果**：
- "全抖音祝贺易烊千玺金鸡影帝"（适配性0.30，适用类目包含"奢侈品"）
- "易烊千玺为什么能拿金鸡影帝"（适配性0.40，适用类目包含"明星周边"）
- 应该能匹配上"轻奢真惠选"直播间（类目：奢侈品）
- 匹配分数应该 > 0（之前是0.0）

### 测试2：验证高潜力热点匹配

**目标**：验证51个高潜力热点（>=0.6）能否匹配上直播间

**步骤**：
1. 重新抓取热点（或使用现有数据）
2. 查看可视化数据，检查高潜力热点的匹配情况
3. 统计匹配成功的数量

**预期结果**：
- 之前51个高潜力热点的匹配分都是0.0
- 现在应该有相当数量的热点匹配分数 > 0
- 特别是那些适用类目与直播间类目匹配的热点

### 测试3：验证预筛选逻辑

**目标**：验证预筛选不再过于严格

**步骤**：
1. 查看一个热点，标题中没有关键词/类目词，但有 `ecommerce_fit.score >= 0.3`
2. 检查该热点是否出现在可视化数据中

**预期结果**：
- 即使标题中没有"奢侈品"等关键词
- 只要LLM识别出适用类目包含"奢侈品"
- 就应该进入匹配计算并显示在可视化中

### 测试4：验证权重分配

**目标**：验证新的权重分配是否生效

**步骤**：
1. 查看匹配日志，检查各项分数
2. 验证内容迁移潜力（电商适配性）是否占60%权重
3. 验证直接关联（关键词+类目）权重是否降低到10%

**预期结果**：
- 匹配分数计算应该遵循新的权重分配
- 电商适配性高的热点，即使关键词匹配度低，也应该有较高的匹配分数

## 测试命令

### 1. 检查现有热点数据

```bash
cd backend
source venv/bin/activate
python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.hotspot import Hotspot
import json

db = SessionLocal()

# 查找易烊千玺相关热点
yi_hotspots = db.query(Hotspot).filter(
    Hotspot.title.ilike('%易烊千玺%') | 
    Hotspot.title.ilike('%易洋千玺%')
).all()

print(f"找到 {len(yi_hotspots)} 个易烊千玺相关热点\n")

for h in yi_hotspots:
    ecommerce_score = 0.0
    applicable_categories = []
    if h.content_analysis:
        try:
            analysis = json.loads(h.content_analysis) if isinstance(h.content_analysis, str) else h.content_analysis
            ecommerce_fit = analysis.get('ecommerce_fit', {})
            if isinstance(ecommerce_fit, dict):
                ecommerce_score = float(ecommerce_fit.get('score', 0.0))
                applicable_categories = ecommerce_fit.get('applicable_categories', [])
        except:
            pass
    
    print(f"标题: {h.title}")
    print(f"  平台: {h.platform}, 热度: {h.heat_score}")
    print(f"  电商适配性: {ecommerce_score:.2f}")
    print(f"  适用类目: {', '.join(applicable_categories[:5])}")
    print(f"  当前匹配分: {h.match_score if hasattr(h, 'match_score') else '无'}")
    print()

db.close()
EOF
```

### 2. 重新计算匹配分数（如果需要）

如果现有热点的匹配分数还是旧的，可以：

1. **通过前端触发重新匹配**：
   - 访问热点可视化页面
   - 系统会自动使用新的匹配算法重新计算

2. **或者重新抓取热点**：
   ```bash
   # 通过API触发热点抓取
   curl -X POST http://localhost:8000/api/v1/hotspots/fetch
   ```

### 3. 查看可视化数据

访问前端页面：
- 打开热点可视化页面
- 查看气泡图，检查易烊千玺相关热点是否出现
- 点击热点查看匹配详情

## 验证要点

### ✅ 成功指标

1. **易烊千玺热点能匹配上**
   - "全抖音祝贺易烊千玺金鸡影帝" 应该匹配"轻奢真惠选"
   - 匹配分数应该 > 0.3（因为适配性0.30，适用类目包含"奢侈品"）

2. **高潜力热点匹配率提升**
   - 51个高潜力热点中，应该有相当数量匹配分数 > 0
   - 特别是适用类目与直播间类目匹配的热点

3. **预筛选不再过于严格**
   - 标题中没有关键词但LLM识别出适用类目的热点，应该能进入匹配

4. **权重分配正确**
   - 电商适配性高的热点，匹配分数应该更高
   - 即使关键词匹配度低，只要适配性高，也应该有不错的匹配分数

### ❌ 如果测试失败

1. **检查服务是否重启**
   - 确保新的代码已加载

2. **检查数据库中的热点数据**
   - 确认热点有 `content_analysis` 数据
   - 确认 `ecommerce_fit.score >= 0.3`

3. **查看日志**
   - 检查匹配计算日志
   - 查看是否有错误信息

4. **检查embedding服务**
   - 如果适用类目匹配使用embedding，确认embedding服务可用

## 下一步

如果测试通过，可以考虑：
1. 调整语义相似度阈值（当前0.7）
2. 优化同义词映射表
3. 增加更多平台的测试
4. 收集用户反馈，进一步优化算法

