# 爬虫集成测试说明

## 测试频率限制和安全要求

### TrendRadar API 限制

根据 TrendRadar 文档和代码分析：

- **默认请求间隔**：1000ms（1秒）
- **最小请求间隔**：50ms
- **重试机制**：
  - 最大重试次数：2次
  - 重试等待时间：3-5秒（随机）
  - 指数退避
- **请求抖动**：-10到+20ms随机抖动

### Firecrawl API 限制

根据 Firecrawl 文档：

- **内置速率限制**：Firecrawl 有内置的速率限制和并行处理
- **重试机制**：
  - 最大重试次数：3次（默认）
  - 初始延迟：1000ms
  - 最大延迟：10000ms
  - 退避因子：2
- **信用额度监控**：
  - 警告阈值：1000 credits
  - 严重阈值：100 credits

## 测试策略

### 1. 频率控制

- **单平台测试**：每次测试只爬取1个平台，避免过多请求
- **请求间隔**：使用至少1000ms的间隔（更安全）
- **批量测试**：批量测试时，确保有足够的间隔（每个平台至少1秒）

### 2. 并发控制

- **串行执行**：测试按顺序执行，不并行
- **批量限制**：批量测试时，限制并发数（最多3-5个）

### 3. 错误处理

- **优雅降级**：如果API失败，跳过测试而不是失败
- **重试机制**：测试中验证重试机制正常工作

## 运行测试

### 运行所有爬虫测试

```bash
cd backend
pytest tests/integration/test_crawler_integration.py -v -m "slow" --tb=short
```

### 运行安全性测试

```bash
pytest tests/integration/test_crawler_safety.py -v -m "slow" --tb=short
```

### 运行 Firecrawl 测试（需要 API Key）

```bash
# 设置环境变量
export FIRECRAWL_ENABLED=true
export FIRECRAWL_API_KEY=fc-YOUR_API_KEY

# 运行测试
pytest tests/integration/test_crawler_integration.py::TestFirecrawlIntegration -v -m "firecrawl" --tb=short
```

### 运行特定测试

```bash
# 只测试直接爬虫
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_direct_crawler_basic -v -s

# 只测试完整工作流
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_complete_workflow -v -s
```

## 测试标记说明

- `@pytest.mark.slow`：慢速测试，需要真实API调用
- `@pytest.mark.firecrawl`：Firecrawl相关测试，需要Firecrawl API Key
- `@pytest.mark.real_api`：真实API测试，需要真实API Key

## 注意事项

1. **不要频繁运行测试**：避免对API造成过大压力
2. **使用测试环境**：如果可能，使用测试API Key
3. **监控日志**：观察测试日志，确认请求频率合理
4. **遵守robots.txt**：确保遵守目标网站的爬取规则

