# 更新服务器前端代码（解决浏览器标题问题）

## 🎯 问题

浏览器标题还显示 "VTICS"，因为服务器上的前端代码还没有更新。

## ✅ 解决方案

在服务器上执行以下命令：

```bash
# 1. SSH连接到服务器
ssh root@39.102.60.67

# 2. 进入项目目录并拉取最新代码
cd /root/Action
git pull

# 3. 重新构建前端
cd frontend
npm run build

# 4. 复制构建文件到Nginx目录
sudo cp -r dist/* /var/www/action-script/

# 5. 设置权限
sudo chown -R www-data:www-data /var/www/action-script
sudo chmod -R 755 /var/www/action-script

# 6. 验证（可选）
curl http://localhost/api/v1/live-rooms/ | head -20
```

**完成后**：刷新浏览器页面（`http://actionscript.fun`），标题应该显示 "Action" 了。

---

## 📝 后续开发流程总结

### 日常开发流程

1. **本地开发**（localhost:3001）
   ```bash
   # 在本地修改代码
   cd ~/Desktop/Action/backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   
   # 新终端：启动前端
   cd ~/Desktop/Action/frontend
   npm run dev
   ```
   - 访问：http://localhost:3001
   - 在这里测试功能是否正常

2. **本地测试通过后，Git提交**
   ```bash
   cd ~/Desktop/Action
   git add .
   git commit -m "描述你的修改"
   git push
   ```

3. **服务器更新**（actionscript.fun）
   ```bash
   # SSH到服务器
   ssh root@39.102.60.67
   
   # 更新代码
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

4. **线上验证**
   - 访问：http://actionscript.fun
   - 验证功能是否正常

---

## 🎯 总结

**是的，你的理解完全正确！**

- **localhost**：本地开发测试环境
- **actionscript.fun**：生产环境（线上）

**流程**：
```
本地开发（localhost） → 测试验证 → Git提交 → 服务器更新 → 线上验证（actionscript.fun）
```

**不需要同时打开两个页面**，而是：
1. 开发时用 localhost
2. 测试通过后更新到服务器
3. 在 actionscript.fun 上验证最终效果

