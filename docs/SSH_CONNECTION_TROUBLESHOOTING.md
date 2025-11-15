# SSH连接故障排查指南

## 问题现象

```
Connection closed by 39.102.60.67 port 22
```

## 可能原因和解决方案

### 1. 检查云服务商控制台

**阿里云/腾讯云控制台检查**：

1. **安全组规则**
   - 登录云服务商控制台
   - 找到你的服务器实例
   - 检查"安全组"设置
   - 确保22端口（SSH）已开放
   - 建议：开放22端口给 `0.0.0.0/0`（所有IP）或你的公网IP

2. **服务器状态**
   - 确认服务器状态为"运行中"
   - 如果状态异常，尝试重启服务器

3. **使用Web终端**
   - 在控制台找到"远程连接"或"Web终端"功能
   - 通过Web终端先登录一次服务器
   - 这样可以确认服务器本身是否正常

### 2. 检查SSH服务配置

如果可以通过Web终端登录，检查SSH配置：

```bash
# 检查SSH服务状态
systemctl status sshd

# 检查SSH配置
cat /etc/ssh/sshd_config | grep -E "PasswordAuthentication|PermitRootLogin"

# 如果PasswordAuthentication为no，需要改为yes
# 如果PermitRootLogin为no，需要改为yes（或prohibit-password）
```

### 3. 使用密钥认证（推荐）

如果服务器只支持密钥认证：

**在本地生成密钥对**：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**将公钥添加到服务器**：
```bash
# 方法1：通过Web终端手动添加
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容，然后在服务器上执行：
# echo "你的公钥内容" >> ~/.ssh/authorized_keys
# chmod 600 ~/.ssh/authorized_keys
# chmod 700 ~/.ssh

# 方法2：如果可以通过其他方式登录，使用ssh-copy-id
ssh-copy-id root@39.102.60.67
```

**使用密钥连接**：
```bash
ssh -i ~/.ssh/id_ed25519 root@39.102.60.67
```

### 4. 尝试其他用户

如果root用户被禁用，尝试使用其他用户：

```bash
# 尝试使用ubuntu用户（Ubuntu系统默认用户）
ssh ubuntu@39.102.60.67

# 或者尝试使用其他管理员用户
```

### 5. 检查防火墙

如果可以通过Web终端登录，检查防火墙：

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 22/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 快速检查清单

- [ ] 云服务商控制台：安全组已开放22端口
- [ ] 云服务商控制台：服务器状态为"运行中"
- [ ] 尝试使用Web终端登录
- [ ] 检查SSH服务配置（PasswordAuthentication、PermitRootLogin）
- [ ] 检查防火墙规则
- [ ] 尝试使用密钥认证
- [ ] 尝试使用其他用户（如ubuntu）

## 下一步

完成以上检查后，告诉我：
1. 能否通过Web终端登录？
2. 安全组配置如何？
3. SSH配置如何？

然后我们可以继续部署流程。

