# 快速开始指南

## 🚀 一键启动（推荐）

### 方式1：使用启动脚本

```bash
# 启动所有服务
./start_dev.sh

# 停止所有服务
./stop_dev.sh
```

### 方式2：手动启动

#### 1. 启动后端
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 启动前端（新终端）
```bash
cd frontend
npm run dev
```

#### 3. 启动Celery Worker（可选，新终端）
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

---

## 📍 访问地址

启动成功后，访问：

- **前端页面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **后端ReDoc**: http://localhost:8000/redoc

---

## ✅ 快速验证

### 1. 检查后端是否启动
```bash
curl http://localhost:8000/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "VTICS API"
}
```

### 2. 检查前端是否启动
打开浏览器访问：http://localhost:3000

应该看到VTICS的登录页面或主界面。

### 3. 检查API文档
访问：http://localhost:8000/docs

应该看到Swagger API文档界面。

---

## 🧪 快速测试流程

### 步骤1：创建直播间
1. 访问 http://localhost:3000
2. 点击"直播间管理"
3. 创建测试直播间

### 步骤2：创建商品
1. 点击"商品管理"
2. 创建测试商品（关联到刚才的直播间）

### 步骤3：测试热点监控
1. 点击"热点监控"
2. 点击"抓取热点"
3. 查看气泡图可视化

### 步骤4：测试视频拆解
1. 点击"视频拆解"
2. 输入视频URL
3. 查看拆解报告

### 步骤5：测试脚本生成
1. 点击"脚本生成"
2. 选择热点、商品、拆解报告
3. 生成脚本

---

## ⚙️ 环境配置

### 必需配置

创建 `backend/.env` 文件：

```env
# 数据库（必需）
DATABASE_URL=postgresql://user:password@localhost:5432/vtics

# Redis（必需）
REDIS_URL=redis://localhost:6379/0
```

### 可选配置（用于真实API）

```env
# DeepSeek API（用于语义关联度和情感分析）
DEEPSEEK_API_KEY=your_key_here

# TrendRadar API（用于真实热点数据）
TRENDRADAR_API_URL=https://api.trendradar.com
TRENDRADAR_API_KEY=your_key_here
```

**注意**：如果没有配置真实API，系统会使用Mock数据或fallback机制。

---

## 🐛 常见问题

### 问题1：端口被占用

**后端端口8000被占用**：
```bash
# 查找占用进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

**前端端口3000被占用**：
```bash
# 修改 frontend/vite.config.ts 中的端口
server: {
  port: 3001,  # 改为其他端口
}
```

### 问题2：数据库连接失败

检查：
1. PostgreSQL是否运行
2. 数据库连接字符串是否正确
3. 数据库是否存在

```bash
# 创建数据库
createdb vtics

# 运行迁移
cd backend
alembic upgrade head
```

### 问题3：前端无法连接后端

检查：
1. 后端是否启动
2. 前端代理配置（`frontend/vite.config.ts`）
3. CORS配置（`backend/app/main.py`）

---

## 📚 更多信息

- **详细测试指南**: [docs/MANUAL_TESTING_GUIDE.md](docs/MANUAL_TESTING_GUIDE.md)
- **API文档**: http://localhost:8000/docs
- **功能实现总结**: [docs/FEATURE_IMPLEMENTATION_SUMMARY.md](docs/FEATURE_IMPLEMENTATION_SUMMARY.md)

---

**祝测试顺利！** 🎉

