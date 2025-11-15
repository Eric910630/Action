# Open-WebSearch MCP Server 集成指南

## 📋 为什么选择Open-WebSearch？

### 优势

1. **✅ 完全免费，无需API Key**
   - 不需要注册或付费
   - 开箱即用

2. **✅ 支持多引擎组合搜索**
   - 支持：Bing、DuckDuckGo、Exa、Brave、Juejin、CSDN、百度、Linux.do
   - 可以同时使用多个引擎，避免单一引擎的速率限制
   - 提高搜索覆盖率和准确性

3. **✅ 内置速率限制管理**
   - 通过多引擎组合，自动分散请求
   - 避免触发单一引擎的速率限制

4. **✅ 支持中文搜索**
   - 支持CSDN、掘金等中文平台
   - 适合查找中文内容（如代言信息）

5. **✅ 易于部署**
   - 支持Docker一键部署
   - 支持NPX快速启动
   - 支持HTTP和SSE传输

## 🚀 安装和配置

### 方案1：使用Docker（推荐）

```bash
# 启动Open-WebSearch MCP Server
docker run -d \
  --name open-websearch \
  -p 3000:3000 \
  -e ENABLE_CORS=true \
  -e CORS_ORIGIN=* \
  -e DEFAULT_SEARCH_ENGINE=bing \
  ghcr.io/aas-ee/open-web-search:latest

# 验证服务
curl http://localhost:3000/mcp
```

### 方案2：使用NPX（快速测试）

```bash
# 直接运行（无需安装）
npx open-websearch@latest

# 或设置环境变量
DEFAULT_SEARCH_ENGINE=bing ENABLE_CORS=true npx open-websearch@latest
```

### 方案3：本地安装

```bash
# 克隆项目
git clone https://github.com/Aas-ee/open-webSearch.git
cd open-webSearch

# 安装依赖
npm install

# 启动服务
npm start
```

## ⚙️ 环境变量配置

在`backend/.env`文件中添加：

```env
# Open-WebSearch MCP Server配置
OPEN_WEBSEARCH_MCP_URL=http://localhost:3000/mcp

# 可选：默认搜索引擎
DEFAULT_SEARCH_ENGINE=bing

# 可选：启用CORS（如果需要跨域访问）
ENABLE_CORS=true
```

## 📝 使用方式

### 在代码中使用

```python
from app.tools.websearch_tools import web_search, search_endorsements

# 基本搜索
results = web_search("王楚钦 代言", max_results=5)

# 多引擎组合搜索（推荐，避免速率限制）
results = web_search(
    "王楚钦 代言",
    max_results=5,
    engines=["bing", "duckduckgo", "baidu"]  # 组合多个引擎
)

# 搜索代言信息
endorsements = search_endorsements("王楚钦", category="女装")
```

### 支持的搜索引擎

- `bing` - 微软必应（推荐，稳定）
- `duckduckgo` - DuckDuckGo（隐私友好）
- `exa` - Exa AI搜索
- `brave` - Brave搜索
- `juejin` - 掘金（中文技术社区）
- `csdn` - CSDN（中文技术博客）
- `baidu` - 百度（中文搜索）
- `linuxdo` - Linux.do论坛

## 🔧 集成到RelevanceAnalysisAgent

已自动集成到`RelevanceAnalysisAgent`中：

1. **自动检测人物**：从热点标题中提取知名人物
2. **多引擎搜索**：使用多个引擎组合搜索，避免速率限制
3. **智能匹配**：如果找到匹配的代言品牌，提升匹配度评分

## 📊 性能对比

| 方案 | 速率限制 | 成本 | 中文支持 | 多引擎 |
|------|---------|------|---------|--------|
| DuckDuckGo直接调用 | 30 req/min | 免费 | 一般 | ❌ |
| Open-WebSearch | 多引擎组合 | 免费 | ✅ 优秀 | ✅ |
| Tavily | 需API Key | 付费 | 一般 | ❌ |

## ⚠️ 注意事项

### 1. 速率限制

虽然Open-WebSearch支持多引擎，但每个引擎仍有自己的速率限制：
- **建议**：使用多引擎组合（如`["bing", "duckduckgo", "baidu"]`）
- **好处**：自动分散请求，避免单一引擎限制

### 2. 服务器部署

如果部署到生产环境：
- 建议使用Docker部署Open-WebSearch服务
- 配置反向代理（Nginx）以提高稳定性
- 监控服务状态和日志

### 3. 备用方案

如果Open-WebSearch服务不可用，代码会自动降级到`duckduckgo-search`（如果已安装）。

## 🔗 相关资源

- **GitHub**: https://github.com/Aas-ee/open-webSearch
- **Docker Hub**: https://hub.docker.com/r/aas-ee/open-web-search
- **文档**: https://github.com/Aas-ee/open-webSearch/blob/main/README.md

## 📝 更新日期

- **2025-01-14**：从DuckDuckGo切换到Open-WebSearch MCP Server

