# 快速启动指南

## 前置要求

- Python 3.10+
- Docker & Docker Compose（推荐）
- 或本地安装 MySQL 8.0 和 Redis 7.0

## 方式一：使用Docker（推荐）

### 1. 启动基础服务

```bash
cd ~/Desktop/Action/docker
docker-compose up -d mysql redis
```

### 2. 配置环境变量

```bash
cd ../backend
cp .env.example .env
# 编辑 .env 文件，填入配置
```

### 3. 安装Python依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 启动FastAPI服务
python run.py
# 或
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 新终端：启动Celery Worker
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info

# 新终端：启动Celery Beat
source venv/bin/activate
celery -A app.celery_app beat --loglevel=info
```

### 6. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## 方式二：使用Docker Compose（完整部署）

### 1. 配置环境变量

```bash
cd ~/Desktop/Action/backend
cp .env.example .env
# 编辑 .env 文件
```

### 2. 启动所有服务

```bash
cd ../docker
docker-compose up -d
```

这将启动：
- MySQL（端口3306）
- Redis（端口6379）
- 后端API（端口8000）
- Celery Worker
- Celery Beat

### 3. 初始化数据库

```bash
cd ../backend
# 进入容器或本地执行
alembic upgrade head
```

### 4. 查看服务状态

```bash
docker-compose ps
```

### 5. 查看日志

```bash
docker-compose logs -f backend
```

## 环境变量配置说明

编辑 `backend/.env` 文件，配置以下关键参数：

```env
# DeepSeek API（必须）
DEEPSEEK_API_KEY=your-deepseek-api-key

# TrendRadar（必须）
TRENDRADAR_API_URL=http://localhost:3333

# AI拆解工具（必须）
VIDEO_ANALYZER_API_URL=http://your-analyzer-api-url
VIDEO_ANALYZER_API_KEY=your-api-key

# 飞书（必须）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url

# 数据库（Docker方式会自动配置）
DATABASE_URL=mysql+pymysql://vtics:vticspassword@mysql:3306/vtics

# Redis（Docker方式会自动配置）
REDIS_HOST=redis
REDIS_PORT=6379
```

## 验证安装

### 1. 检查API服务

```bash
curl http://localhost:8000/health
```

应该返回：
```json
{"status": "healthy", "service": "VTICS API"}
```

### 2. 检查API文档

访问 http://localhost:8000/docs 查看Swagger文档

### 3. 检查数据库连接

```bash
# 进入MySQL容器
docker exec -it vtics-mysql mysql -u vtics -pvticspassword vtics

# 查看表
SHOW TABLES;
```

## 常见问题

### 1. 端口被占用

修改 `docker-compose.yml` 中的端口映射，或停止占用端口的服务

### 2. 数据库连接失败

检查：
- MySQL服务是否启动
- 数据库用户名密码是否正确
- 网络连接是否正常

### 3. Redis连接失败

检查：
- Redis服务是否启动
- Redis配置是否正确

### 4. 依赖安装失败

尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 下一步

1. 配置TrendRadar集成
2. 配置AI拆解工具集成
3. 配置DeepSeek API
4. 开始开发具体功能模块

详见 [PRD.md](../PRD.md)

