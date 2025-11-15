# VTICS 部署使用指南

## 🚀 快速开始（推荐）

### 方式一：Docker Compose（最简单）

**前提条件**：安装 Docker Desktop

1. **解压项目**
   ```bash
   tar -xzf VTICS-v1.0.0.tar.gz
   cd VTICS-v1.0.0
   ```

2. **启动应用**
   ```bash
   cd docker
   chmod +x start.sh
   ./start.sh
   ```

3. **访问应用**
   - 前端页面: http://localhost:3001
   - API文档: http://localhost:8001/docs

4. **配置API Key**
   - 点击右上角设置图标 ⚙️
   - 进入"系统设置"标签
   - 点击"配置DeepSeek API Key"
   - 按照指引获取并输入API Key

### 停止应用
```bash
cd docker
./stop.sh
```

---

## 📦 打包项目

运行打包脚本：
```bash
chmod +x 打包脚本.sh
./打包脚本.sh
```

这会生成 `VTICS-v1.0.0.tar.gz` 压缩包，可以直接分发给用户。

---

## 🔧 系统要求

- **Docker Desktop**（必须）
- 至少 **4GB** 可用内存
- 至少 **10GB** 可用磁盘空间
- 端口 **3001、8001、5432、6379** 未被占用

---

## 📝 详细文档

更多部署选项和说明，请查看：`打包部署指南.md`

---

## ⚠️ 注意事项

1. **首次启动**：需要等待约30-60秒，等待数据库初始化完成
2. **API Key配置**：必须在设置中配置DeepSeek API Key才能使用AI功能
3. **数据持久化**：所有数据保存在Docker volumes中，删除容器不会丢失数据
4. **完全清理**：如需完全删除所有数据，运行 `docker-compose down -v`

---

## 🆘 故障排除

### 端口被占用
修改 `docker/docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "3002:80"  # 前端改为3002
  - "8002:8001"  # 后端改为8002
```

### 服务启动失败
```bash
# 查看日志
cd docker
docker-compose logs -f

# 重启服务
docker-compose restart
```

### 数据库连接失败
等待更长时间，首次启动需要初始化数据库和运行迁移。

---

**版本**: v1.0.0  
**更新日期**: 2025-01-14

