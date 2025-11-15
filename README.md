# VTICS - 短视频热点智能创作系统

基于TrendRadar的短视频热点到脚本生成全链路AI应用

## 项目简介

VTICS（Video Trend Intelligence Creation System）是一个全链路AI应用系统，实现从热点发现到拍摄脚本生成的自动化流程。

### 核心功能

- 🔥 **热点监控**：自动监控抖音等平台热点，筛选与商品相关的内容
- 🎬 **视频拆解**：自动拆解爆款视频，提取可复制的成功要素
- ✍️ **脚本生成**：基于热点+商品+爆款技巧，自动生成拍摄脚本和分镜
- 📊 **效果追踪**：追踪视频和直播间数据，生成效果分析报告

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- Celery + Redis
- MySQL 8.0

### 前端
- Vue 3 + TypeScript
- Element Plus
- Pinia
- Axios

### AI/ML
- DeepSeek API
- LangChain

### 部署
- Docker + Docker Compose

## 快速开始

### 前置要求

- Python 3.10+
- Docker & Docker Compose
- MySQL 8.0（或使用Docker）
- Redis 7.0（或使用Docker）

### 环境搭建

#### 1. 克隆项目

```bash
cd ~/Desktop/Action
```

#### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入相关配置
```

#### 3. 使用Docker启动服务

```bash
cd ../docker
docker-compose up -d
```

这将启动以下服务：
- MySQL（端口3306）
- Redis（端口6379）
- 后端API（端口8000）
- Celery Worker
- Celery Beat

#### 4. 初始化数据库

```bash
cd ../backend
# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head
```

#### 5. 启动开发服务器

```bash
# 启动后端API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery Worker（新终端）
celery -A app.celery_app worker --loglevel=info

# 启动Celery Beat（新终端）
celery -A app.celery_app beat --loglevel=info
```

#### 6. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## 项目结构

```
Action/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务服务
│   │   └── utils/       # 工具函数
│   ├── migrations/      # 数据库迁移
│   ├── tests/           # 测试代码
│   └── requirements.txt # Python依赖
├── frontend/            # 前端代码（待开发）
├── docker/              # Docker配置
│   ├── docker-compose.yml
│   └── Dockerfile.backend
├── config/              # 配置文件
├── docs/                 # 文档
└── PRD.md               # 产品需求文档
```

## API端点

### 热点监控
- `GET /api/v1/hotspots` - 获取热点列表
- `POST /api/v1/hotspots/fetch` - 手动触发热点抓取
- `GET /api/v1/hotspots/{id}` - 获取热点详情
- `POST /api/v1/hotspots/filter` - 关键词筛选热点

### 视频拆解
- `POST /api/v1/analysis/analyze` - 分析视频
- `GET /api/v1/analysis/reports` - 获取拆解报告列表
- `GET /api/v1/analysis/reports/{id}` - 获取拆解报告详情
- `POST /api/v1/analysis/batch` - 批量分析

### 脚本生成
- `POST /api/v1/scripts/generate` - 生成脚本
- `GET /api/v1/scripts` - 获取脚本列表
- `GET /api/v1/scripts/{id}` - 获取脚本详情
- `PUT /api/v1/scripts/{id}` - 更新脚本
- `POST /api/v1/scripts/{id}/review` - 审核脚本
- `POST /api/v1/scripts/{id}/optimize` - 获取优化建议

### 商品管理
- `GET /api/v1/products` - 获取商品列表
- `POST /api/v1/products` - 创建商品
- `GET /api/v1/products/{id}` - 获取商品详情
- `PUT /api/v1/products/{id}` - 更新商品

### 直播间管理
- `GET /api/v1/live-rooms` - 获取直播间列表
- `POST /api/v1/live-rooms` - 创建直播间
- `GET /api/v1/live-rooms/{id}` - 获取直播间详情

## 开发计划

详见 [PRD.md](./PRD.md)

## 许可证

GPL-3.0

