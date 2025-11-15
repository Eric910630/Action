# 使用PolarDB的云端部署指南

## 📋 你已经拥有的资源

1. ✅ **PolarDB**（已购买）
2. ✅ **域名**（已购买，9元/年）
3. ⏳ **云服务器**（还需要购买）

---

## 为什么还需要云服务器？

### PolarDB的作用
- ✅ 提供数据库服务（存储数据）
- ✅ 托管数据库，无需自己管理

### 云服务器的作用
- ✅ 运行应用代码（前端、后端、Celery）
- ✅ 处理业务逻辑
- ✅ 提供Web服务

**简单理解**：
- **PolarDB** = 数据库（存储数据）
- **云服务器** = 应用服务器（运行代码）

两者缺一不可！

---

## 第一步：购买云服务器

### 推荐配置

**最低配置**（适合初期试用）：
- CPU：2核
- 内存：4GB
- 硬盘：40GB SSD
- 带宽：3-5Mbps
- 系统：Ubuntu 22.04 LTS

**推荐服务商**：

#### 阿里云轻量应用服务器（推荐）⭐

**优势**：
- 新用户优惠大（24-34元/月）
- 与PolarDB同属阿里云，内网访问快
- 配置简单，适合新手

**购买步骤**：
1. 访问：https://www.aliyun.com/product/swas
2. 选择"轻量应用服务器"
3. 选择配置：2核4G，40G硬盘，3Mbps带宽
4. 选择系统：Ubuntu 22.04
5. **重要**：选择与PolarDB相同的地域（如：华东1-杭州）
6. 购买时长：建议先买1个月试用

**价格**：
- 新用户：24-34元/月
- 老用户：约60-80元/月

**为什么选择相同地域？**
- 服务器和PolarDB在同一地域，可以内网访问
- 内网访问速度快，延迟低
- 内网流量免费

---

## 第二步：配置PolarDB连接

### 1. 获取PolarDB连接信息

在阿里云控制台找到你的PolarDB实例，记录以下信息：

- **主地址**（读写地址）：`xxx.rwlb.rds.aliyuncs.com`
- **端口**：通常是 `5432`
- **数据库名**：你创建的数据库名
- **用户名**：数据库用户名
- **密码**：数据库密码

### 2. 配置白名单

**重要**：在PolarDB控制台配置白名单，允许云服务器访问：

1. 进入PolarDB控制台
2. 找到"数据安全性" → "白名单设置"
3. 添加云服务器的内网IP（推荐）或公网IP
4. 如果服务器和PolarDB在同一地域，使用内网IP（免费且快速）

**获取服务器内网IP**：
```bash
# 在服务器上执行
ip addr show | grep inet
# 或
hostname -I
```

---

## 第三步：部署应用（使用PolarDB）

### 1. 连接服务器

```bash
ssh root@你的服务器IP
```

### 2. 安装Docker和Docker Compose

```bash
# 更新系统
apt-get update && apt-get upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker

# 安装Docker Compose
apt-get install docker-compose -y
```

### 3. 上传项目代码

```bash
# 方式1：使用Git
cd /root
git clone 你的项目Git地址
cd Action

# 方式2：使用SCP（在本地执行）
scp -r Action root@服务器IP:/root/
```

### 4. 配置环境变量

```bash
cd /root/Action/backend
nano .env
```

**配置内容**：

```env
# ============================================
# PolarDB数据库配置（使用你购买的PolarDB）
# ============================================
# 方式1：使用完整URL（推荐）
DATABASE_URL=postgresql+psycopg2://用户名:密码@PolarDB地址:5432/数据库名

# 方式2：使用独立字段
DB_USER=你的PolarDB用户名
DB_PASSWORD=你的PolarDB密码
DB_HOST=你的PolarDB地址.rwlb.rds.aliyuncs.com
DB_PORT=5432
DB_NAME=你的数据库名

# ============================================
# Redis配置（仍然需要，用于Celery）
# ============================================
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ============================================
# DeepSeek API配置（必须配置）
# ============================================
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# ============================================
# 其他配置
# ============================================
TRENDRADAR_USE_DIRECT_CRAWLER=true
FIRECRAWL_ENABLED=false
VIDEO_ANALYZER_USE_LOCAL=true

# 生产环境配置
ENVIRONMENT=production
DEBUG=false
```

**重要**：
- 替换 `你的PolarDB地址`、`用户名`、`密码`、`数据库名` 为实际值
- 如果服务器和PolarDB在同一地域，使用**内网地址**（更快且免费）

### 5. 修改docker-compose.yml（移除PostgreSQL）

由于使用PolarDB，不需要在Docker中运行PostgreSQL。创建简化版的docker-compose.yml：

```bash
cd /root/Action/docker
cp docker-compose.yml docker-compose.yml.backup
nano docker-compose.yml
```

**修改后的docker-compose.yml**：

```yaml
version: '3.8'

services:
  # Redis（仍然需要，用于Celery）
  redis:
    image: redis:7.0-alpine
    container_name: vtics-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - vtics-network
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端API服务（连接到PolarDB）
  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: vtics-backend
    ports:
      - "8001:8001"
    environment:
      # 从.env文件读取PolarDB配置
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ../backend:/app
      - uploads_data:/app/uploads
      - ../backend/.env:/app/.env  # 挂载.env文件
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - vtics-network
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001"

  # Celery Worker（连接到PolarDB）
  celery-worker:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: vtics-celery-worker
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ../backend:/app
      - uploads_data:/app/uploads
      - ../backend/.env:/app/.env
    depends_on:
      - redis
      - backend
    networks:
      - vtics-network
    command: celery -A app.celery_app worker --loglevel=info --pool=solo

  # Celery Beat（连接到PolarDB）
  celery-beat:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: vtics-celery-beat
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ../backend:/app
      - ../backend/.env:/app/.env
    depends_on:
      - redis
      - backend
    networks:
      - vtics-network
    command: celery -A app.celery_app beat --loglevel=info

  # 前端服务（Nginx）
  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    container_name: vtics-frontend
    ports:
      - "3001:80"
    depends_on:
      - backend
    networks:
      - vtics-network

volumes:
  redis_data:
  uploads_data:

networks:
  vtics-network:
    driver: bridge
```

**主要变化**：
- ❌ 移除了 `postgres` 服务
- ✅ 所有服务通过环境变量连接PolarDB
- ✅ 挂载 `.env` 文件到容器中

### 6. 初始化数据库

```bash
cd /root/Action/backend
source venv/bin/activate  # 如果使用虚拟环境
# 或直接使用python3

# 运行数据库迁移
alembic upgrade head
```

### 7. 启动服务

```bash
cd /root/Action/docker
docker-compose build
docker-compose up -d
docker-compose ps
```

---

## 第四步：配置域名和Nginx

### 1. 配置域名解析

在域名管理后台，将域名指向服务器IP：

| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|--------|-----|
| A | @ | 你的服务器IP | 600 |
| A | www | 你的服务器IP | 600 |

### 2. 安装和配置Nginx

```bash
# 安装Nginx
apt-get install nginx -y

# 创建配置文件
nano /etc/nginx/sites-available/vtics
```

**配置文件内容**：

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 前端
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 启用配置
ln -s /etc/nginx/sites-available/vtics /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 3. 配置SSL证书

```bash
# 安装Certbot
apt-get install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d 你的域名.com -d www.你的域名.com
```

---

## 优势对比

### 使用PolarDB的优势

| 优势 | 说明 |
|------|------|
| ✅ **无需管理数据库** | PolarDB是托管服务，自动备份、监控、维护 |
| ✅ **高可用性** | PolarDB提供99.95%的可用性保证 |
| ✅ **自动备份** | 自动备份，无需担心数据丢失 |
| ✅ **性能更好** | 专为云环境优化，性能更稳定 |
| ✅ **简化部署** | 不需要在服务器上运行PostgreSQL容器 |
| ✅ **节省资源** | 服务器资源可以全部用于应用 |

### 成本对比

| 方案 | 数据库成本 | 服务器成本 | 总计 |
|------|-----------|-----------|------|
| **使用PolarDB** | PolarDB费用 | 24-80元/月 | PolarDB + 24-80元/月 |
| **使用Docker PostgreSQL** | 0元 | 24-80元/月 | 24-80元/月 |

**注意**：虽然PolarDB有额外费用，但提供了更好的可靠性和性能。

---

## 成本总结

| 项目 | 费用 | 说明 |
|------|------|------|
| 域名 | 9元/年 | 已购买 |
| PolarDB | 已购买 | 你的PolarDB费用 |
| 云服务器 | 24-80元/月 | 新用户24-34元/月 |
| SSL证书 | 免费 | Let's Encrypt |
| **总计** | **PolarDB费用 + 24-80元/月** |  |

---

## 快速部署步骤总结

```bash
# 1. 购买云服务器（与PolarDB同地域）

# 2. 连接服务器
ssh root@服务器IP

# 3. 安装Docker
curl -fsSL https://get.docker.com | bash
apt-get install docker-compose -y

# 4. 上传代码
cd /root
git clone 你的项目地址
# 或使用scp上传

# 5. 配置环境变量
cd Action/backend
nano .env
# 填入PolarDB连接信息

# 6. 修改docker-compose.yml（移除postgres服务）

# 7. 初始化数据库
alembic upgrade head

# 8. 启动服务
cd ../docker
docker-compose up -d

# 9. 配置Nginx和SSL
# （参考上面的步骤）
```

---

## 注意事项

### 1. 网络配置

- ✅ **推荐**：服务器和PolarDB在同一地域，使用内网地址
- ⚠️ **注意**：配置PolarDB白名单，允许服务器访问

### 2. 安全配置

- ✅ 不要在代码中硬编码数据库密码
- ✅ 使用环境变量管理敏感信息
- ✅ 定期更新数据库密码

### 3. 备份策略

- ✅ PolarDB自动备份（已配置）
- ✅ 建议定期导出数据作为额外备份

---

## 需要帮助？

如果在部署过程中遇到问题：
1. 检查PolarDB白名单配置
2. 检查环境变量配置
3. 查看日志：`docker-compose logs -f`
4. 测试数据库连接

**祝你部署顺利！** 🚀

