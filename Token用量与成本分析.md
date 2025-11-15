# Token用量与成本分析报告

## 一、流程概览

**每日定时任务流程：**
1. 热点抓取（4个平台：douyin, zhihu, weibo, bilibili）
2. 语义筛选（使用embedding，不涉及LLM）
3. 热点解析（ContentStructureAgent + ContentAnalysisAgent）
4. 匹配分析（RelevanceAnalysisAgent，每个热点匹配多个直播间）
5. 脚本生成（ScriptGenerationAgent，为10个商品生成脚本）

---

## 二、各阶段Token用量估算

### 2.1 热点抓取阶段
- **LLM调用次数**: 0次
- **Token用量**: 0 tokens
- **说明**: 使用爬虫直接抓取，不涉及LLM

### 2.2 语义筛选阶段
- **LLM调用次数**: 0次
- **Token用量**: 0 tokens
- **说明**: 使用embedding和sentiment分析，不涉及LLM

### 2.3 热点解析阶段

#### 假设条件：
- 抓取热点总数：120个（4个平台 × 30个/平台）
- 语义筛选后剩余：50个热点
- 每个热点需要解析

#### ContentStructureAgent（视频结构提取）
- **调用次数**: 50次（每个热点1次）
- **System Prompt**: ~200 tokens
- **User Prompt**: ~800 tokens（包含视频标题、URL、转录文本预览等）
- **Max Output Tokens**: 2000 tokens
- **Temperature**: 0.3

**单次调用Token估算：**
- Input: 200 (system) + 800 (prompt) = 1000 tokens
- Output: ~1500 tokens（实际输出通常为max_tokens的60-80%）

**总Token用量：**
- Input: 1000 × 50 = 50,000 tokens
- Output: 1500 × 50 = 75,000 tokens

#### ContentAnalysisAgent（内容分析）
- **调用次数**: 50次（每个热点1次）
- **System Prompt**: ~300 tokens
- **User Prompt**: ~600 tokens（包含视频结构信息、转录文本等）
- **Max Output Tokens**: 1500 tokens
- **Temperature**: 0.7

**单次调用Token估算：**
- Input: 300 (system) + 600 (prompt) = 900 tokens
- Output: ~1000 tokens

**总Token用量：**
- Input: 900 × 50 = 45,000 tokens
- Output: 1000 × 50 = 50,000 tokens

**热点解析阶段总计：**
- Input: 50,000 + 45,000 = 95,000 tokens
- Output: 75,000 + 50,000 = 125,000 tokens

### 2.4 匹配分析阶段

#### 假设条件：
- 已解析热点数：50个
- 直播间数量：5个
- 每个热点需要与每个直播间进行匹配分析

#### RelevanceAnalysisAgent（匹配度分析）
- **调用次数**: 50 × 5 = 250次（每个热点匹配5个直播间）
- **System Prompt**: ~800 tokens（包含详细的匹配分析框架）
- **User Prompt**: ~700 tokens（包含热点信息、直播间画像等）
- **Max Output Tokens**: 1000 tokens
- **Temperature**: 0.7

**单次调用Token估算：**
- Input: 800 (system) + 700 (prompt) = 1500 tokens
- Output: ~800 tokens

**总Token用量：**
- Input: 1500 × 250 = 375,000 tokens
- Output: 800 × 250 = 200,000 tokens

### 2.5 脚本生成阶段

#### 假设条件：
- 需要生成脚本的商品数：10个
- 每个商品基于1个匹配的热点生成脚本

#### ScriptGenerationAgent（脚本生成）
- **调用次数**: 10次（每个商品1次）
- **System Prompt**: ~200 tokens
- **User Prompt**: ~1500 tokens（包含热点信息、商品信息、拆解报告等）
- **Max Output Tokens**: 3000 tokens
- **Temperature**: 0.7

**单次调用Token估算：**
- Input: 200 (system) + 1500 (prompt) = 1700 tokens
- Output: ~2000 tokens（脚本内容较长）

**总Token用量：**
- Input: 1700 × 10 = 17,000 tokens
- Output: 2000 × 10 = 20,000 tokens

---

## 三、Token用量汇总

### 3.1 每日总Token用量

| 阶段 | Input Tokens | Output Tokens | 总Tokens |
|------|--------------|---------------|----------|
| 热点解析 | 95,000 | 125,000 | 220,000 |
| 匹配分析 | 375,000 | 200,000 | 575,000 |
| 脚本生成 | 17,000 | 20,000 | 37,000 |
| **总计** | **487,000** | **345,000** | **832,000** |

### 3.2 月度Token用量估算

- **每日**: 832,000 tokens
- **每月（30天）**: 832,000 × 30 = **24,960,000 tokens** ≈ **25M tokens**

---

## 四、DeepSeek计费标准（2025年9月6日后）

根据DeepSeek API官方文档，当前计费标准为：

| 类型 | 价格（人民币/百万tokens） |
|------|-------------------------|
| Input (Cache Miss) | 4元 |
| Input (Cache Hit) | 0.5元 |
| Output | 12元 |

### 4.1 Cache命中率假设

根据DeepSeek官方数据：
- **历史数据显示平均缓存命中率超过50%**
- **优化后可达90%的缓存命中率**

**保守估算（50%缓存命中率）：**
- Input Cache Hit: 50%
- Input Cache Miss: 50%

**乐观估算（80%缓存命中率）：**
- Input Cache Hit: 80%
- Input Cache Miss: 20%

---

## 五、成本计算

### 5.1 每日成本（保守估算，50%缓存命中率）

**Input Tokens成本：**
- Cache Hit: 487,000 × 50% × 0.5元/百万 = 0.122元
- Cache Miss: 487,000 × 50% × 4元/百万 = 0.974元
- **Input总成本**: 1.096元

**Output Tokens成本：**
- Output: 345,000 × 12元/百万 = 4.14元

**每日总成本：**
- **1.096 + 4.14 = 5.236元/天**

### 5.2 每日成本（乐观估算，80%缓存命中率）

**Input Tokens成本：**
- Cache Hit: 487,000 × 80% × 0.5元/百万 = 0.195元
- Cache Miss: 487,000 × 20% × 4元/百万 = 0.390元
- **Input总成本**: 0.585元

**Output Tokens成本：**
- Output: 345,000 × 12元/百万 = 4.14元

**每日总成本：**
- **0.585 + 4.14 = 4.725元/天**

### 5.3 月度成本估算

**保守估算（50%缓存命中率）：**
- 每日: 5.236元
- 每月（30天）: **157.08元/月**

**乐观估算（80%缓存命中率）：**
- 每日: 4.725元
- 每月（30天）: **141.75元/月**

---

## 六、成本优化建议

### 6.1 提高缓存命中率
- **优化策略**: 复用相同的system prompt和相似的用户prompt模板
- **预期效果**: 将缓存命中率从50%提升到80%，可节省约15元/月

### 6.2 减少Output Token用量
- **优化策略**: 
  - 调整`max_tokens`参数，根据实际需求设置合理的上限
  - 使用JSON格式输出，减少冗余文本
- **预期效果**: 如果Output减少20%，可节省约25元/月

### 6.3 批量处理优化
- **优化策略**: 对相似的热点进行批量分析，减少重复的system prompt
- **预期效果**: 进一步提高缓存命中率

### 6.4 匹配分析优化
- **当前**: 每个热点匹配5个直播间 = 250次调用
- **优化**: 可以考虑先筛选出高匹配度的热点，再对筛选后的热点进行详细匹配
- **预期效果**: 如果减少50%的匹配调用，可节省约115元/月

---

## 七、总结

### 7.1 核心数据

| 指标 | 数值 |
|------|------|
| 每日Token用量 | 832,000 tokens |
| 每日成本（保守） | 5.24元 |
| 每日成本（乐观） | 4.73元 |
| 月度成本（保守） | 157元 |
| 月度成本（乐观） | 142元 |

### 7.2 成本占比分析

**Output Token成本占比最高（约79%）：**
- Output: 4.14元/天（79%）
- Input Cache Miss: 0.97元/天（19%）
- Input Cache Hit: 0.12元/天（2%）

**优化建议优先级：**
1. **最高优先级**: 优化Output Token用量（减少max_tokens或使用更紧凑的输出格式）
2. **次优先级**: 提高缓存命中率（优化prompt复用）
3. **可选优化**: 减少匹配分析调用次数（通过预筛选）

### 7.3 实际运行建议

1. **监控实际Token用量**: 在运行初期，记录实际的token用量，与估算值对比
2. **逐步优化**: 根据实际数据，逐步实施优化策略
3. **成本预警**: 设置月度成本上限（如200元），超出时触发预警

---

**报告生成时间**: 2025-01-14  
**基于**: DeepSeek API官方文档（2025年9月6日后计费标准）  
**模型**: deepseek-chat (DeepSeek-V3.1)

