#!/bin/bash

# VTICS 项目打包脚本
# 用于创建可发布的压缩包

echo "=========================================="
echo "VTICS 项目打包"
echo "=========================================="

# 获取项目根目录
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION="1.0.0"
PACKAGE_NAME="VTICS-v${VERSION}"

# 创建临时打包目录
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

echo "📦 创建打包目录..."
mkdir -p "$PACKAGE_DIR"

# 复制项目文件（排除不需要的文件）
echo "📋 复制项目文件..."
rsync -av \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.DS_Store' \
  --exclude='dist' \
  --exclude='dist-electron' \
  --exclude='*.pid' \
  --exclude='uploads/*' \
  --exclude='logs/*' \
  "$PROJECT_ROOT/" "$PACKAGE_DIR/"

# 创建启动说明文件
echo "📝 创建使用说明..."
cat > "$PACKAGE_DIR/使用说明.txt" << 'EOF'
==========================================
VTICS 使用说明
==========================================

一、系统要求
- Docker Desktop（必须）
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

二、快速开始

1. 安装 Docker Desktop
   下载地址: https://www.docker.com/products/docker-desktop

2. 启动应用
   cd docker
   chmod +x start.sh
   ./start.sh

3. 访问应用
   前端页面: http://localhost:3001
   API文档: http://localhost:8001/docs

4. 配置 DeepSeek API Key
   - 点击右上角设置图标
   - 进入"系统设置"标签
   - 点击"配置"按钮
   - 按照指引获取并输入API Key

三、常用命令

启动服务:
  cd docker && ./start.sh

停止服务:
  cd docker && ./stop.sh

查看日志:
  cd docker && docker-compose logs -f

重启服务:
  cd docker && docker-compose restart

四、故障排除

1. 端口被占用
   - 确保 3001、8001、5432、6379 端口未被占用
   - 或修改 docker-compose.yml 中的端口映射

2. 服务启动失败
   - 查看日志: docker-compose logs
   - 检查 Docker Desktop 是否正常运行
   - 确保有足够的系统资源

3. 数据库连接失败
   - 等待更长时间（首次启动需要初始化数据库）
   - 检查 postgres 容器是否正常运行

五、技术支持

如有问题，请查看项目文档或联系技术支持。

==========================================
EOF

# 创建压缩包
echo "📦 创建压缩包..."
cd "$TEMP_DIR"
tar -czf "${PROJECT_ROOT}/${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# 清理临时目录
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "✅ 打包完成！"
echo "=========================================="
echo ""
echo "压缩包位置: ${PROJECT_ROOT}/${PACKAGE_NAME}.tar.gz"
echo ""
echo "分发步骤:"
echo "  1. 将压缩包发送给用户"
echo "  2. 用户解压: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  3. 用户运行: cd ${PACKAGE_NAME}/docker && ./start.sh"
echo ""

