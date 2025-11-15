# 服务运行状态

## 🚀 当前运行的服务

### 端口配置
- **后端API**: http://localhost:8001 ✅
- **前端页面**: http://localhost:3001 ✅
- **API文档**: http://localhost:8001/docs
- **Celery Worker**: 运行中 ✅

### 服务状态

#### 后端服务 (uvicorn)
- **端口**: 8001
- **状态**: ✅ 运行中
- **日志**: `logs/backend.log`
- **健康检查**: http://localhost:8001/health
- **PID**: 检查 `ps aux | grep uvicorn`

#### 前端服务 (vite)
- **端口**: 3001
- **状态**: ✅ 运行中
- **日志**: `logs/frontend.log`
- **访问地址**: http://localhost:3001

#### Celery Worker
- **状态**: ✅ 运行中
- **日志**: `logs/celery.log`
- **任务**: 
  - `fetch_daily_hotspots` - 热点抓取
  - `analyze_video_async` - 视频拆解

---

## 📝 访问地址

### 前端页面
```
http://localhost:3001
```

### API文档
```
http://localhost:8001/docs
```

### ReDoc
```
http://localhost:8001/redoc
```

### 健康检查
```
http://localhost:8001/health
```

---

## 🔍 查看日志

```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log

# Celery日志
tail -f logs/celery.log
```

---

## 🛑 停止服务

```bash
# 停止所有服务
pkill -f "uvicorn app.main:app"
pkill -f "vite"
pkill -f "celery"

# 或使用脚本
./stop_dev.sh
```

---

## ⚠️ 注意事项

1. **端口已更改**：
   - 后端从 8000 → 8001
   - 前端从 3000 → 3001
   - 前端代理已自动更新到 8001

2. **数据库配置**：
   - 确保 `backend/.env` 中配置了正确的数据库连接
   - 如果首次运行，需要执行：`cd backend && alembic upgrade head`

3. **前端语法错误已修复**：
   - 修复了 `ScriptsView.vue` 中的导入语句错误

---

## ✅ 快速验证

```bash
# 检查后端
curl http://localhost:8001/health

# 检查前端
curl http://localhost:3001

# 检查进程
ps aux | grep -E "(uvicorn|vite|celery)" | grep -v grep
```

---

**最后更新**: 2024年12月
