# 快速部署指南

## 📋 部署流程确认

**是的，你的理解完全正确！**

```
本地开发测试 → Git提交 → 服务器更新 → 直接看到线上结果
```

**更新耗时**：通常1-2分钟

## ✅ 部署前检查

### 1. 资源准备确认

请确认以下资源已准备：

- [ ] **云服务器**（2核4GB，Ubuntu 22.04）
- [ ] **PolarDB for PostgreSQL**（已购买）
- [ ] **域名**（已购买）
- [ ] **DeepSeek API Key**（已获取）

### 2. 信息收集

请准备以下信息：

**PolarDB连接信息**：
- 主机地址：________________
- 端口：5432
- 数据库名：________________
- 用户名：________________
- 密码：________________

**服务器信息**：
- IP地址：________________
- SSH访问方式：□ 密码  □ 密钥

**域名信息**：
- 域名：________________

## 🚀 快速部署步骤

### 第一步：连接服务器

```bash
ssh root@你的服务器IP
```

### 第二步：运行快速部署脚本

```bash
# 如果使用Git仓库
cd /root
git clone 你的Git仓库地址 Action
cd Action
chmod +x scripts/quick_deploy.sh
./scripts/quick_deploy.sh

# 或手动部署（见下方）
```

### 第三步：配置环境变量

```bash
cd /root/Action/backend
nano .env
```

**必需配置**：

```env
# PolarDB连接信息
DATABASE_URL=postgresql+psycopg2://用户名:密码@主机:5432/数据库名

# Redis（使用Docker Redis）
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# DeepSeek API
DEEPSEEK_API_KEY=你的API_Key

# Open-WebSearch（使用Docker服务）
OPEN_WEBSEARCH_MCP_URL=http://open-websearch:3000/mcp

# 环境标识
ENVIRONMENT=production
```

### 第四步：启动服务

```bash
cd /root/Action/docker

# 使用PolarDB配置
docker-compose -f docker-compose.polardb.yml up -d

# 或使用标准配置（如果使用Docker PostgreSQL）
# docker-compose up -d
```

### 第五步：初始化数据库

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml exec backend alembic upgrade head
```

### 第六步：配置域名和Nginx（可选）

如果需要使用域名访问，参考：
- [云端部署完整指南 - Nginx配置](./CLOUD_DEPLOYMENT_GUIDE.md#第六步配置nginx反向代理)
- [云端部署完整指南 - SSL证书](./CLOUD_DEPLOYMENT_GUIDE.md#第七步配置ssl证书https)

## ✅ 部署后验证

### 1. 检查服务状态

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml ps
```

应该看到所有服务都是 `Up` 状态。

### 2. 测试访问

- **前端页面**：`http://服务器IP:3001`
- **后端API文档**：`http://服务器IP:8001/docs`
- **健康检查**：`http://服务器IP:8001/health`

### 3. 查看日志

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml logs -f
```

## 🔄 后续更新流程（确认）

### 标准流程

```bash
# 1. 本地开发测试
cd ~/Desktop/Action
./start_dev.sh
# 在本地测试功能...

# 2. Git提交
git add .
git commit -m "新功能或优化"
git push

# 3. 服务器更新（1-2分钟）
ssh root@服务器IP
cd /root/Action
git pull
cd docker
docker-compose -f docker-compose.polardb.yml restart backend celery-worker celery-beat frontend

# 4. 验证上线
# 访问域名或服务器IP，测试新功能
```

**是的，就是这样！** 更新后立即可以看到线上结果。

## 📝 部署检查清单

使用 [部署检查清单](./DEPLOYMENT_CHECKLIST.md) 确保所有步骤都完成。

## 🔗 详细文档

- [部署检查清单](./DEPLOYMENT_CHECKLIST.md) - 完整的检查清单
- [云端部署完整指南](./CLOUD_DEPLOYMENT_GUIDE.md) - 详细的部署步骤
- [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md) - PolarDB专用配置
- [部署与更新流程](./DEPLOYMENT_WORKFLOW.md) - 更新流程说明

## 🎯 开始部署

准备好了吗？让我们开始部署！

1. **确认资源**：云服务器、PolarDB、域名都已准备好
2. **收集信息**：PolarDB连接信息、服务器IP等
3. **开始部署**：按照上述步骤执行

如果遇到问题，随时告诉我！

