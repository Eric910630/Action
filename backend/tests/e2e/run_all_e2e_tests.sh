#!/bin/bash

# 运行所有E2E测试
# 包括：语义功能测试、视频拆解测试、脚本生成测试、完整流程测试

echo "=========================================="
echo "运行E2E测试套件"
echo "=========================================="

# 设置环境变量
export USE_TEST_DB=true
export TESTING=true

# 运行语义功能测试
echo ""
echo "1. 运行语义关联度功能测试..."
pytest tests/e2e/test_semantic_features.py -v --tb=short

# 运行视频拆解测试
echo ""
echo "2. 运行视频拆解E2E测试..."
pytest tests/e2e/test_analysis_e2e.py -v --tb=short

# 运行脚本生成测试
echo ""
echo "3. 运行脚本生成E2E测试..."
pytest tests/e2e/test_script_generation_e2e.py -v --tb=short

# 运行完整流程测试
echo ""
echo "4. 运行完整流程E2E测试..."
pytest tests/e2e/test_complete_workflow_e2e.py -v --tb=short

# 运行原有测试（可选）
echo ""
echo "5. 运行原有E2E测试..."
pytest tests/e2e/test_e2e_workflow.py -v --tb=short

echo ""
echo "=========================================="
echo "所有E2E测试完成"
echo "=========================================="

