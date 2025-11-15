# 热点抓取失败问题解决报告

**问题日期**: 2025-11-13  
**问题状态**: ✅ **已解决**

---

## 🐛 问题描述

### 错误现象
- 前端显示：`热点抓取失败: Worker exited prematurely: signal 6 (SIGABRT) Job: 0.`
- 任务无法完成，Celery Worker 崩溃

### 错误日志
```
objc[63702]: +[NSMutableString initialize] may have been in progress in another thread when fork() was called.
objc[63702]: +[NSMutableString initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
[2025-11-13 18:00:20,524: ERROR/MainProcess] Process 'ForkPoolWorker-8' pid:63702 exited with 'signal 6 (SIGABRT)'
[2025-11-13 18:00:20,541: ERROR/MainProcess] Task handler raised error: WorkerLostError('Worker exited prematurely: signal 6 (SIGABRT) Job: 0.')
```

---

## 🔍 问题分析

### 根本原因

**macOS Fork 问题**：
1. Celery 默认使用 `prefork` pool（多进程模式）
2. `prefork` 使用 `fork()` 系统调用创建子进程
3. macOS 的 Objective-C 运行时在 fork() 时存在已知问题
4. 当 Objective-C 类（如 `NSMutableString`）正在初始化时调用 `fork()`
5. macOS 检测到不安全情况，强制终止进程（SIGABRT）

### 触发条件

- 使用 `httpx` 进行 HTTP 请求
- 在 fork 子进程中执行网络请求
- macOS 系统环境

---

## ✅ 解决方案

### 修复方法：使用 Solo Pool

在 macOS 上使用 `--pool=solo` 而不是默认的 `prefork` pool。

**Solo Pool 特点**：
- ✅ 单进程执行（不使用 fork）
- ✅ 避免 macOS fork 问题
- ✅ 适合开发和测试环境
- ⚠️ 不支持并发执行多个任务（但适合大多数场景）

### 修复内容

#### 1. 更新 Celery 配置 (`backend/app/celery_app.py`)
```python
import platform

# macOS 上使用 solo pool 避免 fork 问题
if platform.system() == "Darwin":  # macOS
    worker_pool = "solo"
else:
    worker_pool = "prefork"  # Linux/其他系统使用 prefork

celery_app.conf.update(
    # ... 其他配置 ...
    worker_pool=worker_pool,
)
```

#### 2. 更新启动脚本
- ✅ `backend/start_celery.sh` - 自动检测 macOS 并使用 solo pool
- ✅ `scripts/start_services.sh` - 服务启动脚本使用 solo pool
- ✅ `scripts/stop_services.sh` - 停止脚本包含 Celery Worker

---

## 📊 修复验证

### 修复前
- ❌ Worker 崩溃：`signal 6 (SIGABRT)`
- ❌ 任务失败：`Worker exited prematurely`
- ❌ 无法完成热点抓取任务

### 修复后
- ✅ Worker 正常运行：`celery@zhangrandeMacBook-Air.local ready.`
- ✅ Pool 模式：`concurrency: 8 (solo)`
- ✅ 任务成功执行：
  ```
  Task app.services.hotspot.tasks.fetch_daily_hotspots[...] succeeded in 27.8s
  {'status': 'success', 'message': '热点抓取任务已完成（使用语义关联度筛选）', 'count': 30}
  ```
- ✅ 无 SIGABRT 错误
- ✅ 热点抓取功能正常

### 测试结果

```bash
# 触发热点抓取
curl -X POST "http://localhost:8001/api/v1/hotspots/fetch?platform=douyin"

# 响应
{
    "message": "热点抓取任务已启动（使用语义关联度筛选）",
    "platform": "douyin",
    "task_id": "a6b5058d-1d6e-4f59-bd96-ac076ac9197d"
}

# 任务执行成功
Task succeeded in 27.8s
成功抓取并保存 30 个热点
```

---

## 📝 技术细节

### macOS Fork 问题

1. **Objective-C 运行时限制**：
   - macOS 的 Objective-C 运行时不是 fork-safe
   - 当运行时正在初始化时调用 fork() 会导致未定义行为
   - macOS 检测到这种情况会强制终止进程

2. **httpx 的影响**：
   - `httpx` 库可能使用底层系统调用
   - 这些调用可能触发 Objective-C 运行时初始化
   - 在 fork 子进程中执行会导致崩溃

3. **为什么 Solo Pool 有效**：
   - Solo pool 不使用 fork()
   - 所有任务在主进程中顺序执行
   - 避免了 fork 相关的所有问题

### 性能影响

**Solo Pool**：
- ✅ 避免 fork 问题
- ✅ 适合开发和测试
- ⚠️ 单进程执行（不支持并发）
- ⚠️ 不适合高并发生产环境

**建议**：
- **开发/测试（macOS）**：使用 `--pool=solo` ✅
- **生产（Linux）**：使用默认 `prefork` pool

---

## ✅ 修复状态

- ✅ 已更新 `backend/app/celery_app.py` - 自动检测 macOS 并使用 solo pool
- ✅ 已更新 `backend/start_celery.sh` - 启动脚本使用 solo pool
- ✅ 已更新 `scripts/start_services.sh` - 服务启动脚本使用 solo pool
- ✅ 已更新 `scripts/stop_services.sh` - 停止脚本包含 Celery Worker
- ✅ 已测试验证 - 任务正常执行，无崩溃
- ✅ 已创建文档 - `docs/CELERY_MACOS_FIX.md`

---

## 🎯 当前服务状态

### ✅ 所有服务正常运行

1. **后端 API 服务**
   - 地址: http://localhost:8001
   - 状态: ✅ 运行中

2. **前端应用服务**
   - 地址: http://localhost:3001
   - 状态: ✅ 运行中

3. **Celery Worker**
   - Pool: `solo` (macOS)
   - 状态: ✅ 运行中
   - 任务执行: ✅ 正常

---

## 📚 相关文档

- [Celery macOS Fix 详细说明](./CELERY_MACOS_FIX.md)
- [Celery 官方文档 - Worker Pools](https://docs.celeryq.dev/en/stable/userguide/workers.html#concurrency)
- [Apple Developer: fork() and exec()](https://developer.apple.com/library/archive/qa/qa2008/qa1628.html)

---

**问题解决时间**: 2025-11-13  
**问题状态**: ✅ **已解决，所有服务正常运行**

