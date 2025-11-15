# 测试快速开始指南

## 前置条件

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **确保数据库可访问**
   - 测试使用与生产相同的数据库（但使用测试表）
   - 或配置独立的测试数据库

## 快速运行

### 1. 运行所有测试
```bash
cd backend
pytest tests/ -v
```

### 2. 运行单元测试（最快）
```bash
pytest tests/unit/ -v
```

### 3. 运行集成测试
```bash
pytest tests/integration/ -v
```

### 4. 运行API测试
```bash
pytest tests/api/ -v
```

## 测试分类运行

### 按标记运行
```bash
# 只运行单元测试
pytest -m unit -v

# 只运行集成测试
pytest -m integration -v

# 只运行API测试
pytest -m api -v
```

## 运行特定测试

### 运行特定文件
```bash
pytest tests/unit/test_hotspot_service.py -v
```

### 运行特定测试类
```bash
pytest tests/unit/test_hotspot_service.py::TestHotspotMonitorService -v
```

### 运行特定测试方法
```bash
pytest tests/unit/test_hotspot_service.py::TestHotspotMonitorService::test_fetch_hotspots_success -v
```

## 测试输出

### 详细输出
```bash
pytest tests/ -v -s
```

### 显示打印语句
```bash
pytest tests/ -v -s --capture=no
```

### 只显示失败
```bash
pytest tests/ -v --tb=short
```

## 测试覆盖率

### 生成覆盖率报告
```bash
pytest tests/ --cov=app --cov-report=html
```

### 查看报告
打开 `htmlcov/index.html`

## 常见问题

### 问题1: ModuleNotFoundError
**解决**: 安装依赖
```bash
pip install -r requirements.txt
```

### 问题2: 数据库连接失败
**解决**: 检查数据库配置，确保数据库可访问

### 问题3: 测试失败
**解决**: 
1. 查看详细错误信息：`pytest tests/ -v -s`
2. 检查测试数据是否正确
3. 检查Mock是否正确配置

## 测试统计

- **测试文件**: 12个
- **测试方法**: 72个
- **测试类型**: 单元测试、集成测试、API测试

## 下一步

运行测试后：
1. 查看测试结果
2. 修复失败的测试
3. 补充遗漏的测试用例
4. 提高测试覆盖率

