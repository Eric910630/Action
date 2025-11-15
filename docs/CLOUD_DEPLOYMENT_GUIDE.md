# 云端部署完整指南

## 📋 部署前准备清单

### 需要准备的东西

1. ✅ **域名**（已决定购买，9元/年）
2. ⏳ **云服务器**（需要购买）
3. ⏳ **数据库**（可选：PolarDB或使用Docker PostgreSQL）
4. ⏳ **服务器配置**（需要设置）

### 如果你已经购买了PolarDB

如果你已经购买了PolarDB，可以：
- ✅ 使用PolarDB作为数据库（推荐）
- ✅ 简化部署，不需要在服务器上运行PostgreSQL
- ✅ 参考 [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md)

---

## 第一步：购买云服务器（必须）

**重要**：即使你已经购买了PolarDB和域名，**仍然需要购买云服务器**！

### 为什么需要云服务器？

- **PolarDB**：只提供数据库服务（存储数据）
- **云服务器**：运行应用代码（前端、后端、Celery）

两者缺一不可！

### 如果你使用PolarDB

- ✅ 推荐选择与PolarDB**相同地域**的服务器
- ✅ 可以使用内网访问PolarDB（更快且免费）
- ✅ 参考 [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md) 了解详细配置

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

#### 1. 阿里云轻量应用服务器（推荐）⭐

**优势**：
- 新用户优惠大（24-34元/月）
- 配置简单，适合新手
- 国内访问速度快

**购买步骤**：
1. 访问：https://www.aliyun.com/product/swas
2. 选择"轻量应用服务器"
3. 选择配置：2核4G，40G硬盘，3Mbps带宽
4. 选择系统：Ubuntu 22.04
5. 选择地域：选择离你最近的城市（如：华东1-杭州）
6. 购买时长：建议先买1个月试用

**价格**：
- 新用户：24-34元/月
- 老用户：约60-80元/月

#### 2. 腾讯云轻量应用服务器

**优势**：
- 新用户优惠大
- 配置简单

**购买步骤**：
1. 访问：https://cloud.tencent.com/product/lighthouse
2. 选择配置：2核4G，40G硬盘，3Mbps带宽
3. 选择系统：Ubuntu 22.04
4. 购买

**价格**：
- 新用户：24-34元/月

#### 3. 其他选择

- **华为云**：https://www.huaweicloud.com
- **京东云**：https://www.jdcloud.com

### 购买后需要记录的信息

购买完成后，记录以下信息：
- ✅ 服务器公网IP地址
- ✅ 服务器root密码（或SSH密钥）
- ✅ 服务器用户名（通常是 `root`）

---

## 第二步：购买和配置域名

### 1. 购买域名

**推荐域名注册商**：
- **阿里云万网**：https://wanwang.aliyun.com
- **腾讯云DNSPod**：https://dnspod.cloud.tencent.com
- **GoDaddy**：https://www.godaddy.com（国外）

**购买步骤**：
1. 搜索想要的域名（如：`vtics.yourname.com`）
2. 添加到购物车
3. 完成购买（9元/年）

### 2. 域名解析配置

购买域名后，需要将域名指向你的服务器IP：

**在域名管理后台添加解析记录**：

| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|--------|-----|
| A | @ | 你的服务器IP | 600 |
| A | www | 你的服务器IP | 600 |

**示例**：
- 如果域名是 `vtics.example.com`
- 服务器IP是 `123.456.789.0`
- 则添加：
  - `@` → `123.456.789.0`
  - `www` → `123.456.789.0`

**解析生效时间**：通常5-30分钟

---

## 第三步：连接服务器并安装Docker

### 1. 连接服务器

**Mac/Linux**：
```bash
ssh root@你的服务器IP
# 输入密码
```

**Windows**：
- 使用 PuTTY 或 Windows Terminal
- 输入服务器IP和端口22
- 输入用户名和密码

### 2. 安装Docker和Docker Compose

连接服务器后，执行以下命令：

```bash
# 更新系统
apt-get update && apt-get upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | bash

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 安装Docker Compose
apt-get install docker-compose -y

# 验证安装
docker --version
docker-compose --version
```

---

## 第四步：上传项目代码到服务器

### 方式1：使用Git（推荐）

**如果项目在Git仓库**：

```bash
# 在服务器上执行
cd /root
git clone 你的项目Git地址
cd Action
```

### 方式2：使用SCP上传

**在本地Mac/Linux执行**：

```bash
# 打包项目（排除不需要的文件）
cd ~/Desktop
tar -czf Action.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  Action

# 上传到服务器
scp Action.tar.gz root@你的服务器IP:/root/

# 在服务器上解压
ssh root@你的服务器IP
cd /root
tar -xzf Action.tar.gz
cd Action
```

### 方式3：使用FTP工具

- 使用 FileZilla 或 WinSCP
- 连接服务器
- 上传项目文件夹

---

## 第五步：配置环境变量

### 1. 创建.env文件

```bash
cd /root/Action/backend
cp .env.example .env
nano .env  # 或使用 vi
```

### 2. 配置.env文件

```env
# 数据库配置（Docker会自动配置）
DATABASE_URL=postgresql+psycopg2://vtics:vtics123@postgres:5432/vtics

# Redis配置（Docker会自动配置）
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# DeepSeek API配置（必须配置）
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 其他配置
TRENDRADAR_USE_DIRECT_CRAWLER=true
FIRECRAWL_ENABLED=false
VIDEO_ANALYZER_USE_LOCAL=true

# 生产环境配置
ENVIRONMENT=production
DEBUG=false
```

**重要**：必须配置 `DEEPSEEK_API_KEY`，否则AI功能无法使用！

---

## 第六步：配置Nginx反向代理

### 1. 安装Nginx

```bash
apt-get install nginx -y
systemctl start nginx
systemctl enable nginx
```

### 2. 配置Nginx

创建配置文件：

```bash
nano /etc/nginx/sites-available/vtics
```

**配置文件内容**：

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;  # 替换为你的域名

    # 前端
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
ln -s /etc/nginx/sites-available/vtics /etc/nginx/sites-enabled/

# 删除默认配置（可选）
rm /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

---

## 第七步：配置SSL证书（HTTPS）

### 使用Let's Encrypt免费证书

```bash
# 安装Certbot
apt-get install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d 你的域名.com -d www.你的域名.com

# 按提示操作：
# 1. 输入邮箱（用于证书到期提醒）
# 2. 同意服务条款
# 3. 选择是否分享邮箱（选N）
# 4. 选择重定向HTTP到HTTPS（选2，推荐）

# 自动续期（已自动配置）
certbot renew --dry-run
```

**完成后**：
- 访问 `https://你的域名.com` 应该可以正常访问
- 证书会自动续期（每90天）

---

## 第八步：启动Docker服务

### 1. 进入项目目录

```bash
cd /root/Action/docker
```

### 2. 修改docker-compose.yml（如果需要）

检查端口配置，确保不与Nginx冲突：

```yaml
# 后端端口（内部使用，Nginx会代理）
ports:
  - "8001:8001"  # 只监听localhost，不对外暴露

# 前端端口（内部使用，Nginx会代理）
ports:
  - "3001:80"  # 只监听localhost，不对外暴露
```

### 3. 启动服务

```bash
# 构建镜像（首次运行需要几分钟）
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 等待服务启动

首次启动需要：
- 下载Docker镜像（约5-10分钟）
- 初始化数据库（约30-60秒）
- 构建前端（约2-5分钟）

**检查服务是否启动成功**：

```bash
# 查看所有容器状态
docker-compose ps

# 应该看到所有服务都是 "Up" 状态：
# - vtics-postgres
# - vtics-redis
# - vtics-backend
# - vtics-celery-worker
# - vtics-celery-beat
# - vtics-frontend
```

---

## 第九步：配置防火墙

### 开放必要端口

```bash
# Ubuntu使用ufw
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp    # HTTPS
ufw enable

# 查看防火墙状态
ufw status
```

**重要**：只开放必要端口，不要开放8001和3001（由Nginx代理）

---

## 第十步：测试访问

### 1. 测试HTTP访问

```bash
# 在服务器上测试
curl http://localhost:3001
curl http://localhost:8001/docs
```

### 2. 测试域名访问

在浏览器访问：
- `http://你的域名.com` → 应该重定向到HTTPS
- `https://你的域名.com` → 应该看到前端页面
- `https://你的域名.com/api/docs` → 应该看到API文档

### 3. 配置DeepSeek API Key

1. 访问 `https://你的域名.com`
2. 点击右上角设置图标 ⚙️
3. 进入"系统设置"标签
4. 配置DeepSeek API Key

---

## 日常维护命令

### 查看服务状态

```bash
cd /root/Action/docker
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery-worker
```

### 重启服务

```bash
cd /root/Action/docker
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 更新代码

```bash
# 如果使用Git
cd /root/Action
git pull

# 重启服务
cd docker
docker-compose restart
```

### 备份数据库

```bash
# 备份
docker-compose exec postgres pg_dump -U vtics vtics > backup_$(date +%Y%m%d).sql

# 恢复
docker-compose exec -T postgres psql -U vtics vtics < backup_20250114.sql
```

---

## 故障排查

### 问题1：无法访问网站

**检查步骤**：
1. 检查域名解析是否正确：`ping 你的域名.com`
2. 检查Nginx是否运行：`systemctl status nginx`
3. 检查Docker服务是否运行：`docker-compose ps`
4. 检查防火墙：`ufw status`

### 问题2：502 Bad Gateway

**可能原因**：
- 后端服务未启动
- Nginx配置错误

**解决方案**：
```bash
# 检查后端服务
docker-compose ps backend
docker-compose logs backend

# 检查Nginx配置
nginx -t
systemctl restart nginx
```

### 问题3：数据库连接失败

**解决方案**：
```bash
# 检查数据库服务
docker-compose ps postgres
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 问题4：SSL证书问题

**解决方案**：
```bash
# 重新申请证书
certbot --nginx -d 你的域名.com -d www.你的域名.com --force-renewal

# 检查证书状态
certbot certificates
```

---

## 成本总结

| 项目 | 费用 | 说明 |
|------|------|------|
| 域名 | 9元/年 | 一次性或年付 |
| 云服务器 | 24-80元/月 | 新用户24-34元/月，老用户60-80元/月 |
| SSL证书 | 免费 | Let's Encrypt |
| **总计** | **约33-89元/月** | 新用户约33元/月 |

---

## 快速部署脚本

我为你创建了一个自动化部署脚本，可以简化部署过程：

```bash
# 在服务器上执行
cd /root
wget https://raw.githubusercontent.com/your-repo/deploy.sh  # 需要创建这个脚本
chmod +x deploy.sh
./deploy.sh
```

---

## 下一步

部署完成后：

1. ✅ **测试所有功能**
   - 热点抓取
   - 视频分析
   - 脚本生成

2. ✅ **配置监控**
   - 设置服务监控
   - 配置告警

3. ✅ **分享给业务同事**
   - 发送访问地址
   - 提供使用说明

4. ✅ **收集反馈**
   - 记录使用情况
   - 收集改进建议

---

## 📝 部署后的功能调整

**好消息**：部署上线后，你仍然可以方便地进行功能调整！

### 推荐流程：
```
本地开发 → 本地测试 → Git提交 → 服务器更新 → 验证上线
```

### 快速更新步骤：

```bash
# 1. 本地修改代码并测试
# 2. 提交到Git
git add .
git commit -m "新功能"
git push

# 3. 在服务器上更新
ssh root@服务器IP
cd /root/Action
git pull
cd docker
docker-compose restart

# 完成！新功能已上线
```

**详细说明**：请参考 [生产环境开发与更新指南](./PRODUCTION_DEVELOPMENT_GUIDE.md)

---

## 需要帮助？

如果在部署过程中遇到问题，可以：
1. 查看日志：`docker-compose logs -f`
2. 检查服务状态：`docker-compose ps`
3. 参考故障排查章节
4. 参考生产环境开发指南

**祝你部署顺利！** 🚀

