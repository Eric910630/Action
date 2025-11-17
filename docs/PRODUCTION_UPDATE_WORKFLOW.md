# 生产环境更新流程

## 📋 更新流程概览

```
本地开发 → 本地测试 → Git提交 → 服务器更新 → 验证上线
```

**预计耗时**：2-5分钟（取决于修改内容）

---

## 🔄 完整更新步骤

### 第一步：本地开发和测试

```bash
# 1. 在本地进行代码修改
# 2. 本地测试功能是否正常
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 新终端：启动前端
cd frontend
npm run dev
```

**测试要点**：
- ✅ 功能是否正常
- ✅ 是否有报错
- ✅ UI是否正常显示

---

### 第二步：Git提交

```bash
# 在项目根目录
cd ~/Desktop/Action

# 查看修改的文件
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述你的修改内容，例如：更新品牌名称为Action"

# 推送到远程仓库
git push
```

**提交信息建议**：
- `fix: 修复直播间加载问题`
- `feat: 添加新功能XXX`
- `refactor: 重构XXX模块`
- `style: 更新UI样式`
- `docs: 更新文档`

---

### 第三步：服务器更新代码

```bash
# SSH连接到服务器
ssh root@39.102.60.67

# 进入项目目录
cd /root/Action

# 拉取最新代码
git pull
```

---

### 第四步：更新服务（根据修改内容选择）

#### 4.1 如果只修改了后端代码

```bash
# 重启后端服务
sudo systemctl restart action-backend

# 如果修改了数据库模型，需要运行迁移
cd /root/Action/backend
source venv/bin/activate
alembic upgrade head

# 重启Celery Worker（如果修改了任务相关代码）
sudo systemctl restart action-celery-worker
sudo systemctl restart action-celery-beat
```

#### 4.2 如果只修改了前端代码

```bash
# 重新构建前端
cd /root/Action/frontend
npm install  # 如果package.json有变化
npm run build  # 或 npx vite build（跳过类型检查）

# 复制构建文件到Nginx目录
sudo cp -r dist/* /var/www/action-script/

# 设置权限
sudo chown -R www-data:www-data /var/www/action-script
sudo chmod -R 755 /var/www/action-script

# 重启Nginx（可选，通常不需要）
sudo systemctl restart nginx
```

#### 4.3 如果同时修改了前后端

```bash
# 先更新后端
sudo systemctl restart action-backend

# 再更新前端
cd /root/Action/frontend
npm run build
sudo cp -r dist/* /var/www/action-script/
sudo chown -R www-data:www-data /var/www/action-script
```

---

### 第五步：验证更新

```bash
# 1. 检查后端服务状态
sudo systemctl status action-backend
sudo systemctl status action-celery-worker

# 2. 检查后端API
curl http://localhost:8001/health

# 3. 检查前端（在浏览器中）
# 访问 http://39.102.60.67 或 http://actionscript.fun
# 检查功能是否正常
```

---

## 🚀 快速更新脚本

为了简化流程，可以创建更新脚本：

### 创建服务器端更新脚本

```bash
# 在服务器上创建
nano /root/Action/scripts/update.sh
```

**脚本内容**：

```bash
#!/bin/bash
# 生产环境快速更新脚本

set -e

echo "🔄 开始更新..."

# 进入项目目录
cd /root/Action

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull

# 检查是否有前端修改
if git diff HEAD@{1} --name-only | grep -q "frontend/"; then
    echo "🎨 检测到前端修改，重新构建前端..."
    cd frontend
    npm run build
    sudo cp -r dist/* /var/www/action-script/
    sudo chown -R www-data:www-data /var/www/action-script
    echo "✅ 前端更新完成"
fi

# 检查是否有后端修改
if git diff HEAD@{1} --name-only | grep -q "backend/"; then
    echo "⚙️ 检测到后端修改，重启后端服务..."
    sudo systemctl restart action-backend
    sudo systemctl restart action-celery-worker
    sudo systemctl restart action-celery-beat
    echo "✅ 后端更新完成"
fi

# 检查是否有数据库迁移
if git diff HEAD@{1} --name-only | grep -q "migrations/"; then
    echo "🗄️ 检测到数据库迁移，运行迁移..."
    cd /root/Action/backend
    source venv/bin/activate
    alembic upgrade head
    echo "✅ 数据库迁移完成"
fi

echo "🎉 更新完成！"
```

**设置执行权限**：

```bash
chmod +x /root/Action/scripts/update.sh
```

**使用方法**：

```bash
# 在服务器上执行
/root/Action/scripts/update.sh
```

---

## 📝 常见更新场景

### 场景1：修改了API接口

```bash
# 1. 本地测试
# 2. Git提交
git add .
git commit -m "feat: 添加新API接口"
git push

# 3. 服务器更新
ssh root@39.102.60.67
cd /root/Action
git pull
sudo systemctl restart action-backend
```

### 场景2：修改了前端UI

```bash
# 1. 本地测试
# 2. Git提交
git add .
git commit -m "style: 更新UI样式"
git push

# 3. 服务器更新
ssh root@39.102.60.67
cd /root/Action
git pull
cd frontend
npm run build
sudo cp -r dist/* /var/www/action-script/
sudo chown -R www-data:www-data /var/www/action-script
```

### 场景3：修改了数据库模型

```bash
# 1. 本地创建迁移
cd backend
alembic revision --autogenerate -m "添加新字段"
alembic upgrade head

# 2. 本地测试
# 3. Git提交
git add .
git commit -m "feat: 添加新数据库字段"
git push

# 4. 服务器更新
ssh root@39.102.60.67
cd /root/Action
git pull
cd backend
source venv/bin/activate
alembic upgrade head
sudo systemctl restart action-backend
```

---

## ⚠️ 注意事项

### 1. 数据库迁移

- **重要**：数据库迁移是不可逆的，确保在本地测试通过后再部署
- 生产环境迁移前，建议先备份数据库

### 2. 前端构建

- 如果 `package.json` 有变化，需要先运行 `npm install`
- 如果TypeScript类型检查报错，可以使用 `npx vite build` 跳过类型检查

### 3. 服务重启

- 重启后端服务时，正在处理的任务可能会中断
- 建议在低峰期进行更新

### 4. 回滚

如果更新后出现问题，可以快速回滚：

```bash
# 回滚到上一个版本
cd /root/Action
git log  # 查看提交历史
git reset --hard <上一个版本的commit hash>
# 然后重新构建/重启服务
```

---

## 🎯 最佳实践

1. **小步快跑**：频繁提交小改动，而不是一次性提交大量修改
2. **测试先行**：本地测试通过后再提交
3. **提交信息清晰**：使用清晰的commit message，方便追踪
4. **备份重要数据**：更新前备份数据库（特别是数据库迁移）
5. **低峰期更新**：选择用户较少的时间段进行更新

---

## 📞 遇到问题？

如果更新后出现问题：

1. **检查服务状态**：
   ```bash
   sudo systemctl status action-backend
   sudo systemctl status action-celery-worker
   sudo systemctl status nginx
   ```

2. **查看日志**：
   ```bash
   sudo journalctl -u action-backend -n 50
   sudo journalctl -u action-celery-worker -n 50
   ```

3. **回滚代码**：使用 `git reset --hard` 回滚到上一个版本

