# 逐步部署指南

## 📋 部署步骤清单

我们将按照以下步骤逐步进行部署。每完成一步，告诉我，我们继续下一步。

## 第一步：确认资源准备 ✅

请确认以下资源已准备好：

### 1.1 云服务器
- [ ] 已购买
- [ ] IP地址：________________
- [ ] SSH访问方式：□ 密码  □ 密钥

### 1.2 PolarDB
- [ ] 已购买
- [ ] 主机地址：________________
- [ ] 端口：5432
- [ ] 数据库名：________________
- [ ] 用户名：________________
- [ ] 密码：________________

### 1.3 域名（可选，可以先使用IP）
- [ ] 已购买
- [ ] 域名：________________

### 1.4 DeepSeek API Key
- [ ] 已获取
- [ ] API Key：________________

---

## 第二步：准备代码上传

### 2.1 Git仓库（推荐）

**如果已有Git仓库**：
- [ ] 仓库地址：________________
- [ ] 代码已提交到仓库

**如果没有Git仓库**：
- [ ] 需要创建Git仓库（GitHub/GitLab等）
- [ ] 或使用SCP直接上传

### 2.2 代码检查

- [ ] 本地代码已测试
- [ ] 所有功能正常

---

## 第三步：服务器准备

### 3.1 连接服务器

```bash
ssh root@你的服务器IP
```

**请告诉我**：
- [ ] 能否成功连接服务器？
- [ ] 如果连接失败，错误信息是什么？

### 3.2 检查服务器环境

连接成功后，在服务器上执行：

```bash
# 检查系统版本
cat /etc/os-release

# 检查Docker（如果已安装）
docker --version

# 检查Docker Compose（如果已安装）
docker-compose --version

# 检查Git（如果已安装）
git --version
```

**请告诉我**：
- [ ] 系统版本是什么？
- [ ] Docker是否已安装？
- [ ] Docker Compose是否已安装？
- [ ] Git是否已安装？

---

## 第四步：安装必要软件

### 4.1 安装Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker
```

**请告诉我**：
- [ ] Docker安装是否成功？
- [ ] 如果失败，错误信息是什么？

### 4.2 安装Docker Compose

```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

**请告诉我**：
- [ ] Docker Compose安装是否成功？

### 4.3 安装Git（如果未安装）

```bash
apt update
apt install -y git
```

**请告诉我**：
- [ ] Git安装是否成功？

---

## 第五步：上传代码

### 5.1 选择上传方式

**方式1：使用Git（推荐）**

```bash
# 在服务器上
cd /root
git clone 你的Git仓库地址 Action
cd Action
```

**方式2：使用SCP上传**

```bash
# 在本地执行
cd ~/Desktop
tar -czf Action.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  Action

scp Action.tar.gz root@服务器IP:/root/

# 在服务器上
cd /root
tar -xzf Action.tar.gz
cd Action
```

**请告诉我**：
- [ ] 代码是否已上传到服务器？
- [ ] 上传方式：□ Git  □ SCP

---

## 第六步：配置环境变量

### 6.1 创建.env文件

```bash
cd /root/Action/backend
nano .env
```

### 6.2 配置内容

请提供以下信息，我会帮你生成完整的.env配置：

**PolarDB连接信息**：
- 主机地址：________________
- 数据库名：________________
- 用户名：________________
- 密码：________________

**DeepSeek API Key**：
- API Key：________________

**请告诉我**：
- [ ] .env文件是否已配置完成？

---

## 第七步：启动服务

### 7.1 启动Docker服务

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml up -d
```

**请告诉我**：
- [ ] 服务是否启动成功？
- [ ] 如果失败，错误信息是什么？

### 7.2 检查服务状态

```bash
docker-compose -f docker-compose.polardb.yml ps
```

**请告诉我**：
- [ ] 所有服务是否都是 `Up` 状态？
- [ ] 如果有服务未启动，是哪个服务？

---

## 第八步：初始化数据库

### 8.1 运行数据库迁移

```bash
cd /root/Action/docker
docker-compose -f docker-compose.polardb.yml exec backend alembic upgrade head
```

**请告诉我**：
- [ ] 数据库迁移是否成功？
- [ ] 如果失败，错误信息是什么？

---

## 第九步：验证部署

### 9.1 检查服务

```bash
# 检查服务状态
docker-compose -f docker-compose.polardb.yml ps

# 查看日志
docker-compose -f docker-compose.polardb.yml logs -f
```

### 9.2 测试访问

- 前端：`http://服务器IP:3001`
- 后端API文档：`http://服务器IP:8001/docs`
- 健康检查：`http://服务器IP:8001/health`

**请告诉我**：
- [ ] 前端页面是否可以访问？
- [ ] API文档是否可以访问？
- [ ] 健康检查是否通过？

---

## 🎯 当前步骤

**我们现在从第一步开始：确认资源准备**

请告诉我：
1. 云服务器是否已购买？IP地址是什么？
2. PolarDB是否已购买？连接信息是否已获取？
3. 域名是否已购买？（可选）
4. DeepSeek API Key是否已获取？

准备好了就告诉我，我们开始第一步！

