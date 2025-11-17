# 服务器 Git 仓库设置

## 🔍 问题诊断

如果你在服务器上执行 `git` 命令时遇到 `fatal: not a git repository`，说明：

1. **不在项目目录中**：需要先 `cd /root/Action`
2. **项目目录不是 Git 仓库**：需要初始化或克隆

---

## ✅ 解决方案

### 方案1：如果项目目录已存在，但未初始化 Git

```bash
# 进入项目目录
cd /root/Action

# 初始化 Git 仓库
git init

# 添加远程仓库（如果有）
git remote add origin <你的Git仓库地址>

# 拉取代码
git pull origin main
# 或
git pull origin master
```

### 方案2：如果项目目录不存在，需要克隆

```bash
# 删除旧目录（如果存在）
rm -rf /root/Action

# 克隆仓库
cd /root
git clone <你的Git仓库地址> Action

# 进入项目目录
cd /root/Action
```

### 方案3：如果项目目录存在，但没有 Git 仓库

**选项A：保留现有代码，初始化 Git**

```bash
cd /root/Action
git init
git add .
git commit -m "Initial commit"
git remote add origin <你的Git仓库地址>
git push -u origin main
```

**选项B：从远程仓库重新克隆（会覆盖现有代码）**

```bash
# 备份现有代码
mv /root/Action /root/Action.backup

# 克隆仓库
cd /root
git clone <你的Git仓库地址> Action

# 如果需要恢复某些文件，从备份中复制
```

---

## 🎯 推荐流程

### 如果你已经有 Git 仓库（GitHub/GitLab等）

```bash
# 1. 进入项目目录
cd /root/Action

# 2. 检查是否已有 Git 仓库
ls -la | grep .git

# 3. 如果没有 .git 目录，初始化
git init
git remote add origin <你的Git仓库地址>

# 4. 拉取代码
git pull origin main --allow-unrelated-histories
# 或
git pull origin master --allow-unrelated-histories
```

### 如果你还没有 Git 仓库

**步骤1：在本地创建 Git 仓库并推送到远程**

```bash
# 在本地（你的Mac）
cd ~/Desktop/Action

# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 在 GitHub/GitLab 创建新仓库，然后：
git remote add origin <你的Git仓库地址>
git push -u origin main
```

**步骤2：在服务器上克隆**

```bash
# 在服务器上
cd /root
rm -rf Action  # 如果已存在，先删除
git clone <你的Git仓库地址> Action
cd /root/Action
```

---

## 📝 当前情况处理

根据你的情况，最可能的是：

1. **项目目录存在，但没有 Git 仓库**
2. **或者你在错误的目录下**

**快速检查**：

```bash
# 检查当前目录
pwd

# 检查项目目录是否存在
ls -la /root/Action

# 检查项目目录是否是 Git 仓库
cd /root/Action
ls -la | grep .git
```

**如果项目目录存在但没有 Git**：

```bash
cd /root/Action
git init
git add .
git commit -m "Initial commit from server"

# 然后添加远程仓库（如果你有）
git remote add origin <你的Git仓库地址>
git branch -M main
git push -u origin main
```

---

## 🔄 后续更新流程

一旦 Git 仓库设置好，后续更新流程就是：

```bash
# 在服务器上
cd /root/Action
git pull

# 如果修改了后端
sudo systemctl restart action-backend

# 如果修改了前端
cd frontend
npm run build
sudo cp -r dist/* /var/www/action-script/
sudo chown -R www-data:www-data /var/www/action-script
```

---

## ❓ 需要帮助？

请告诉我：

1. **你是否有 Git 仓库**（GitHub/GitLab等）？
2. **项目目录 `/root/Action` 是否存在**？
3. **项目目录中是否有 `.git` 文件夹**？

根据你的回答，我会给出具体的操作步骤。

