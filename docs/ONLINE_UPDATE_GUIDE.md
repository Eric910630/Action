# 线上服务器更新指南

## 📋 更新前准备

### 1. 确认服务器信息

```bash
# 服务器IP地址（示例，请替换为实际IP）
SERVER_IP="你的服务器IP"

# 或者使用域名
SERVER_DOMAIN="你的域名"
```

### 2. 确认本地代码已推送

```bash
# 在本地项目目录
cd ~/Desktop/Action

# 检查是否有未提交的更改
git status

# 确认代码已推送到远程仓库
git log --oneline -3
```

---

## 🚀 方法一：使用部署脚本（推荐）

### 步骤1：SSH连接到服务器

```bash
# 使用SSH连接到服务器
ssh root@你的服务器IP

# 如果使用密钥认证
ssh -i ~/.ssh/your_key root@你的服务器IP

# 如果使用域名
ssh root@你的域名
```

**常见问题**：
- 如果提示"Permission denied"，检查SSH密钥是否正确
- 如果提示"Host key verification failed"，运行：`ssh-keygen -R 服务器IP`

### 步骤2：进入项目目录

```bash
# 进入项目根目录
cd /root/Action

# 确认当前目录
pwd
# 应该显示：/root/Action

# 查看当前分支和状态
git status
```

### 步骤3：拉取最新代码

```bash
# 拉取最新代码（从远程仓库）
git pull origin main

# 或者如果当前分支已设置跟踪
git pull
```

**如果遇到冲突**：
```bash
# 查看冲突文件
git status

# 如果需要放弃本地更改，使用远程版本
git fetch origin
git reset --hard origin/main

# ⚠️ 注意：这会覆盖本地所有未提交的更改
```

### 步骤4：运行部署脚本

```bash
# 给脚本添加执行权限（如果还没有）
chmod +x scripts/deploy_to_production.sh

# 运行部署脚本
bash scripts/deploy_to_production.sh
```

**部署脚本会自动完成**：
- ✅ 检查数据库迁移
- ✅ 更新Systemd服务配置（如果使用）
- ✅ 安装/更新依赖
- ✅ 重启所有服务
- ✅ 构建并部署前端
- ✅ 验证服务状态

### 步骤5：验证更新

```bash
# 检查服务状态
systemctl status action-backend
systemctl status action-celery-worker

# 或者如果使用Docker
docker-compose -f docker/docker-compose.polardb.yml ps

# 测试后端API
curl http://localhost:8001/health

# 查看服务日志（确认没有错误）
journalctl -u action-backend -n 50
# 或
docker-compose -f docker/docker-compose.polardb.yml logs backend --tail=50
```

---

## 🔧 方法二：手动更新（如果部署脚本不可用）

### 步骤1：SSH连接和进入目录

```bash
# SSH连接
ssh root@你的服务器IP

# 进入项目目录
cd /root/Action
```

### 步骤2：拉取代码

```bash
# 拉取最新代码
git pull origin main
```

### 步骤3：检查是否有数据库迁移

```bash
# 检查是否有新的迁移文件
ls -la backend/migrations/versions/ | tail -5

# 如果有新的迁移，运行迁移
cd backend
source venv/bin/activate
alembic upgrade head
cd /root/Action
```

### 步骤4：更新依赖（如果需要）

```bash
# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd /root/Action

# 更新前端依赖（如果需要）
cd frontend
npm install
cd /root/Action
```

### 步骤5：更新Systemd服务配置（如果使用systemd）

```bash
# 更新服务配置文件
sudo cp docs/systemd/action-backend.service /etc/systemd/system/
sudo cp docs/systemd/action-celery-worker.service /etc/systemd/system/

# 重新加载systemd配置
sudo systemctl daemon-reload
```

### 步骤6：重启服务

**如果使用Systemd**：
```bash
# 重启后端服务
sudo systemctl restart action-backend

# 重启Celery Worker
sudo systemctl restart action-celery-worker
sudo systemctl restart action-celery-beat

# 检查服务状态
sudo systemctl status action-backend
sudo systemctl status action-celery-worker
```

**如果使用Docker Compose**：
```bash
# 进入docker目录
cd docker

# 停止服务
docker-compose -f docker-compose.polardb.yml down

# 重新构建（如果需要）
docker-compose -f docker-compose.polardb.yml build backend frontend

# 启动服务
docker-compose -f docker-compose.polardb.yml up -d

# 查看服务状态
docker-compose -f docker-compose.polardb.yml ps

# 查看日志
docker-compose -f docker-compose.polardb.yml logs -f backend
```

**如果使用Docker但只更新代码**：
```bash
# 进入docker目录
cd docker

# 重启服务（不重新构建）
docker-compose -f docker-compose.polardb.yml restart backend celery-worker celery-beat

# 查看日志确认启动成功
docker-compose -f docker-compose.polardb.yml logs backend --tail=50
```

### 步骤7：更新前端（如果修改了前端代码）

```bash
# 进入前端目录
cd /root/Action/frontend

# 安装依赖（如果package.json有变化）
npm install

# 构建前端
npm run build

# 复制到Nginx目录
sudo cp -r dist/* /var/www/action-script/

# 设置权限
sudo chown -R www-data:www-data /var/www/action-script
sudo chmod -R 755 /var/www/action-script

# 重启Nginx（通常不需要，但如果有问题可以重启）
sudo systemctl restart nginx
```

### 步骤8：验证更新

```bash
# 1. 检查后端服务
curl http://localhost:8001/health
# 应该返回：{"status": "healthy"} 或类似

# 2. 检查前端（在浏览器中访问）
# http://你的域名 或 http://服务器IP

# 3. 测试PDF导出功能
# 在浏览器中进入脚本管理页面，点击"导出PDF"按钮

# 4. 查看服务日志（确认没有错误）
journalctl -u action-backend -n 100 --no-pager
# 或
docker-compose -f docker/docker-compose.polardb.yml logs backend --tail=100
```

---

## 🔍 详细验证步骤

### 1. 检查代码版本

```bash
# 在服务器上
cd /root/Action
git log --oneline -1
# 应该看到最新的commit，包含"fix: 修复PDF导出功能"

# 检查修改的文件
git show --name-only HEAD
# 应该看到：
# - backend/app/api/v1/endpoints/scripts.py
# - frontend/src/api/client.ts
# - frontend/src/views/ScriptsView.vue
```

### 2. 检查服务是否正常运行

```bash
# 检查后端进程
ps aux | grep uvicorn
# 应该看到uvicorn进程，如果使用2 workers，应该看到多个进程

# 检查Celery Worker
ps aux | grep celery
# 应该看到celery worker进程

# 检查端口监听
netstat -tlnp | grep 8001
# 应该看到8001端口被监听
```

### 3. 测试API端点

```bash
# 测试健康检查
curl http://localhost:8001/health

# 测试脚本列表API
curl http://localhost:8001/api/v1/scripts?limit=1

# 测试PDF导出API（需要替换script_id）
curl -O http://localhost:8001/api/v1/scripts/你的script_id/export-pdf
```

### 4. 检查日志

```bash
# 查看后端日志（最近50行）
journalctl -u action-backend -n 50 --no-pager

# 实时查看日志
journalctl -u action-backend -f

# 查看错误日志
journalctl -u action-backend -p err -n 50 --no-pager
```

---

## ⚠️ 常见问题和解决方案

### 问题1：git pull失败 - "Permission denied"

**原因**：SSH密钥未配置或权限不足

**解决方案**：
```bash
# 检查SSH密钥
ls -la ~/.ssh/

# 如果使用HTTPS，可能需要输入用户名密码
git pull https://github.com/Eric910630/Action.git main
```

### 问题2：git pull失败 - "Your local changes would be overwritten"

**原因**：本地有未提交的更改

**解决方案**：
```bash
# 查看本地更改
git status

# 方案1：保存本地更改（推荐）
git stash
git pull
git stash pop

# 方案2：放弃本地更改（⚠️ 会丢失本地修改）
git reset --hard origin/main
git pull
```

### 问题3：服务启动失败

**原因**：可能是依赖问题或配置问题

**解决方案**：
```bash
# 查看详细错误日志
journalctl -u action-backend -n 100 --no-pager

# 检查依赖是否安装
cd /root/Action/backend
source venv/bin/activate
pip list | grep reportlab
# 应该看到reportlab>=4.0.0

# 如果reportlab未安装
pip install reportlab>=4.0.0
```

### 问题4：PDF导出仍然失败

**原因**：可能是前端缓存或服务未重启

**解决方案**：
```bash
# 1. 确认代码已更新
cd /root/Action
git log --oneline -1 | grep "PDF"

# 2. 重启后端服务
sudo systemctl restart action-backend
# 或
docker-compose -f docker/docker-compose.polardb.yml restart backend

# 3. 清除浏览器缓存
# 在浏览器中按 Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)

# 4. 检查后端日志
journalctl -u action-backend -f
# 然后在前端点击导出PDF，查看是否有错误
```

### 问题5：前端构建失败

**原因**：可能是npm依赖问题

**解决方案**：
```bash
cd /root/Action/frontend

# 清除node_modules和缓存
rm -rf node_modules package-lock.json
npm cache clean --force

# 重新安装依赖
npm install

# 重新构建
npm run build
```

---

## 📝 快速更新命令（一键执行）

如果服务器已经配置好，可以使用以下命令快速更新：

```bash
# 复制以下命令到服务器执行
cd /root/Action && \
git pull origin main && \
cd backend && \
source venv/bin/activate && \
pip install -q -r requirements.txt && \
alembic upgrade head && \
cd /root/Action && \
sudo systemctl restart action-backend action-celery-worker action-celery-beat && \
cd frontend && \
npm install --silent && \
npm run build && \
sudo cp -r dist/* /var/www/action-script/ && \
sudo chown -R www-data:www-data /var/www/action-script && \
echo "✅ 更新完成！" && \
systemctl status action-backend --no-pager -l | head -10
```

---

## 🔄 回滚方法（如果更新后出现问题）

### 回滚到上一个版本

```bash
# 查看提交历史
cd /root/Action
git log --oneline -10

# 回滚到上一个commit（替换COMMIT_HASH为上一个commit的hash）
git reset --hard 上一个commit的hash

# 重启服务
sudo systemctl restart action-backend action-celery-worker
```

### 回滚到远程仓库的版本

```bash
cd /root/Action
git fetch origin
git reset --hard origin/main
sudo systemctl restart action-backend action-celery-worker
```

---

## 📞 获取帮助

如果遇到问题，可以：

1. **查看日志**：
   ```bash
   journalctl -u action-backend -n 100
   ```

2. **检查服务状态**：
   ```bash
   systemctl status action-backend
   ```

3. **查看Git状态**：
   ```bash
   cd /root/Action
   git status
   git log --oneline -5
   ```

---

## ✅ 更新检查清单

更新完成后，请确认：

- [ ] 代码已成功拉取（`git log`显示最新commit）
- [ ] 后端服务正常运行（`systemctl status action-backend`）
- [ ] Celery Worker正常运行（`systemctl status action-celery-worker`）
- [ ] 后端API响应正常（`curl http://localhost:8001/health`）
- [ ] 前端页面可以正常访问
- [ ] PDF导出功能可以正常使用
- [ ] 没有错误日志（`journalctl -u action-backend -p err`）

---

**最后更新**：2024年（PDF导出功能修复）

