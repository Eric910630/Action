# Open-WebSearch 快速配置指南

## ✅ 配置状态

已完成的配置：
- ✅ 代码已更新为使用Open-WebSearch MCP Server
- ✅ Docker Compose配置已添加Open-WebSearch服务
- ✅ 环境变量已配置

## 🚀 启动服务

### 方式1：使用Docker Compose（推荐）

```bash
cd docker
docker-compose up -d open-websearch
```

### 方式2：单独启动Open-WebSearch

```bash
docker run -d \
  --name vtics-open-websearch \
  -p 3000:3000 \
  -e ENABLE_CORS=true \
  -e CORS_ORIGIN=* \
  -e DEFAULT_SEARCH_ENGINE=bing \
  --network vtics-network \
  ghcr.io/aas-ee/open-web-search:latest
```

### 方式3：使用NPX（本地开发）

```bash
# 在终端运行（保持运行）
DEFAULT_SEARCH_ENGINE=bing ENABLE_CORS=true npx open-websearch@latest
```

## 🔍 验证配置

### 1. 检查服务状态

```bash
# 检查容器是否运行
docker ps | grep open-websearch

# 检查服务是否响应
curl http://localhost:3000/mcp
```

### 2. 测试搜索功能

```bash
# 测试MCP搜索接口
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search",
      "arguments": {
        "query": "王楚钦 代言",
        "limit": 3,
        "engines": ["bing", "duckduckgo"]
      }
    }
  }'
```

## 📝 环境变量说明

### Docker Compose环境变量

在`docker-compose.yml`中已配置：
- `OPEN_WEBSEARCH_MCP_URL=http://open-websearch:3000/mcp`（容器内访问）
- 服务端口：`3000`

### 本地开发环境变量

如果使用本地开发（不使用Docker），在`backend/.env`中添加：

```env
# Open-WebSearch MCP Server配置
OPEN_WEBSEARCH_MCP_URL=http://localhost:3000/mcp
```

## 🔧 故障排查

### 问题1：服务无法连接

**症状**：`Connection refused` 或 `无法连接到Open-WebSearch服务`

**解决方案**：
1. 检查服务是否运行：`docker ps | grep open-websearch`
2. 检查端口是否被占用：`lsof -i :3000`
3. 查看服务日志：`docker logs vtics-open-websearch`

### 问题2：CORS错误

**症状**：浏览器控制台显示CORS错误

**解决方案**：
- 确保环境变量 `ENABLE_CORS=true` 和 `CORS_ORIGIN=*` 已设置
- 重启容器：`docker-compose restart open-websearch`

### 问题3：搜索返回空结果

**症状**：搜索功能返回空结果或错误

**解决方案**：
1. 检查服务日志：`docker logs vtics-open-websearch`
2. 尝试不同的搜索引擎：`engines: ["bing", "baidu"]`
3. 检查网络连接

## 📊 服务信息

- **服务名称**：`vtics-open-websearch`
- **端口**：`3000`
- **MCP端点**：`http://localhost:3000/mcp`
- **健康检查**：`http://localhost:3000/mcp`

## 🎯 下一步

配置完成后，系统会自动：
1. 在匹配度分析时检测热点中的知名人物
2. 使用多引擎组合搜索代言信息
3. 如果找到匹配的代言品牌，提升匹配度评分

无需额外配置，开箱即用！

## 📝 更新日期

- **2025-01-14**：完成Open-WebSearch配置

