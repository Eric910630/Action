# 部署命令清单

## 📋 部署信息

- **服务器IP**：39.102.60.67
- **域名**：actionscript.fun
- **PolarDB主机**：pe-2ze3jxdxfxo2txk1r.rwlb.rds.aliyuncs.com
- **数据库名**：action_script_db
- **用户名**：action_scipter

## 🚀 部署步骤

### 第一步：连接服务器

```bash
ssh root@39.102.60.67
# 输入密码：z_13731790081
```

### 第二步：安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 第三步：安装Git

```bash
apt update
apt install -y git
```

### 第四步：上传代码

**方式1：使用SCP（推荐，因为还没有Git仓库）**

```bash
# 在本地执行（Mac）
cd ~/Desktop
tar -czf Action.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='backend/venv' \
  --exclude='frontend/node_modules' \
  Action

# 上传到服务器
scp Action.tar.gz root@39.102.60.67:/root/

# 在服务器上解压
ssh root@39.102.60.67
cd /root
tar -xzf Action.tar.gz
cd Action
```

### 第五步：配置环境变量

```bash
# 在服务器上
cd /root/Action/backend

# 创建.env文件
nano .env
```

**配置内容**（请填写DeepSeek API Key）：

```env
# PolarDB连接信息
DATABASE_URL=postgresql+psycopg2://action_scipter:z_13731790081s@pe-2ze3jxdxfxo2txk1r.rwlb.rds.aliyuncs.com:5432/action_script_db

# Redis配置（使用Docker Redis）
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# DeepSeek API（必须填写！）
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# Open-WebSearch（使用Docker服务）
OPEN_WEBSEARCH_MCP_URL=http://open-websearch:3000/mcp

# 其他配置
TRENDRADAR_USE_DIRECT_CRAWLER=true
FIRECRAWL_ENABLED=false
VIDEO_ANALYZER_USE_LOCAL=true

# 生产环境配置
ENVIRONMENT=production
DEBUG=false
MATCH_SCORE_THRESHOLD=0.3
```

### 第六步：配置PolarDB白名单

**重要**：在阿里云控制台配置PolarDB白名单，允许服务器访问：

1. 登录阿里云控制台
2. 进入PolarDB控制台
3. 找到你的PolarDB实例
4. 进入"数据安全性" → "白名单设置"
5. 添加服务器IP：`39.102.60.67`
6. 或添加：`0.0.0.0/0`（允许所有IP，仅用于测试）

### 第七步：启动服务

```bash
# 在服务器上
cd /root/Action/docker

# 使用PolarDB配置启动
docker-compose -f docker-compose.polardb.yml up -d

# 查看服务状态
docker-compose -f docker-compose.polardb.yml ps
```

### 第八步：初始化数据库

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml exec backend alembic upgrade head
```

### 第九步：验证部署

```bash
# 查看服务状态
docker-compose -f docker-compose.polardb.yml ps

# 查看日志
docker-compose -f docker-compose.polardb.yml logs -f
```

**访问地址**：
- 前端：`http://39.102.60.67:3001`
- 后端API文档：`http://39.102.60.67:8001/docs`
- 健康检查：`http://39.102.60.67:8001/health`

### 第十步：配置域名和Nginx（可选）

如果需要使用域名访问，参考：
- [云端部署完整指南 - Nginx配置](./CLOUD_DEPLOYMENT_GUIDE.md#第六步配置nginx反向代理)
- [云端部署完整指南 - SSL证书](./CLOUD_DEPLOYMENT_GUIDE.md#第七步配置ssl证书https)

## 🔄 后续更新流程

```bash
# 1. 本地开发测试
cd ~/Desktop/Action
./start_dev.sh
# 测试功能...

# 2. Git提交（如果创建了Git仓库）
git add .
git commit -m "新功能"
git push

# 3. 服务器更新（1-2分钟）
ssh root@39.102.60.67
cd /root/Action
# 如果使用Git：git pull
# 或使用SCP重新上传
cd docker
docker-compose -f docker-compose.polardb.yml restart backend celery-worker celery-beat frontend

# 4. 验证上线
# 访问 http://39.102.60.67:3001 或 http://actionscript.fun
```

