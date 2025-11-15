# Celery macOS Fork 问题修复

**问题日期**: 2025-11-13  
**问题状态**: ✅ 已修复

---

## 🐛 问题描述

### 错误信息
```
objc[63702]: +[NSMutableString initialize] may have been in progress in another thread when fork() was called.
objc[63702]: +[NSMutableString initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
[2025-11-13 18:00:20,524: ERROR/MainProcess] Process 'ForkPoolWorker-8' pid:63702 exited with 'signal 6 (SIGABRT)'
[2025-11-13 18:00:20,541: ERROR/MainProcess] Task handler raised error: WorkerLostError('Worker exited prematurely: signal 6 (SIGABRT) Job: 0.')
```

### 问题原因

在 macOS 上，Celery 默认使用 `prefork` pool（多进程模式），这会使用 `fork()` 系统调用来创建子进程。然而，macOS 的 Objective-C 运行时在 fork() 时存在已知问题：

1. **Objective-C 运行时初始化冲突**：
   - 当某些 Objective-C 类（如 `NSMutableString`）正在初始化时调用 `fork()`
   - macOS 会检测到这种不安全的情况并强制终止进程（SIGABRT）

2. **httpx 库的影响**：
   - 使用 `httpx` 进行 HTTP 请求时，可能会触发 Objective-C 运行时的初始化
   - 在 fork 子进程中执行这些操作会导致崩溃

---

## ✅ 解决方案

### 方案：使用 Solo Pool

在 macOS 上使用 `--pool=solo` 而不是默认的 `prefork` pool。

**Solo Pool 特点**：
- ✅ 单进程执行任务（不使用 fork）
- ✅ 避免 macOS fork 问题
- ✅ 适合开发和测试环境
- ⚠️ 不支持并发执行多个任务（但适合大多数场景）

### 实现方式

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

#### 2. 更新启动脚本 (`backend/start_celery.sh`)

```bash
# macOS 上使用 --pool=solo 避免 fork 问题
if [[ "$OSTYPE" == "darwin"* ]]; then
    celery -A app.celery_app worker --loglevel=info --pool=solo
else
    celery -A app.celery_app worker --loglevel=info
fi
```

#### 3. 更新服务启动脚本 (`scripts/start_services.sh`)

```bash
# macOS 上使用 --pool=solo 避免 fork 问题
if [[ "$OSTYPE" == "darwin"* ]]; then
    CELERY_POOL="--pool=solo"
else
    CELERY_POOL=""
fi

celery -A app.celery_app worker --loglevel=info $CELERY_POOL
```

---

## 📊 修复验证

### 修复前
- ❌ Worker 崩溃：`signal 6 (SIGABRT)`
- ❌ 任务失败：`Worker exited prematurely`
- ❌ 无法完成热点抓取任务

### 修复后
- ✅ Worker 正常运行：`celery@zhangrandeMacBook-Air.local ready.`
- ✅ Pool 模式：`concurrency: 8 (solo)`
- ✅ 任务成功执行：热点抓取任务正常完成
- ✅ 无 SIGABRT 错误

### 测试结果

```bash
# 启动 Celery Worker（使用 solo pool）
celery -A app.celery_app worker --loglevel=info --pool=solo

# 触发热点抓取任务
curl -X POST "http://localhost:8001/api/v1/hotspots/fetch?platform=douyin"

# 结果：任务成功执行，无错误
```

---

## 🔍 技术细节

### macOS Fork 问题背景

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

**Prefork Pool**（Linux）：
- ✅ 支持多进程并发
- ✅ 适合生产环境
- ❌ macOS 上会崩溃

**建议**：
- **开发/测试（macOS）**：使用 `--pool=solo`
- **生产（Linux）**：使用默认 `prefork` pool

---

## 📝 相关文档

### Celery 官方文档
- [Worker Pools](https://docs.celeryq.dev/en/stable/userguide/workers.html#concurrency)
- [Solo Pool](https://docs.celeryq.dev/en/stable/userguide/workers.html#solo-pool)

### macOS Fork 问题
- [Apple Developer: fork() and exec()](https://developer.apple.com/library/archive/qa/qa2008/qa1628.html)
- [Python multiprocessing on macOS](https://bugs.python.org/issue33725)

---

## ✅ 修复状态

- ✅ 已更新 `backend/app/celery_app.py` - 自动检测 macOS 并使用 solo pool
- ✅ 已更新 `backend/start_celery.sh` - 启动脚本使用 solo pool
- ✅ 已更新 `scripts/start_services.sh` - 服务启动脚本使用 solo pool
- ✅ 已测试验证 - 任务正常执行，无崩溃

---

**修复完成时间**: 2025-11-13  
**问题状态**: ✅ 已解决

