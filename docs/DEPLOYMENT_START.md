# 🚀 开始部署上线

## ✅ 流程确认

**是的，你的理解完全正确！**

```
本地开发测试 → Git提交 → 服务器更新 → 直接看到线上结果
```

**更新耗时**：通常1-2分钟

## 📋 部署前检查

### 请确认以下资源已准备：

- [ ] **云服务器**（2核4GB，Ubuntu 22.04）
  - 已购买：□ 是
  - IP地址：39.102.60.67

- [ ] **PolarDB for PostgreSQL**
  - 已购买：□ 是
  - 连接信息已获取：□ 是

- [ ] **域名**
  - 已购买：□ 是
  - 域名：actionscript.fun

- [ ] **DeepSeek API Key**
  - 已获取：□ 是

## 🚀 快速部署步骤

### 第一步：准备服务器信息

请准备以下信息：

**PolarDB连接信息**：
- 主机地址：pe-2ze3jxdxfxo2txk1r.rwlb.rds.aliyuncs.com
- 端口：5432
- 数据库名：action_script_db
- 用户名：action_scipter
- 密码：z_13731790081s

**服务器信息**：
- IP地址：39.102.60.67
- SSH访问：□ 密码 z_13731790081

**域名信息**（可选，可以先使用IP访问）：
- 域名：actionscript.fun

### 第二步：连接服务器

```bash
ssh root@你的服务器IP
```

### 第三步：安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 第四步：上传代码

**方式1：使用Git（推荐）**

```bash
# 在服务器上
cd /root
git clone 你的Git仓库地址 Action
cd Action
```

**方式2：使用SCP上传**

```bash
# 在本地执行
cd ~/Desktop
tar -czf Action.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  Action

# 上传到服务器
scp Action.tar.gz root@服务器IP:/root/

# 在服务器上解压
ssh root@服务器IP
cd /root
tar -xzf Action.tar.gz
cd Action
```

### 第五步：配置环境变量

```bash
# 在服务器上
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

### 第六步：启动服务

```bash
# 在服务器上
cd /root/Action/docker

# 使用PolarDB配置（推荐）
docker-compose -f docker-compose.polardb.yml up -d

# 或使用标准配置（如果使用Docker PostgreSQL）
# docker-compose up -d
```

### 第七步：初始化数据库

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml exec backend alembic upgrade head
```

### 第八步：验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose.polardb.yml ps

# 查看日志
docker-compose -f docker-compose.polardb.yml logs -f
```

**访问地址**：
- 前端：`http://服务器IP:3001`
- 后端API文档：`http://服务器IP:8001/docs`
- 健康检查：`http://服务器IP:8001/health`

### 第九步：配置域名（可选）

如果需要使用域名访问，参考：
- [云端部署完整指南 - Nginx配置](./CLOUD_DEPLOYMENT_GUIDE.md#第六步配置nginx反向代理)
- [云端部署完整指南 - SSL证书](./CLOUD_DEPLOYMENT_GUIDE.md#第七步配置ssl证书https)

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

## 📝 详细文档

- [快速部署指南](./QUICK_DEPLOYMENT_GUIDE.md) - 快速部署步骤
- [部署检查清单](./DEPLOYMENT_CHECKLIST.md) - 完整的检查清单
- [云端部署完整指南](./CLOUD_DEPLOYMENT_GUIDE.md) - 详细的部署步骤
- [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md) - PolarDB专用配置

## 🎯 开始部署

准备好了吗？让我们开始部署！

**请告诉我**：
1. 云服务器是否已购买？
2. PolarDB连接信息是否已获取？
3. 域名是否已购买？
4. 是否需要我协助配置？

我可以：
- ✅ 提供详细的部署步骤
- ✅ 协助配置环境变量
- ✅ 排查部署问题
- ✅ 验证部署结果

准备好了就告诉我，我们开始部署！

