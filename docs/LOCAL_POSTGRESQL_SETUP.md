# 本地PostgreSQL数据库设置指南

## 方案概述

对于本地开发，你可以选择：
1. **本地安装PostgreSQL**（推荐，功能完整）
2. **继续使用PolarDB**（如果VPN配置正确）

## 方案1：本地安装PostgreSQL（推荐）

### macOS安装PostgreSQL

#### 使用Homebrew安装

```bash
# 安装PostgreSQL
brew install postgresql@15

# 启动PostgreSQL服务
brew services start postgresql@15

# 或者手动启动（不自动启动）
pg_ctl -D /usr/local/var/postgresql@15 start
```

#### 创建数据库和用户

```bash
# 进入PostgreSQL命令行
psql postgres

# 在PostgreSQL中执行以下命令：
CREATE DATABASE action_script_db;
CREATE USER action_scripter WITH PASSWORD 'local_dev_password';
GRANT ALL PRIVILEGES ON DATABASE action_script_db TO action_scripter;
\q
```

### 配置本地开发环境

更新 `backend/.env` 文件：

```env
# 本地开发数据库配置
DB_USER=action_scripter
DB_PASSWORD=local_dev_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=action_script_db
DATABASE_ECHO=False

# 其他配置保持不变...
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
DEEPSEEK_API_KEY=sk-5b2030b163d140539c22f91aa3c08310
```

### 初始化数据库

```bash
cd backend
source venv/bin/activate

# 运行数据库迁移
alembic upgrade head

# 初始化种子数据（创建初始直播间）
python3 -m app.services.data.seed
```

## 方案2：继续使用PolarDB

如果你能配置好VPN和IP白名单，可以继续使用PolarDB。

### 检查VPN连接

```bash
# 检查你的公网IP（通过VPN后的IP）
curl ifconfig.me

# 然后在阿里云PolarDB控制台，将这个IP添加到白名单
```

### 使用PolarDB公网地址

如果PolarDB有公网地址，使用公网地址而不是内网地址：

```env
# 使用PolarDB公网地址（如果有）
DB_HOST=polardb-opensite.pg.polardb.rds.aliyuncs.com  # 公网地址示例
DB_USER=action_scripter
DB_PASSWORD=Test0099
DB_PORT=5432
DB_NAME=action_script_db
```

## 推荐工作流程

### 本地开发阶段
- ✅ 使用本地PostgreSQL
- ✅ 快速迭代，无需网络依赖
- ✅ 可以随意测试，不影响生产数据

### 部署到生产
- ✅ 使用PolarDB（生产环境）
- ✅ 代码通过Git推送到服务器
- ✅ 服务器连接PolarDB

## 快速切换配置

你可以创建两个`.env`文件：
- `backend/.env.local` - 本地开发配置（本地PostgreSQL）
- `backend/.env.production` - 生产环境配置（PolarDB）

然后根据需要使用：
```bash
# 本地开发
cp .env.local .env

# 生产部署
cp .env.production .env
```

