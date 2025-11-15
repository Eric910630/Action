# TrendRadar MCP 服务配置指南

## 概述

Action 项目通过 MCP（Model Context Protocol）协议调用 TrendRadar 服务来获取热点数据。

## 配置步骤

### 1. 部署 TrendRadar MCP 服务

#### 1.1 克隆 TrendRadar 项目

```bash
# 在合适的位置克隆项目（不要放在Action项目内）
cd ~/Desktop  # 或你喜欢的目录
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar
```

#### 1.2 安装依赖

```bash
# 根据TrendRadar的README安装依赖
# 通常需要：
pip install -r requirements.txt
# 或使用uv（如果项目推荐）
uv pip install -r requirements.txt
```

#### 1.3 启动 MCP 服务器

```bash
# 启动MCP HTTP服务器（默认端口3333）
uv run python -m mcp_server.server --transport http --port 3333

# 或者使用自定义端口
uv run python -m mcp_server.server --transport http --port 33333
```

**注意**：确保 MCP 服务器持续运行，Action 项目才能正常调用。

### 2. 配置 Action 项目

#### 2.1 环境变量配置

在 `backend/.env` 文件中添加：

```env
# TrendRadar MCP服务配置
TRENDRADAR_API_URL=http://localhost:3333/mcp
TRENDRADAR_API_KEY=  # 如果MCP服务需要认证，填写API Key（通常不需要）
TRENDRADAR_USE_MCP=true  # 明确指定使用MCP协议
```

#### 2.2 配置说明

- **TRENDRADAR_API_URL**: MCP 服务的完整 URL，必须包含 `/mcp` 路径
  - 本地部署：`http://localhost:3333/mcp`
  - 远程部署：`http://your-server:3333/mcp`
  
- **TRENDRADAR_API_KEY**: 如果 TrendRadar MCP 服务启用了认证，填写 API Key（通常不需要）

- **TRENDRADAR_USE_MCP**: 是否使用 MCP 协议
  - `true`: 使用 MCP 协议调用
  - `false`: 使用传统 HTTP API（如果 TrendRadar 提供）

### 3. 验证配置

#### 3.1 检查 MCP 服务是否运行

```bash
# 检查端口是否被占用
lsof -i :3333  # Mac/Linux
netstat -ano | findstr :3333  # Windows

# 测试MCP服务是否可访问
curl http://localhost:3333/mcp
```

#### 3.2 测试 Action 项目连接

```bash
cd /Users/eric/Desktop/Action/backend

# 运行测试
pytest tests/e2e/test_complete_workflow_real_llm.py::TestCompleteWorkflowRealLLM::test_complete_workflow_with_real_llm -v -s
```

### 4. 使用方式

配置完成后，Action 项目会自动通过 MCP 协议调用 TrendRadar 服务：

```python
from app.utils.trendradar import TrendRadarClient

client = TrendRadarClient()
hotspots = await client.get_hotspots(platform="douyin")
```

## 故障排查

### 问题1: MCP 服务无法启动

**检查步骤**：
1. 确认端口 3333 未被占用
2. 检查 TrendRadar 项目依赖是否安装完整
3. 查看 TrendRadar 项目的错误日志

**解决方案**：
```bash
# 尝试使用其他端口
uv run python -m mcp_server.server --transport http --port 33333

# 然后更新.env中的URL
TRENDRADAR_API_URL=http://localhost:33333/mcp
```

### 问题2: Action 项目无法连接到 MCP 服务

**检查步骤**：
1. 确认 MCP 服务正在运行
2. 检查防火墙设置
3. 验证 URL 配置是否正确（必须包含 `/mcp`）

**解决方案**：
```bash
# 测试连接
curl -X POST http://localhost:3333/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### 问题3: MCP 调用返回错误

**可能原因**：
1. TrendRadar 的工具名称不匹配
2. 参数格式不正确
3. TrendRadar 数据不存在（需要先运行爬虫）

**解决方案**：
- 查看 TrendRadar 项目的 MCP 工具文档
- 确认已运行过 TrendRadar 的爬虫，有数据输出
- 检查 `TrendRadar/output` 目录是否有数据文件

## 注意事项

1. **数据依赖**：TrendRadar MCP 服务需要先运行爬虫获取数据，才能返回热点
2. **服务持续运行**：确保 MCP 服务在 Action 项目运行期间一直保持运行
3. **端口冲突**：如果端口 3333 被占用，可以修改为其他端口
4. **网络访问**：如果 Action 和 TrendRadar 不在同一机器，确保网络可达

## 参考链接

- [TrendRadar GitHub 仓库](https://github.com/sansan0/TrendRadar)
- [MCP 协议文档](https://modelcontextprotocol.io/)

