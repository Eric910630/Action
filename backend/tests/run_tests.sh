#!/bin/bash
# 测试运行脚本

echo "=========================================="
echo "VTICS 自动化测试"
echo "=========================================="

# 设置环境变量
export TESTING=true
unset DATABASE_URL

# 运行单元测试
echo ""
echo "1. 运行单元测试..."
pytest tests/unit/ -v --tb=short -m unit

# 运行集成测试
echo ""
echo "2. 运行集成测试..."
pytest tests/integration/ -v --tb=short -m integration

# 运行API测试
echo ""
echo "3. 运行API测试..."
pytest tests/api/ -v --tb=short -m api

# 运行所有测试
echo ""
echo "4. 运行所有测试..."
pytest tests/ -v --tb=short

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

