# 生产环境开发与更新指南

## 📋 概述

部署上线后，你仍然可以方便地进行功能调整和更新。本文档说明如何在生产环境中进行开发和部署更新。

---

## 🎯 开发流程

### 推荐流程

```
本地开发 → 测试验证 → 提交代码 → 服务器更新 → 验证上线
```

---

## 方式一：本地开发 + 服务器更新（推荐）⭐

### 优点
- ✅ 不影响生产环境
- ✅ 可以充分测试
- ✅ 更新可控

### 工作流程

#### 1. 本地开发

在你的本地电脑上开发新功能：

```bash
# 本地已经有运行的服务（之前启动的）
# 在本地进行开发和测试
cd ~/Desktop/Action

# 修改代码
# 测试功能
# ...

# 提交到Git（如果有Git仓库）
git add .
git commit -m "添加新功能"
git push
```

#### 2. 服务器更新

开发完成后，更新服务器：

**方式A：使用Git（推荐）**

```bash
# 在服务器上执行
ssh root@你的服务器IP
cd /root/Action

# 拉取最新代码
git pull

# 如果有数据库迁移
cd docker
docker-compose exec backend alembic upgrade head

# 重启服务（应用新代码）
docker-compose restart backend frontend

# 查看日志确认
docker-compose logs -f backend
```

**方式B：使用SCP上传**

```bash
# 在本地执行
cd ~/Desktop
tar -czf Action-update.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  Action

# 上传到服务器
scp Action-update.tar.gz root@你的服务器IP:/root/

# 在服务器上
ssh root@你的服务器IP
cd /root
tar -xzf Action-update.tar.gz
cd Action/docker
docker-compose restart
```

---

## 方式二：直接在服务器上开发（不推荐）

### 适用场景
- 小改动
- 紧急修复

### 注意事项
- ⚠️ 可能影响生产环境
- ⚠️ 没有版本控制
- ⚠️ 容易出错

### 操作步骤

```bash
# 连接服务器
ssh root@你的服务器IP
cd /root/Action

# 直接编辑文件
nano backend/app/api/v1/endpoints/hotspots.py

# 重启服务
cd docker
docker-compose restart backend
```

---

## 方式三：使用Git分支管理（最佳实践）⭐

### 工作流程

```
main分支（生产环境）
  ↓
feature分支（开发新功能）
  ↓
测试通过后合并到main
  ↓
服务器拉取main分支更新
```

### 具体操作

#### 1. 创建功能分支

```bash
# 在本地
cd ~/Desktop/Action
git checkout -b feature/new-function

# 开发新功能
# ...

# 提交
git add .
git commit -m "添加新功能"
git push origin feature/new-function
```

#### 2. 测试通过后合并

```bash
# 合并到main分支
git checkout main
git merge feature/new-function
git push origin main
```

#### 3. 服务器更新

```bash
# 在服务器上
cd /root/Action
git pull origin main
cd docker
docker-compose restart
```

---

## 🔄 常见更新场景

### 场景1：修改前端界面

**步骤**：

```bash
# 1. 本地修改前端代码
cd ~/Desktop/Action/frontend
# 修改 Vue 组件、样式等

# 2. 本地测试
npm run dev
# 在浏览器测试

# 3. 构建生产版本
npm run build

# 4. 上传到服务器
# 方式A：使用Git
git add .
git commit -m "更新前端界面"
git push

# 在服务器上
cd /root/Action
git pull
cd docker
docker-compose restart frontend

# 方式B：直接上传构建后的文件
scp -r frontend/dist root@服务器IP:/root/Action/frontend/
# 在服务器上重启前端容器
```

### 场景2：修改后端API

**步骤**：

```bash
# 1. 本地修改后端代码
cd ~/Desktop/Action/backend
# 修改 API 端点、业务逻辑等

# 2. 本地测试
# 确保API文档可以访问：http://localhost:8001/docs
# 测试API功能

# 3. 提交代码
git add .
git commit -m "更新API功能"
git push

# 4. 服务器更新
ssh root@服务器IP
cd /root/Action
git pull
cd docker
docker-compose restart backend

# 5. 查看日志
docker-compose logs -f backend
```

### 场景3：修改数据库结构

**步骤**：

```bash
# 1. 本地创建数据库迁移
cd ~/Desktop/Action/backend
source venv/bin/activate

# 创建迁移文件
alembic revision --autogenerate -m "添加新字段"

# 检查迁移文件
# 编辑 migrations/versions/xxx_xxx.py

# 2. 本地测试迁移
alembic upgrade head

# 3. 提交迁移文件
git add migrations/
git commit -m "数据库迁移：添加新字段"
git push

# 4. 服务器执行迁移
ssh root@服务器IP
cd /root/Action
git pull
cd docker

# 执行迁移
docker-compose exec backend alembic upgrade head

# 重启服务
docker-compose restart backend
```

### 场景4：添加新的依赖包

**步骤**：

```bash
# 1. 本地添加依赖
cd ~/Desktop/Action/backend
source venv/bin/activate
pip install 新包名

# 2. 更新requirements.txt
pip freeze > requirements.txt
# 或手动添加到requirements.txt

# 3. 提交
git add requirements.txt
git commit -m "添加新依赖包"
git push

# 4. 服务器更新
ssh root@服务器IP
cd /root/Action
git pull
cd docker

# 重新构建镜像（包含新依赖）
docker-compose build backend
docker-compose up -d backend
```

---

## 🛠️ 开发环境配置

### 推荐配置：本地开发 + 生产部署

**本地环境**：
- 用于开发和测试
- 可以随时重启，不影响用户
- 使用热重载，修改代码自动生效

**生产环境**：
- 用于正式服务
- 稳定运行，不频繁重启
- 更新前充分测试

### 本地开发服务器

你已经启动了本地开发服务器：
- 后端：http://localhost:8001
- 前端：http://localhost:3001

**开发流程**：
1. 在本地修改代码
2. 本地测试（自动热重载）
3. 测试通过后，更新生产环境

---

## 📝 更新检查清单

每次更新前，检查以下事项：

### 代码检查
- [ ] 代码已测试通过
- [ ] 没有语法错误
- [ ] 没有引入新的bug

### 数据库检查
- [ ] 如果有数据库变更，已创建迁移文件
- [ ] 迁移文件已测试
- [ ] 备份了生产数据库

### 配置检查
- [ ] 环境变量配置正确
- [ ] API Key等敏感信息已配置
- [ ] 配置文件已更新

### 依赖检查
- [ ] 如果有新依赖，已更新requirements.txt
- [ ] 依赖版本兼容

### 测试检查
- [ ] 功能测试通过
- [ ] 性能测试通过
- [ ] 兼容性测试通过

---

## 🚨 更新注意事项

### 1. 备份数据

更新前备份数据库：

```bash
# 在服务器上
cd /root/Action/docker
docker-compose exec postgres pg_dump -U vtics vtics > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 选择更新时间

- ✅ 选择用户使用较少的时间段
- ✅ 提前通知用户（如果有）
- ✅ 准备回滚方案

### 3. 逐步更新

- ✅ 先更新测试环境（如果有）
- ✅ 小范围测试
- ✅ 确认无误后全量更新

### 4. 监控日志

更新后监控日志：

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 查看错误日志
docker-compose logs | grep -i error
```

### 5. 回滚方案

如果更新出现问题，快速回滚：

```bash
# 方式1：Git回滚
cd /root/Action
git log  # 查看提交历史
git checkout <之前的commit-hash>
cd docker
docker-compose restart

# 方式2：恢复备份
docker-compose exec -T postgres psql -U vtics vtics < backup_20250114.sql
```

---

## 🔧 开发工具推荐

### 代码编辑器
- **VS Code**：推荐，支持远程开发
- **Cursor**：你正在使用的，AI辅助开发

### 远程开发
- **VS Code Remote SSH**：可以直接在服务器上编辑代码
- **Git**：版本控制，方便代码管理

### 部署工具
- **Docker Compose**：容器管理
- **Git**：代码同步

---

## 📊 开发效率提升

### 1. 使用热重载

**本地开发**已经配置了热重载：
- 后端：`--reload` 参数，修改代码自动重启
- 前端：Vite自动热重载，修改代码立即生效

### 2. 使用Git工作流

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 开发完成后
git add .
git commit -m "新功能"
git push

# 合并到main
git checkout main
git merge feature/new-feature
git push
```

### 3. 使用Docker Compose

```bash
# 快速重启服务
docker-compose restart backend

# 查看日志
docker-compose logs -f backend

# 进入容器调试
docker-compose exec backend bash
```

---

## 🎯 最佳实践总结

### ✅ 推荐做法

1. **本地开发，服务器部署**
   - 在本地充分测试
   - 测试通过后再更新生产环境

2. **使用Git管理代码**
   - 版本控制
   - 方便回滚
   - 代码同步

3. **使用分支管理**
   - main分支：生产环境
   - feature分支：开发新功能
   - 测试通过后合并

4. **更新前备份**
   - 备份数据库
   - 记录当前版本

5. **逐步更新**
   - 小改动可以快速更新
   - 大改动要充分测试

### ❌ 不推荐做法

1. **直接在服务器上开发**
   - 容易影响生产环境
   - 没有版本控制

2. **频繁重启服务**
   - 影响用户体验
   - 选择合适的时间更新

3. **不测试就更新**
   - 容易引入bug
   - 影响系统稳定性

---

## 📞 常见问题

### Q1: 更新后服务无法启动怎么办？

**A**: 
```bash
# 查看错误日志
docker-compose logs backend

# 检查代码是否有语法错误
docker-compose exec backend python -m py_compile app/main.py

# 回滚到之前的版本
git checkout <之前的commit>
docker-compose restart
```

### Q2: 如何在不影响用户的情况下更新？

**A**: 
- 选择用户使用较少的时间段
- 使用蓝绿部署（如果有条件）
- 先更新测试环境验证

### Q3: 更新需要多长时间？

**A**: 
- 小改动：1-2分钟（重启服务）
- 大改动：5-10分钟（重新构建镜像）
- 数据库迁移：取决于数据量

### Q4: 可以同时开发多个功能吗？

**A**: 
- 可以，使用不同的分支
- 开发完成后分别测试
- 按优先级依次合并和部署

---

## 🎉 总结

**部署上线后，你仍然可以方便地进行功能调整：**

1. ✅ **本地开发**：在本地修改和测试
2. ✅ **Git同步**：使用Git管理代码版本
3. ✅ **快速更新**：几分钟内完成更新
4. ✅ **可控回滚**：出现问题可以快速回滚

**推荐工作流程**：
```
本地开发 → 本地测试 → Git提交 → 服务器拉取 → 重启服务 → 验证
```

**这样既不影响生产环境，又能快速迭代功能！** 🚀

