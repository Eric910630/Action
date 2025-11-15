# 问题排查指南

## 关于307状态码

**307是正常的，不是错误！**

307是HTTP临时重定向状态码。FastAPI会自动将：
- `/api/v1/hotspots` → `/api/v1/hotspots/`（添加尾部斜杠）

这是FastAPI的标准行为，用于保持URL一致性。浏览器会自动跟随重定向，最终请求会成功（返回200）。

### 为什么会有307？

FastAPI的路由定义使用了 `/hotspots`（没有尾部斜杠），但实际访问时可能会：
- 前端请求：`/api/v1/hotspots?limit=20`
- FastAPI重定向到：`/api/v1/hotspots/?limit=20`（添加斜杠）
- 最终返回：200 OK

这是**正常且预期的行为**，不需要担心。

---

## 热点抓取任务相关问题

### 问题1：任务已启动但看不到进度

**原因**：
- 热点抓取是异步任务（通过Celery执行）
- 前端只是触发了任务，不会立即看到结果
- 任务在后台执行，完成后数据会保存到数据库

**解决方案**：
1. 等待几秒钟（任务通常很快完成）
2. 点击"查询"按钮刷新热点列表
3. 查看Celery日志：`tail -f logs/celery.log`

### 问题2：抓取后没有数据

**可能原因**：
1. **TrendRadar API未配置或连接失败**
   - 检查 `backend/.env` 中的 `TRENDRADAR_API_URL` 和 `TRENDRADAR_API_KEY`
   - 如果没有配置，系统会使用Mock数据（测试数据）

2. **没有匹配的热点**
   - 语义筛选可能过滤掉了所有热点
   - 检查是否有主推商品配置

3. **任务执行失败**
   - 查看Celery日志：`tail -f logs/celery.log`
   - 查看后端日志：`tail -f logs/backend.log`

**解决方案**：
- 如果没有真实API，系统会自动使用Mock数据
- 确保已创建直播间和商品
- 检查日志中的错误信息

---

## 查看任务状态

### 方式1：查看Celery日志

```bash
tail -f logs/celery.log
```

你会看到类似这样的日志：
```
[INFO] Task app.services.hotspot.tasks.fetch_daily_hotspots[...] received
[INFO] 开始抓取每日热点，平台: douyin
[INFO] 成功获取 X 个热点
[INFO] Task succeeded
```

### 方式2：使用任务状态API（已添加）

```bash
# 查询任务状态
curl http://localhost:8001/api/v1/tasks/{task_id}
```

任务ID在点击"抓取热点"后会在响应中返回。

---

## 常见错误及解决方案

### 错误1：CORS错误

**症状**：浏览器控制台显示 "Access-Control-Allow-Origin" 错误

**解决**：
- ✅ 已修复：CORS配置已包含 `localhost:3001`
- 如果仍有问题，检查 `backend/app/core/config.py` 中的 `CORS_ORIGINS`

### 错误2：网络错误

**症状**：前端显示 "Network Error"

**解决**：
1. 检查后端是否运行：`curl http://localhost:8001/health`
2. 检查前端代理配置：`frontend/vite.config.ts`
3. 检查CORS配置

### 错误3：数据库连接失败

**症状**：创建数据时提示数据库错误

**解决**：
1. 检查数据库配置：`backend/.env`
2. 运行数据库迁移：`cd backend && alembic upgrade head`
3. 检查数据库服务是否运行

### 错误4：TrendRadar API连接失败

**症状**：日志显示 "All connection attempts failed"

**解决**：
- 如果没有真实API，这是正常的
- 系统会自动使用Mock数据（测试数据）
- 确保 `backend/.env` 中配置了正确的API地址（如果有）

---

## 测试数据

如果没有真实API，系统会自动使用Mock数据，包括：

1. **Mock热点数据**：
   - 时尚穿搭推荐
   - 美妆教程
   - 童装推荐
   - 家具推荐
   - 家电测评

2. **Mock数据特点**：
   - 包含完整的热点信息
   - 包含热度、标签等字段
   - 可以用于测试语义筛选和可视化功能

---

## 验证步骤

### 1. 验证后端服务
```bash
curl http://localhost:8001/health
# 应该返回: {"status":"healthy","service":"VTICS API"}
```

### 2. 验证前端服务
```bash
curl http://localhost:3001
# 应该返回HTML页面
```

### 3. 验证Celery Worker
```bash
ps aux | grep celery | grep -v grep
# 应该看到celery进程
```

### 4. 验证任务执行
```bash
tail -f logs/celery.log
# 点击"抓取热点"后应该看到任务日志
```

---

## 获取帮助

如果问题仍然存在：

1. **查看日志**：
   - 后端：`tail -f logs/backend.log`
   - 前端：`tail -f logs/frontend.log`
   - Celery：`tail -f logs/celery.log`

2. **检查配置**：
   - `backend/.env` - 环境变量配置
   - `frontend/vite.config.ts` - 前端代理配置

3. **检查服务状态**：
   ```bash
   ps aux | grep -E "(uvicorn|vite|celery)" | grep -v grep
   ```

---

**最后更新**: 2024年12月

