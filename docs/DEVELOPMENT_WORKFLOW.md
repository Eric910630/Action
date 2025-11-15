# 开发流程指南

## 📋 开发流程概述

**推荐流程**：**本地开发 → 测试验证 → Git提交 → 云服务器部署 → 功能迭代**

### 为什么这样安排？

1. **本地开发**：快速迭代，无需Docker（避免M1 MacBook Air卡顿）
2. **云服务器部署**：使用Docker Compose，环境一致，易于管理
3. **功能迭代**：本地开发 → Git提交 → 服务器更新，持续改进

## 🖥️ 本地开发环境（不使用Docker）

### 前置要求

- ✅ Python 3.10+（本地安装）
- ✅ Node.js 16+（本地安装）
- ✅ PostgreSQL（可选：使用PolarDB或本地PostgreSQL）
- ✅ Redis（可选：使用云Redis或本地Redis）

### 本地开发配置

#### 1. 数据库选择

**方案1：使用PolarDB（推荐）**
- 无需本地安装PostgreSQL
- 直接连接云端PolarDB
- 配置简单

**方案2：本地PostgreSQL**
- 需要本地安装PostgreSQL
- 适合完全离线开发

**方案3：轻量Docker（仅数据库）**
```bash
# 只启动PostgreSQL和Redis（轻量，不会卡）
docker run -d --name postgres -p 5432:5432 postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7.0-alpine
```

#### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
# 数据库（使用PolarDB或本地PostgreSQL）
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

# Redis（使用云Redis或本地Redis）
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# DeepSeek API
DEEPSEEK_API_KEY=your-api-key

# Open-WebSearch（可选，如果本地启动）
OPEN_WEBSEARCH_MCP_URL=http://localhost:3000/mcp
```

#### 3. 启动本地开发服务

**方式1：使用启动脚本（推荐）**

```bash
# 启动所有服务（后端+前端）
./start_dev.sh

# 停止所有服务
./stop_dev.sh
```

**方式2：手动启动**

```bash
# 终端1：启动后端
cd backend
source venv/bin/activate  # 或 python3 -m venv venv && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 终端2：启动Celery Worker
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info --pool=solo

# 终端3：启动前端
cd frontend
npm run dev
```

#### 4. 访问服务

- **前端页面**：http://localhost:3001
- **后端API文档**：http://localhost:8001/docs
- **后端API**：http://localhost:8001

### 本地开发优势

✅ **快速启动**：无需等待Docker构建  
✅ **热重载**：代码修改自动生效  
✅ **性能好**：M1 MacBook Air不会卡顿  
✅ **调试方便**：直接使用IDE调试  
✅ **资源占用少**：只运行必要的服务  

## ☁️ 云服务器部署（使用Docker）

### 部署时机

**建议**：在核心功能开发完成后，再进行首次部署

### 部署流程

1. **购买云服务器**（2核4GB，Ubuntu 22.04）
2. **购买PolarDB**（如果还没有）
3. **配置域名**（如果还没有）
4. **上传代码到服务器**
5. **使用Docker Compose部署**

详细步骤请参考：
- [云端部署完整指南](./CLOUD_DEPLOYMENT_GUIDE.md)
- [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md)

### Docker部署优势

✅ **环境一致**：开发、测试、生产环境一致  
✅ **易于管理**：一键启动/停止所有服务  
✅ **隔离性好**：服务之间互不干扰  
✅ **扩展性强**：易于添加新服务（如Open-WebSearch）  

## 🔄 功能迭代流程

### 日常开发流程

```
1. 本地开发
   ↓
2. 本地测试
   ↓
3. Git提交
   git add .
   git commit -m "新功能"
   git push
   ↓
4. 服务器更新
   ssh root@服务器IP
   cd /root/Action
   git pull
   cd docker
   docker-compose restart
   ↓
5. 验证上线
   访问域名，测试新功能
```

### 快速更新命令

```bash
# 在服务器上执行
cd /root/Action
git pull
cd docker
docker-compose restart backend celery-worker celery-beat frontend
```

## 📊 开发环境对比

| 环境 | 用途 | Docker | 优势 | 劣势 |
|------|------|--------|------|------|
| **本地开发** | 日常开发、调试 | ❌ 不使用 | 快速、轻量、调试方便 | 需要配置数据库 |
| **云服务器** | 生产部署、测试 | ✅ 使用Docker | 环境一致、易于管理 | 需要服务器资源 |

## 🎯 推荐配置

### 开发阶段

- ✅ **本地开发**：使用PolarDB + 本地Redis（或云Redis）
- ✅ **不使用Docker**：避免M1 MacBook Air卡顿
- ✅ **快速迭代**：代码修改立即生效

### 部署阶段

- ✅ **云服务器**：使用Docker Compose部署
- ✅ **PolarDB**：使用云端数据库
- ✅ **域名访问**：配置域名和SSL证书

### 迭代阶段

- ✅ **本地开发** → **Git提交** → **服务器更新**
- ✅ **持续改进**：快速响应业务需求

## ⚠️ 注意事项

### 1. 数据库连接

- **本地开发**：连接PolarDB或本地PostgreSQL
- **服务器部署**：连接PolarDB（推荐）或Docker PostgreSQL

### 2. Redis连接

- **本地开发**：连接本地Redis或云Redis
- **服务器部署**：使用Docker Redis

### 3. Open-WebSearch

- **本地开发**：
  - **方案1（推荐）**：不启动Open-WebSearch，使用备用搜索方案（duckduckgo-search）
    - 安装：`pip install duckduckgo-search`
    - 代码会自动降级到备用方案
    - 无需Docker，无需额外服务
  - **方案2**：连接到云服务器上的Open-WebSearch服务（如果已部署）
  - **方案3**：使用NPX快速启动（轻量，不占用太多资源）
- **服务器部署**：使用Docker Compose自动启动

**详细说明**：请参考 [本地开发Web搜索配置指南](./LOCAL_DEVELOPMENT_WEBSEARCH.md)

### 4. 环境变量

- **本地开发**：使用 `backend/.env` 文件
- **服务器部署**：使用 `backend/.env` 文件（通过Docker挂载）

## 📝 总结

**最佳实践**：

1. ✅ **本地开发**：不使用Docker，直接运行Python和Node.js
2. ✅ **云服务器部署**：使用Docker Compose，环境一致
3. ✅ **功能迭代**：本地开发 → Git提交 → 服务器更新

这样既能保证开发效率（本地快速迭代），又能保证部署质量（Docker环境一致）。

## 🔗 相关文档

- [云端部署完整指南](./CLOUD_DEPLOYMENT_GUIDE.md)
- [PolarDB部署指南](./POLARDB_DEPLOYMENT_GUIDE.md)
- [生产环境开发与更新指南](./PRODUCTION_DEVELOPMENT_GUIDE.md)
- [快速启动指南](./QUICK_START.md)

