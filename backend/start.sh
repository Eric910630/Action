#!/bin/bash
# 启动开发服务器

echo "启动VTICS后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "启动FastAPI服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

