# 项目结构说明

## 目录结构

```
Action/
├── backend/                    # 后端代码
│   ├── app/                    # 应用主目录
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── celery_app.py      # Celery应用配置
│   │   ├── api/               # API路由
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/ # API端点
│   │   │   │   │   ├── hotspots.py    # 热点监控API
│   │   │   │   │   ├── analysis.py   # 视频拆解API
│   │   │   │   │   ├── scripts.py    # 脚本生成API
│   │   │   │   │   ├── products.py   # 商品管理API
│   │   │   │   │   └── live_rooms.py # 直播间管理API
│   │   │   │   └── depends/   # 依赖注入
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── redis_client.py # Redis客户端
│   │   ├── models/            # 数据模型
│   │   │   ├── base.py        # 基础模型
│   │   │   ├── hotspot.py     # 热点模型
│   │   │   ├── product.py     # 商品模型
│   │   │   ├── analysis.py    # 拆解报告模型
│   │   │   └── script.py      # 脚本模型
│   │   ├── services/          # 业务服务
│   │   │   ├── hotspot/       # 热点监控服务
│   │   │   │   └── tasks.py   # Celery任务
│   │   │   ├── analysis/      # 视频拆解服务
│   │   │   │   └── tasks.py
│   │   │   ├── script/        # 脚本生成服务
│   │   │   │   └── tasks.py
│   │   │   ├── data/          # 数据管理服务
│   │   │   │   └── tasks.py
│   │   │   └── analytics/     # 效果追踪服务
│   │   └── utils/             # 工具函数
│   │       ├── helpers.py     # 通用工具
│   │       ├── feishu.py      # 飞书客户端
│   │       ├── deepseek.py    # DeepSeek客户端
│   │       ├── trendradar.py  # TrendRadar客户端
│   │       └── video_analyzer.py # 拆解工具客户端
│   ├── migrations/            # 数据库迁移
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/                 # 测试代码
│   ├── requirements.txt       # Python依赖
│   ├── alembic.ini           # Alembic配置
│   ├── .env.example           # 环境变量示例
│   ├── .gitignore
│   ├── run.py                 # 启动脚本
│   ├── start.sh               # 开发服务器启动脚本
│   ├── start_celery.sh        # Celery Worker启动脚本
│   └── start_beat.sh          # Celery Beat启动脚本
├── frontend/                  # 前端代码（待开发）
├── docker/                    # Docker配置
│   ├── docker-compose.yml     # Docker Compose配置
│   └── Dockerfile.backend     # 后端Dockerfile
├── config/                    # 配置文件
├── docs/                      # 文档
│   └── PROJECT_STRUCTURE.md   # 项目结构说明
├── PRD.md                     # 产品需求文档
├── README.md                  # 项目说明
└── .gitignore                 # Git忽略文件
```

## 核心模块说明

### 1. API层 (app/api/)
- 处理HTTP请求和响应
- 路由定义和参数验证
- 调用服务层处理业务逻辑

### 2. 服务层 (app/services/)
- 业务逻辑实现
- 外部系统集成（TrendRadar、AI拆解工具、DeepSeek）
- Celery异步任务

### 3. 数据模型层 (app/models/)
- SQLAlchemy ORM模型
- 数据库表结构定义

### 4. 工具层 (app/utils/)
- 通用工具函数
- 外部API客户端封装

### 5. 核心配置 (app/core/)
- 应用配置管理
- 数据库连接
- Redis连接

## 开发流程

1. **环境搭建**：使用Docker Compose启动基础服务
2. **配置环境变量**：复制.env.example为.env并配置
3. **数据库迁移**：运行alembic初始化数据库
4. **启动服务**：运行start.sh启动开发服务器
5. **开发功能**：按照PRD文档实现各个模块

## 下一步开发

1. 实现热点监控服务（集成TrendRadar）
2. 实现视频拆解服务（集成AI拆解工具）
3. 实现脚本生成服务（集成DeepSeek）
4. 完善数据模型和数据库迁移
5. 实现前端界面

