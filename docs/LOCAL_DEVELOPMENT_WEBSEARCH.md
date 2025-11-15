# 本地开发Web搜索配置指南

## 📋 问题

Open-WebSearch MCP Server需要Docker环境，但本地开发时不想运行Docker（避免M1 MacBook Air卡顿）。

## ✅ 解决方案

### 方案1：使用备用搜索方案（推荐）⭐

**优点**：
- ✅ 无需Docker
- ✅ 无需额外服务
- ✅ 开箱即用

**配置**：

1. **安装备用搜索库**（可选，代码会自动降级）：
```bash
cd backend
pip install duckduckgo-search
```

2. **配置环境变量**（可选）：
```env
# backend/.env
# 不设置 OPEN_WEBSEARCH_MCP_URL，或设置为空
# OPEN_WEBSEARCH_MCP_URL=
```

3. **代码自动处理**：
   - 如果Open-WebSearch不可用，自动使用`duckduckgo-search`
   - 如果`duckduckgo-search`也未安装，返回空结果（不影响其他功能）

**注意**：
- 备用方案有速率限制（约30 req/min）
- 但本地开发时搜索频率不高，通常够用
- 如果遇到速率限制，可以稍等片刻再试

### 方案2：连接到云服务器上的Open-WebSearch

**适用场景**：如果已经部署了云服务器，可以连接到服务器上的Open-WebSearch服务

**配置**：

```env
# backend/.env
# 连接到云服务器上的Open-WebSearch
OPEN_WEBSEARCH_MCP_URL=http://your-server-ip:3000/mcp
# 或使用域名
OPEN_WEBSEARCH_MCP_URL=http://your-domain.com:3000/mcp
```

**优点**：
- ✅ 无需本地Docker
- ✅ 使用多引擎搜索（无速率限制）
- ✅ 功能完整

**缺点**：
- ⚠️ 需要云服务器已部署
- ⚠️ 需要网络连接

### 方案3：使用NPX快速启动（轻量）

**适用场景**：需要完整功能，但不想使用Docker

**配置**：

```bash
# 在终端运行（保持运行）
DEFAULT_SEARCH_ENGINE=bing ENABLE_CORS=true npx open-websearch@latest
```

然后在 `backend/.env` 中配置：
```env
OPEN_WEBSEARCH_MCP_URL=http://localhost:3000/mcp
```

**优点**：
- ✅ 无需Docker
- ✅ 轻量级（比Docker占用资源少）
- ✅ 功能完整

**缺点**：
- ⚠️ 需要保持终端运行
- ⚠️ 占用一些系统资源

### 方案4：暂时禁用Web搜索功能

**适用场景**：开发阶段不需要Web搜索功能

**配置**：

```env
# backend/.env
# 不设置 OPEN_WEBSEARCH_MCP_URL
# 或设置为空
OPEN_WEBSEARCH_MCP_URL=
```

**代码行为**：
- Web搜索功能会自动降级
- 匹配度分析仍然正常工作
- 只是不会查找代言和品牌信息
- 不影响其他功能

## 🎯 推荐配置

### 开发阶段

**推荐**：使用方案1（备用搜索方案）

```bash
# 安装备用搜索库
cd backend
pip install duckduckgo-search
```

**优点**：
- 无需Docker
- 无需额外服务
- 功能基本可用（有速率限制，但开发时够用）

### 部署阶段

**推荐**：使用Docker Compose自动启动Open-WebSearch

```bash
cd docker
docker-compose up -d open-websearch
```

**优点**：
- 功能完整
- 多引擎搜索
- 无速率限制

## 📊 方案对比

| 方案 | Docker | 额外服务 | 功能完整度 | 推荐度 |
|------|--------|---------|-----------|--------|
| 方案1：备用搜索 | ❌ | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 方案2：连接云服务器 | ❌ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案3：NPX启动 | ❌ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 方案4：禁用搜索 | ❌ | ❌ | ⭐⭐ | ⭐⭐ |

## 🔧 代码自动降级机制

代码已经实现了自动降级机制：

1. **优先使用Open-WebSearch**：如果`OPEN_WEBSEARCH_MCP_URL`配置且服务可用
2. **降级到duckduckgo-search**：如果Open-WebSearch不可用，自动使用备用方案
3. **返回空结果**：如果都不可用，返回空结果（不影响其他功能）

**代码位置**：`backend/app/tools/websearch_tools.py`

```python
def web_search(query: str, max_results: int = 5, engines: Optional[list] = None):
    try:
        # 尝试使用Open-WebSearch MCP Server
        # ...
    except httpx.HTTPError as e:
        logger.warning(f"Open-WebSearch MCP服务器连接失败: {e}，尝试备用方案")
        # 自动降级到duckduckgo-search
        return _fallback_search(query, max_results)
```

## 📝 总结

**本地开发推荐**：
- ✅ 使用方案1（备用搜索方案）
- ✅ 安装`duckduckgo-search`：`pip install duckduckgo-search`
- ✅ 无需配置`OPEN_WEBSEARCH_MCP_URL`
- ✅ 代码自动使用备用方案

**云服务器部署**：
- ✅ 使用Docker Compose自动启动Open-WebSearch
- ✅ 功能完整，无速率限制

这样既能保证本地开发效率（无需Docker），又能保证部署质量（完整功能）。

