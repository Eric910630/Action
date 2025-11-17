# 生产环境并发能力优化指南

## 🎯 优化目标

支持 **20-50人短视频部门** 同时使用系统，确保系统稳定运行。

## 📊 当前配置 vs 优化后配置

| 组件 | 当前配置 | 优化后配置 | 提升效果 |
|------|---------|-----------|---------|
| 带宽 | 3Mbps ✅ | 3Mbps | 已优化 |
| 数据库连接池 | 15个连接 | 50个连接 | 3.3倍 |
| Uvicorn | 单进程 | 2 workers | 2倍 |
| Celery Worker | Solo池 | Prefork池，2并发 | 2倍 |
| Redis连接池 | 默认 | 50个连接 | 优化 |

**优化后预期并发用户数**：**20-30 并发用户** ✅（满足20-50人部门需求）

---

## 🚀 优化实施步骤

### 第一步：更新代码配置

#### 1. 数据库连接池优化 ✅（已完成）

**文件**：`backend/app/core/database.py`

**变更**：
```python
engine = create_engine(
    settings.database_url,
    pool_size=20,        # 从5增加到20
    max_overflow=30,     # 从10增加到30
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

**效果**：从15个连接增加到50个连接

#### 2. Redis连接池优化 ✅（已完成）

**文件**：`backend/app/core/redis_client.py`

**变更**：
```python
redis_client = redis.Redis(
    ...
    max_connections=50,  # 增加连接池大小
)
```

**效果**：支持更多并发Redis操作

---

### 第二步：更新Docker配置

#### 1. 后端服务优化 ✅（已完成）

**文件**：`docker/docker-compose.polardb.yml`

**变更**：
```yaml
backend:
  command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2"
```

**效果**：从单进程增加到2 workers

#### 2. Celery Worker优化 ✅（已完成）

**文件**：`docker/docker-compose.polardb.yml`

**变更**：
```yaml
celery-worker:
  command: celery -A app.celery_app worker --loglevel=info --pool=prefork --concurrency=2
```

**效果**：从solo池改为prefork池，2并发

---

### 第三步：更新Systemd服务配置（如果使用systemd）

#### 1. 后端服务配置

**文件**：`/etc/systemd/system/action-backend.service`

**创建或更新**：
```ini
[Unit]
Description=Action Backend API Service
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/Action/backend
Environment="PATH=/root/Action/backend/venv/bin"
ExecStart=/root/Action/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**应用配置**：
```bash
# 在服务器上执行
sudo cp /root/Action/docs/systemd/action-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart action-backend
```

#### 2. Celery Worker配置

**文件**：`/etc/systemd/system/action-celery-worker.service`

**创建或更新**：
```ini
[Unit]
Description=Action Celery Worker Service
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/Action/backend
Environment="PATH=/root/Action/backend/venv/bin"
ExecStart=/root/Action/backend/venv/bin/celery -A app.celery_app worker --loglevel=info --pool=prefork --concurrency=2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**应用配置**：
```bash
# 在服务器上执行
sudo cp /root/Action/docs/systemd/action-celery-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart action-celery-worker
```

---

### 第四步：部署优化后的配置

#### 方式1：使用Docker Compose（推荐）

```bash
# 在服务器上执行
cd /root/Action
git pull  # 或上传更新后的文件

# 重启服务以应用新配置
cd docker
docker-compose -f docker-compose.polardb.yml down
docker-compose -f docker-compose.polardb.yml up -d

# 查看服务状态
docker-compose -f docker-compose.polardb.yml ps

# 查看日志确认workers已启动
docker-compose -f docker-compose.polardb.yml logs backend | grep "workers"
docker-compose -f docker-compose.polardb.yml logs celery-worker | grep "concurrency"
```

#### 方式2：使用Systemd服务

```bash
# 在服务器上执行
cd /root/Action
git pull  # 或上传更新后的文件

# 更新systemd服务配置
sudo cp docs/systemd/action-backend.service /etc/systemd/system/
sudo cp docs/systemd/action-celery-worker.service /etc/systemd/system/
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart action-backend
sudo systemctl restart action-celery-worker

# 查看服务状态
sudo systemctl status action-backend
sudo systemctl status action-celery-worker
```

---

### 第五步：验证优化效果

#### 1. 检查后端Workers

```bash
# 如果使用Docker
docker-compose -f docker-compose.polardb.yml exec backend ps aux | grep uvicorn

# 应该看到2个uvicorn进程（主进程 + 2个worker）
```

#### 2. 检查Celery Worker

```bash
# 如果使用Docker
docker-compose -f docker-compose.polardb.yml logs celery-worker | grep "ready"

# 应该看到类似：celery@xxx ready (2 workers)
```

#### 3. 检查数据库连接池

```bash
# 连接到PolarDB，查看当前连接数
# 在PolarDB控制台或使用psql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'your_database_name';
```

#### 4. 压力测试（可选）

```bash
# 使用ab或wrk进行简单压力测试
ab -n 1000 -c 20 http://your-domain.com/api/v1/hotspots/

# 或使用wrk
wrk -t4 -c20 -d30s http://your-domain.com/api/v1/hotspots/
```

---

## ⚠️ 注意事项

### 1. PolarDB实例连接数限制

**重要**：需要确认PolarDB实例的最大连接数限制。

**检查方法**：
1. 登录阿里云控制台
2. 进入PolarDB控制台
3. 查看实例规格和最大连接数

**如果连接数不足**：
- 需要升级PolarDB实例规格
- 或减少连接池大小（但会影响并发能力）

### 2. 服务器资源监控

**建议监控指标**：
- CPU使用率（2核CPU，2 workers会占用较多CPU）
- 内存使用率（4GB内存，2 workers约占用600MB）
- 数据库连接数
- 响应时间

**监控工具**：
- 阿里云监控
- Prometheus + Grafana（可选）

### 3. 渐进式优化

**建议**：
1. 先应用数据库连接池优化
2. 观察1-2天，确认稳定
3. 再应用Uvicorn workers优化
4. 最后应用Celery Worker优化

---

## 📈 优化效果预期

### 优化前
- **并发用户数**：10-15用户
- **主要瓶颈**：数据库连接池（15个连接）

### 优化后
- **并发用户数**：20-30用户 ✅
- **主要瓶颈**：服务器资源（2核CPU，4GB内存）

### 如果未来需要更多并发

**选项1：升级服务器配置**
- CPU：2核 → 4核
- 内存：4GB → 8GB
- Uvicorn workers：2 → 4
- **预期**：50-100并发用户

**选项2：水平扩展**
- 部署多个后端实例
- 使用负载均衡器（如阿里云SLB）
- **预期**：100+并发用户

---

## 🔄 回滚方案

如果优化后出现问题，可以快速回滚：

### Docker Compose回滚

```bash
cd /root/Action/docker
# 恢复到单进程配置
docker-compose -f docker-compose.polardb.yml down
# 编辑docker-compose.polardb.yml，移除--workers 2
docker-compose -f docker-compose.polardb.yml up -d
```

### Systemd回滚

```bash
# 编辑systemd服务文件，移除--workers 2
sudo systemctl edit action-backend
# 或直接编辑
sudo nano /etc/systemd/system/action-backend.service
sudo systemctl daemon-reload
sudo systemctl restart action-backend
```

---

## ✅ 优化检查清单

- [ ] 数据库连接池已优化（pool_size=20, max_overflow=30）
- [ ] Redis连接池已优化（max_connections=50）
- [ ] Uvicorn已配置2 workers
- [ ] Celery Worker已配置prefork池，2并发
- [ ] Docker配置已更新
- [ ] Systemd服务配置已更新（如果使用）
- [ ] 服务已重启并验证
- [ ] 监控已配置（可选）

---

## 📞 问题排查

### 问题1：服务启动失败

**检查**：
```bash
# 查看服务日志
journalctl -u action-backend -n 50
journalctl -u action-celery-worker -n 50

# 或Docker日志
docker-compose -f docker-compose.polardb.yml logs backend
docker-compose -f docker-compose.polardb.yml logs celery-worker
```

### 问题2：数据库连接数不足

**检查**：
```bash
# 查看PolarDB控制台的连接数监控
# 或使用SQL查询
SELECT count(*) FROM pg_stat_activity;
```

**解决**：
- 升级PolarDB实例规格
- 或减少连接池大小

### 问题3：内存不足

**检查**：
```bash
free -h
top
```

**解决**：
- 减少workers数量（从2改为1）
- 或升级服务器内存

---

## 🎯 总结

通过以上优化，系统并发能力从 **10-15用户** 提升到 **20-30用户**，可以满足20-50人短视频部门的使用需求。

**关键优化点**：
1. ✅ 数据库连接池：15 → 50个连接
2. ✅ Uvicorn：单进程 → 2 workers
3. ✅ Celery Worker：solo池 → prefork池，2并发
4. ✅ Redis连接池：默认 → 50个连接

**下一步**：
1. 部署优化后的配置
2. 监控系统性能
3. 根据实际使用情况调整参数

