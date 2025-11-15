# Firecrawl API Key 获取指南

## 概述

Firecrawl 是一个强大的网页爬取和数据提取服务，提供 Cloud API 和自托管两种方式。要使用 Firecrawl 增强功能，需要获取 API Key。

## 获取方式

### 方式1：Firecrawl Cloud API（推荐）

#### 步骤1：注册账户

1. 访问 [Firecrawl 官网](https://www.firecrawl.dev/)
2. 点击 "Sign Up" 或 "Get Started" 按钮
3. 使用邮箱注册账户

#### 步骤2：登录并获取 API Key

1. 登录 Firecrawl 账户
2. 访问 [Dashboard（仪表板）](https://www.firecrawl.dev/dashboard)
3. 在仪表板中找到 "API Keys" 或 "Settings" 部分
4. 复制您的 API Key（格式通常为 `fc-xxxxxxxxxxxxx`）

#### 步骤3：配置到 Action 项目

在 `backend/.env` 文件中添加：

```env
# 启用 Firecrawl 增强功能
FIRECRAWL_ENABLED=true

# Firecrawl Cloud API Key
FIRECRAWL_API_KEY=fc-YOUR_API_KEY_HERE
```

### 方式2：自托管 Firecrawl（高级）

如果您想自托管 Firecrawl 服务：

1. 克隆 [Firecrawl 项目](https://github.com/firecrawl/firecrawl)
2. 按照项目文档部署
3. 配置 Action 项目使用自托管服务：

```env
# 启用 Firecrawl 增强功能
FIRECRAWL_ENABLED=true

# 自托管 Firecrawl 服务 URL
FIRECRAWL_MCP_SERVER_URL=http://your-firecrawl-server:8080

# 如果需要认证
FIRECRAWL_API_KEY=your-self-hosted-api-key
```

## 免费额度

根据 Firecrawl 官方信息：

- **免费额度**：500 个免费抓取页面（500 credits/月）
- **每次抓取费用**：5 个信用点
- **超出后**：需要升级到付费计划
- **速率限制**：免费计划有速率限制（1 个并发爬虫作业/分钟）

## 定价计划

Firecrawl 提供多种定价计划：

| 方案 | 月费 | 信用点数 | 可抓取页面数 | 并发限制 |
|------|------|---------|------------|---------|
| **免费** | $0 | 500 | 500 | 1/分钟 |
| **爱好者** | $19 | 3,000 | 3,000 | 3/分钟 |
| **标准** | $99 | 100,000 | 1,000,000 | 10/分钟 |
| **成长** | $399 | 500,000 | 5,000,000 | 50/分钟 |
| **企业** | 自定义 | 无限 | 无限 | 自定义 |

详细定价信息请参考：[Firecrawl 定价标准](./FIRECRAWL_PRICING.md) 或访问 [Firecrawl 官网](https://www.firecrawl.dev/pricing)

## 配置验证

### 验证 API Key 是否有效

运行以下测试：

```bash
cd backend

# 设置环境变量
export FIRECRAWL_ENABLED=true
export FIRECRAWL_API_KEY=fc-YOUR_API_KEY

# 运行 Firecrawl 测试
pytest tests/integration/test_crawler_integration.py::TestFirecrawlIntegration -v -m firecrawl
```

### 检查配置

```python
# 在 Python 中验证
from app.utils.firecrawl import FirecrawlClient

client = FirecrawlClient()
# 如果初始化成功，说明配置正确
```

## 使用建议

### 成本控制

1. **选择性增强**：
   - 只增强重要热点（如前10个）
   - 避免对所有热点都进行增强

2. **监控使用量**：
   - 定期检查 Firecrawl Dashboard 中的使用量
   - 设置使用量警告

3. **缓存利用**：
   - Firecrawl 支持缓存（`maxAge` 参数）
   - 合理设置缓存时间，减少重复请求

### 速率限制

Firecrawl 有速率限制：

- **免费计划**：较低的速率限制
- **付费计划**：更高的速率限制

如果遇到 429 错误（速率限制），系统会自动重试（最多3次，指数退避）。

## 故障排查

### 问题1：API Key 无效

**症状**：测试失败，错误信息包含 "unauthorized" 或 "401"

**解决方案**：
1. 确认 API Key 格式正确（通常以 `fc-` 开头）
2. 检查 API Key 是否已复制完整
3. 确认 API Key 在 Firecrawl Dashboard 中有效

### 问题2：超出免费额度

**症状**：测试失败，错误信息包含 "quota" 或 "limit"

**解决方案**：
1. 检查 Firecrawl Dashboard 中的使用量
2. 考虑升级到付费计划
3. 减少增强的热点数量

### 问题3：速率限制

**症状**：测试失败，错误信息包含 "rate limit" 或 "429"

**解决方案**：
1. 系统会自动重试（最多3次）
2. 增加请求间隔
3. 减少并发数

## 参考链接

- [Firecrawl 官网](https://www.firecrawl.dev/)
- [Firecrawl 文档](https://docs.firecrawl.dev/)
- [Firecrawl Dashboard](https://www.firecrawl.dev/dashboard)
- [Firecrawl 定价](https://www.firecrawl.dev/pricing)
- [Firecrawl GitHub](https://github.com/firecrawl/firecrawl)

## 注意事项

1. **API Key 安全**：
   - 不要将 API Key 提交到 Git 仓库
   - 使用环境变量或 `.env` 文件（已加入 `.gitignore`）
   - 定期轮换 API Key

2. **成本监控**：
   - 定期检查使用量
   - 设置使用量警告
   - 根据实际需求选择计划

3. **功能使用**：
   - Firecrawl 是可选功能，不影响核心功能
   - 如果不需要增强功能，可以不配置 API Key
   - 系统会在 Firecrawl 未启用时自动跳过增强步骤

