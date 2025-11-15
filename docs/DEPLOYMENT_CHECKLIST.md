# 部署上线检查清单

## ✅ 部署前准备

### 1. 资源准备

- [ ] **云服务器**（2核4GB，Ubuntu 22.04）
  - 地域：与PolarDB相同（推荐）
  - 已购买：□ 是  □ 否

- [ ] **PolarDB for PostgreSQL**
  - 已购买：□ 是  □ 否
  - 连接信息已获取：□ 是  □ 否

- [ ] **域名**
  - 已购买：□ 是  □ 否
  - 域名：________________

### 2. 配置信息

- [ ] **PolarDB连接信息**
  - 主机：________________
  - 端口：5432
  - 数据库名：________________
  - 用户名：________________
  - 密码：________________

- [ ] **DeepSeek API Key**
  - 已配置：□ 是  □ 否
  - API Key：________________

- [ ] **服务器信息**
  - IP地址：________________
  - SSH密钥：________________
  - root密码：________________

### 3. 代码准备

- [ ] **Git仓库**
  - 已创建：□ 是  □ 否
  - 仓库地址：________________
  - 代码已提交：□ 是  □ 否

- [ ] **环境变量**
  - `backend/.env` 已配置：□ 是  □ 否
  - 所有必需配置已填写：□ 是  □ 否

## 🚀 部署步骤

### 第一步：准备服务器

1. **连接服务器**
   ```bash
   ssh root@你的服务器IP
   ```

2. **安装Docker和Docker Compose**
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

3. **安装Git**
   ```bash
   apt update
   apt install -y git
   ```

### 第二步：上传代码

**方式1：使用Git（推荐）**

```bash
# 在服务器上
cd /root
git clone 你的Git仓库地址 Action
# 或如果已有仓库
cd /root/Action
git pull
```

**方式2：使用SCP上传**

```bash
# 在本地
cd ~/Desktop
tar -czf Action.tar.gz --exclude='node_modules' --exclude='venv' --exclude='.git' Action
scp Action.tar.gz root@服务器IP:/root/

# 在服务器上
cd /root
tar -xzf Action.tar.gz
```

### 第三步：配置环境变量

```bash
# 在服务器上
cd /root/Action/backend
nano .env
```

配置以下内容：

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

# 其他配置
ENVIRONMENT=production
```

### 第四步：启动服务

```bash
# 在服务器上
cd /root/Action/docker

# 如果使用PolarDB
docker-compose -f docker-compose.polardb.yml up -d

# 或使用标准配置
docker-compose up -d
```

### 第五步：初始化数据库

```bash
# 在服务器上
cd /root/Action/docker
docker-compose exec backend alembic upgrade head
```

### 第六步：配置Nginx反向代理

```bash
# 在服务器上
apt install -y nginx

# 创建Nginx配置
nano /etc/nginx/sites-available/action
```

配置内容（参考 `docs/CLOUD_DEPLOYMENT_GUIDE.md`）

### 第七步：配置SSL证书（HTTPS）

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d 你的域名
```

### 第八步：配置防火墙

```bash
# 允许HTTP和HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

## ✅ 部署后验证

- [ ] 访问域名，前端页面正常显示
- [ ] API文档可以访问：`https://你的域名/api/docs`
- [ ] 健康检查通过：`https://你的域名/api/health`
- [ ] 热点抓取功能正常
- [ ] 脚本生成功能正常

## 🔄 后续更新流程

### 标准更新流程

```bash
# 1. 本地开发测试
./start_dev.sh
# 测试功能...

# 2. Git提交
git add .
git commit -m "新功能"
git push

# 3. 服务器更新
ssh root@服务器IP
cd /root/Action
git pull
cd docker
docker-compose restart backend celery-worker celery-beat frontend

# 4. 验证上线
# 访问域名，测试新功能
```

**耗时**：通常1-2分钟

## 📝 注意事项

1. **数据库备份**：重要更新前备份数据库
2. **选择更新时间**：选择用户使用较少的时间段
3. **监控日志**：更新后查看日志确认
4. **准备回滚**：如果出现问题，可以快速回滚

## 🔗 相关文档

- [云端部署完整指南](./CLOUD_DEPLOYMENT_GUIDE.md)
- [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md)
- [部署与更新流程](./DEPLOYMENT_WORKFLOW.md)

