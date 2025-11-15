# 测试指南

## 爬虫集成测试

### 测试频率限制和安全要求

根据 TrendRadar 和 Firecrawl 的文档，测试需要遵循以下频率限制：

#### TrendRadar API

- **默认请求间隔**：1000ms（1秒）
- **最小请求间隔**：50ms
- **重试机制**：
  - 最大重试：2次
  - 重试等待：3-5秒（随机）
  - 指数退避
- **请求抖动**：-10到+20ms随机抖动

#### Firecrawl API

- **内置速率限制**：Firecrawl 有内置的速率限制和并行处理
- **重试机制**：
  - 最大重试：3次（默认）
  - 初始延迟：1000ms
  - 最大延迟：10000ms
  - 退避因子：2
- **信用额度监控**：
  - 警告阈值：1000 credits
  - 严重阈值：100 credits

### 运行测试

#### 方式1：使用测试脚本（推荐）

```bash
cd backend
./scripts/run_crawler_tests.sh
```

脚本会自动：
- 在测试之间添加间隔（2秒）
- 按顺序执行测试
- 处理跳过的情况

#### 方式2：手动运行

```bash
cd backend

# 运行所有爬虫集成测试
pytest tests/integration/test_crawler_integration.py -v -m slow --tb=short

# 运行安全性测试
pytest tests/integration/test_crawler_safety.py -v -m slow --tb=short

# 运行特定测试
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_direct_crawler_basic -v -s
```

#### 方式3：运行完整测试套件

```bash
# 运行所有集成测试（包括爬虫测试）
pytest tests/integration/ -v -m slow --tb=short

# 运行所有测试（包括单元测试）
pytest tests/ -v --tb=short
```

### 测试标记

- `@pytest.mark.slow`：慢速测试，需要真实API调用
- `@pytest.mark.firecrawl`：Firecrawl相关测试，需要Firecrawl API Key
- `@pytest.mark.real_api`：真实API测试，需要真实API Key

### 测试环境变量

#### 基础测试（不需要额外配置）

```bash
# 直接爬虫测试会自动使用 newsnow.busiyi.world API
# 无需额外配置
```

#### Firecrawl 测试（可选）

```bash
export FIRECRAWL_ENABLED=true
export FIRECRAWL_API_KEY=fc-YOUR_API_KEY
```

#### MCP 降级测试（可选）

```bash
export TRENDRADAR_API_URL=http://localhost:3333/mcp
export TRENDRADAR_USE_MCP=true
```

### 测试覆盖

#### 已实现的测试

1. ✅ **直接爬虫基本功能**
   - 测试单个平台爬取
   - 验证数据格式

2. ✅ **请求间隔控制**
   - 测试批量爬取时的间隔控制
   - 验证最小间隔和默认间隔

3. ✅ **HotspotMonitorService 集成**
   - 测试直接爬虫模式
   - 测试 MCP 降级模式

4. ✅ **完整工作流**
   - 爬取 -> 筛选 -> 保存

5. ✅ **安全性测试**
   - 请求间隔合规性
   - 重试机制
   - 并发控制

6. ⏸️ **Firecrawl 增强功能**（需要 API Key）
   - 热点详情提取
   - 批量抓取

### 测试最佳实践

1. **频率控制**
   - 每次测试只爬取1个平台（避免过多请求）
   - 测试之间添加间隔（至少2秒）
   - 批量测试时，确保有足够的间隔

2. **错误处理**
   - 如果API失败，跳过测试而不是失败
   - 记录详细的错误信息

3. **监控日志**
   - 观察请求频率
   - 确认没有触发限流
   - 检查错误信息

4. **成本控制**
   - Firecrawl 测试需要 API Key，注意成本
   - 只测试必要的功能

### 故障排查

#### 问题1：测试失败 - API 限流

**症状**：测试失败，错误信息包含 "rate limit" 或 "429"

**解决方案**：
- 增加测试间隔
- 减少并发数
- 检查是否有其他进程在使用API

#### 问题2：测试失败 - 网络错误

**症状**：测试失败，错误信息包含 "connection" 或 "timeout"

**解决方案**：
- 检查网络连接
- 检查API服务是否可用
- 增加超时时间

#### 问题3：测试跳过 - MCP 服务不可用

**症状**：MCP 降级测试被跳过

**解决方案**：
- 确认 TrendRadar MCP 服务正在运行
- 检查 `TRENDRADAR_API_URL` 配置
- 参考 `docs/TRENDRADAR_MCP_SETUP.md`

### 持续集成

在 CI/CD 环境中运行测试时：

1. **使用测试环境**：如果可能，使用测试API Key
2. **限制并发**：确保测试串行执行
3. **监控成本**：监控API使用量
4. **错误处理**：如果API不可用，跳过测试而不是失败

### 参考文档

- [爬虫集成方案分析](./CRAWLER_INTEGRATION_ANALYSIS.md)
- [爬虫架构升级文档](./CRAWLER_UPGRADE.md)
- [Firecrawl 集成文档](./FIRECRAWL_INTEGRATION.md)
- [测试说明](./tests/integration/README_CRAWLER_TESTS.md)

