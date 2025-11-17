# 生产环境并发用户数评估报告

## 📊 生产环境实际配置

### 服务器配置（ECS）
- **CPU**: 2核
- **内存**: 4GB
- **硬盘**: 40GB SSD
- **带宽**: 3Mbps ✅（已优化）
- **系统**: Ubuntu 22.04
- **地域**: 华北2（北京）

### 部署方式
根据文档，生产环境可能使用以下两种方式之一：

#### 方式1：Docker Compose部署
```yaml
# docker-compose.polardb.yml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8001  # 单进程

celery-worker:
  command: celery -A app.celery_app worker --loglevel=info --pool=solo  # Solo池
```

#### 方式2：Systemd服务部署
```bash
# 使用systemd管理服务
systemctl start action-backend
systemctl start action-celery-worker
```

**注意**：需要查看实际的systemd service文件才能确定启动参数。

---

## 🔍 生产环境各组件并发能力分析

### 1. 前端（Vue.js + Nginx）

**配置**：
- 静态文件通过Nginx提供服务
- Nginx默认配置

**并发能力**：
- ✅ **非常高**：静态文件可以支持数千并发
- Nginx默认 `worker_connections: 1024`
- **评估**：**10,000+ 并发**（静态资源）

**瓶颈**：无（静态文件）

---

### 2. 后端API（FastAPI + Uvicorn）

**生产环境配置**（基于docker-compose.polardb.yml）：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**问题**：
- ❌ **单进程模式**（没有 `--workers` 参数）
- ❌ **没有配置连接数限制**
- ❌ **没有配置超时时间**

**当前并发能力**：
- Uvicorn单进程：**约100-200并发请求**
- 受限于：
  - Python GIL（全局解释器锁）
  - 单进程处理能力
  - 数据库连接池大小（15个连接）

**评估**：**50-100 并发请求**（保守估计）

**服务器资源限制**：
- CPU：2核 → 可以支持2-4个worker进程
- 内存：4GB → 每个worker约300MB，可以支持4-6个worker

---

### 3. 数据库（PolarDB PostgreSQL）

**当前配置**：
```python
# backend/app/core/database.py
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    # ❌ 没有配置 pool_size 和 max_overflow
)
```

**SQLAlchemy默认值**：
- `pool_size=5`
- `max_overflow=10`
- **最大连接数**：**15个连接**

**PolarDB实例限制**：
- 取决于PolarDB实例规格
- 需要查看PolarDB控制台确认最大连接数
- 常见规格：
  - **入门级**（1核2GB）：50-100个连接
  - **标准级**（2核4GB）：100-200个连接
  - **高级**（4核8GB）：200-500个连接

**当前并发能力**：
- 每个数据库连接可以处理一个请求
- **理论最大**：**15个并发数据库操作**
- **实际可用**：**10-12个并发**（考虑连接复用）

**评估**：**10-15 并发用户**（数据库瓶颈）

---

### 4. Redis

**配置**：
- 使用Docker Redis或系统Redis
- 默认配置

**并发能力**：
- ✅ **非常高**：Redis单实例可以支持 **50,000+ 并发连接**
- 主要用于：
  - Celery任务队列
  - 缓存（如果有）

**评估**：**不是瓶颈**（当前使用场景下）

---

### 5. Celery Worker

**生产环境配置**（基于docker-compose.polardb.yml）：
```bash
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**问题**：
- ❌ **使用solo池**（单线程，用于Windows/开发环境）
- ❌ **没有配置并发数**

**当前并发能力**：
- Solo池：**1个任务/时间**
- **评估**：**1个并发任务**

**注意**：Celery任务通常用于后台处理（热点抓取、脚本生成），不影响用户请求的并发数。

---

### 6. 带宽限制

**当前配置**：**3Mbps** ✅（已优化）

**影响**：
- 前端资源加载：每个用户约需要0.1-0.2Mbps
- **理论最大**：**15-30个并发用户**（带宽充足）
- 如果用户操作触发大量数据传输（如视频分析），带宽仍然可能成为瓶颈

**评估**：**15-30 并发用户**（带宽充足，不再是主要瓶颈）

---

### 7. DeepSeek LLM API

**限制因素**：
- API速率限制（需要查看DeepSeek的配额）
- 每个LLM调用耗时：**2-10秒**
- 如果大量用户同时触发LLM调用，会排队等待

**评估**：
- 如果LLM调用是异步的（Celery任务）：**不影响用户请求并发**
- 如果LLM调用是同步的：**受限于API速率限制**

---

## 🎯 生产环境综合评估

### 当前系统瓶颈（按严重程度）

1. **数据库连接池**（最严重）⚠️⚠️⚠️
   - 当前：15个连接
   - 限制：**10-15 并发用户**

2. **Uvicorn单进程**（严重）⚠️⚠️
   - 当前：单进程
   - 限制：**50-100 并发请求**

3. **带宽限制**（中等）⚠️
   - 当前：3Mbps ✅（已优化）
   - 限制：**15-30 并发用户**（不再是主要瓶颈）

4. **Celery Worker**（低）⚠️
   - 当前：solo池
   - 限制：**1个并发任务**（不影响用户请求）

### 当前生产环境最大并发用户数

**保守估计**：**10-15 并发用户**

**原因**：
1. **数据库连接池是主要瓶颈**（15个连接只能支持10-15个并发用户）
2. Uvicorn单进程是次要瓶颈（单进程处理能力有限）
3. 带宽3Mbps已经足够（不再是瓶颈）

---

## 🚀 优化建议（按优先级）

### 优先级1：立即优化（最重要）

#### A. 增加数据库连接池大小 ⚠️⚠️⚠️
```python
# backend/app/core/database.py
engine = create_engine(
    settings.database_url,
    pool_size=20,        # 从5增加到20
    max_overflow=30,     # 从10增加到30
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

**效果**：
- 从15个连接增加到50个连接
- 支持 **30-40并发用户**

**注意**：需要确认PolarDB实例的最大连接数限制

#### B. 使用多进程Uvicorn ⚠️⚠️
```bash
# 修改启动命令
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

**效果**：
- 从单进程增加到2进程（考虑2核CPU）
- 支持 **100-200并发请求**

**注意**：
- 2核CPU建议使用2个worker（每个worker占用1核）
- 如果使用4个worker，可能会因为CPU竞争导致性能下降

#### C. 优化Celery Worker ⚠️
```bash
# 修改启动命令
celery -A app.celery_app worker --loglevel=info --pool=prefork --concurrency=2
```

**效果**：
- 从1个任务增加到2个并发任务
- 加快后台任务处理速度

**注意**：
- 2核CPU建议使用2个并发（每个并发占用1核）
- 如果使用4个并发，可能会因为CPU竞争导致性能下降

#### B. 配置Nginx限流
```nginx
# /etc/nginx/sites-available/action
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://localhost:8001;
    # ... 其他配置
}
```

**效果**：
- 防止单个用户占用过多资源
- 保护后端服务

### 优先级3：长期优化

#### A. 水平扩展
- 使用负载均衡器（如阿里云SLB）
- 部署多个后端实例
- 数据库读写分离

#### B. 缓存策略
- 热点数据缓存（Redis）
- API响应缓存
- 静态资源CDN

#### C. 升级服务器配置
- CPU：2核 → 4核
- 内存：4GB → 8GB
- 带宽：3Mbps → 5Mbps

---

## 📈 优化后的预期并发能力

### 优化方案1：基础优化（立即实施）

**配置**：
- 带宽：3Mbps ✅（已完成）
- 数据库连接池：50个连接
- Uvicorn：2 workers（考虑2核CPU）
- Celery：2并发

**预期**：**20-30 并发用户**

**成本**：无（代码优化）

### 优化方案2：完整优化（中期实施）

**配置**：
- 带宽：3Mbps ✅（已完成）
- 数据库连接池：50个连接
- Uvicorn：2 workers
- Celery：2并发
- Nginx限流：10r/s
- Redis连接池优化

**预期**：**30-40 并发用户**

**成本**：无（代码优化）

### 优化方案3：服务器升级（长期实施）

**配置**：
- 服务器：4核8GB
- 带宽：5Mbps
- 数据库连接池：50个连接
- Uvicorn：4 workers
- Celery：4并发

**预期**：**50-100 并发用户**

**成本**：约增加100-150元/月（服务器升级）

---

## ⚠️ 重要注意事项

### 1. PolarDB实例规格
- 需要确认PolarDB实例的最大连接数限制
- 如果实例规格较低，可能需要升级PolarDB

### 2. DeepSeek API配额
- 需要确认API的速率限制
- 如果配额较低，可能需要：
  - 增加API配额
  - 实现请求队列
  - 使用缓存减少API调用

### 3. 服务器资源监控
- 建议安装监控工具（如Prometheus + Grafana）
- 监控CPU、内存、带宽使用情况
- 根据实际使用情况调整配置

### 4. 数据库性能
- 需要优化慢查询
- 添加必要的索引
- 考虑读写分离（如果用户数较多）

---

## 🎯 总结

| 组件 | 当前配置 | 当前瓶颈 | 优化后 | 优化效果 |
|------|---------|---------|--------|---------|
| 带宽 | 1Mbps | ⚠️⚠️⚠️ 严重 | 3-5Mbps | 3-5倍 |
| 数据库连接池 | 15个连接 | ⚠️⚠️ 严重 | 50个连接 | 3.3倍 |
| Uvicorn | 单进程 | ⚠️ 中等 | 2 workers | 2倍 |
| Celery | Solo池 | ⚠️ 低 | 2并发 | 2倍 |
| Redis | 默认 | ✅ 无 | - | - |
| 前端/Nginx | 默认 | ✅ 无 | - | - |

**当前生产环境最大并发用户数**：**10-15 用户**

**基础优化后最大并发用户数**：**20-30 用户** ✅（满足20-50人部门需求）

**完整优化后最大并发用户数**：**30-40 用户** ✅（满足20-50人部门需求）

**服务器升级后最大并发用户数**：**50-100 用户**（如果未来需要更多）

---

## 💡 推荐实施步骤

### 第一步：立即优化（1-2天）
1. ✅ **带宽3Mbps**（已完成）
2. ✅ 增加数据库连接池大小（代码优化）
3. ✅ 使用多进程Uvicorn（2 workers，代码优化）
4. ✅ 优化Celery Worker（代码优化）

**预期效果**：从10-15并发用户提升到20-30并发用户 ✅（满足20-50人部门需求）

### 第二步：监控和测试（1周）
1. 部署优化后的配置
2. 进行压力测试
3. 监控系统性能
4. 根据实际情况调整参数

### 第三步：进一步优化（2-4周）
1. 如果带宽仍然不够，升级到5Mbps
2. 优化Celery Worker配置
3. 配置Nginx限流
4. 考虑服务器升级（如果用户数持续增长）

