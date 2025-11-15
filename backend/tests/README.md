# 自动化测试文档

## 测试结构

```
tests/
├── conftest.py              # Pytest配置和共享fixtures
├── unit/                    # 单元测试（单一功能测试）
│   ├── test_models.py      # 数据模型测试
│   ├── test_hotspot_service.py    # 热点服务测试
│   ├── test_analysis_service.py   # 拆解服务测试
│   ├── test_data_service.py       # 数据服务测试
│   └── test_script_service.py      # 脚本服务测试
├── integration/            # 集成测试（关联节点联合测试）
│   ├── test_hotspot_workflow.py    # 热点工作流测试
│   ├── test_analysis_workflow.py   # 拆解工作流测试
│   ├── test_script_workflow.py     # 脚本生成工作流测试
│   └── test_full_workflow.py        # 完整业务流程测试
└── api/                     # API端点测试
    ├── test_hotspots_api.py         # 热点API测试
    ├── test_products_api.py         # 商品API测试
    └── test_scripts_api.py          # 脚本API测试
```

## 测试原则

### 1. 单一功能测试（单元测试）
- 每个服务方法独立测试
- 每个数据模型独立测试
- 不依赖外部服务（使用Mock）

### 2. 关联节点联合测试（集成测试）
- 测试多个服务协同工作
- 测试完整业务流程
- 测试数据流转

## 运行测试

### 运行所有测试
```bash
cd backend
pytest tests/ -v
```

### 运行单元测试
```bash
pytest tests/unit/ -v -m unit
```

### 运行集成测试
```bash
pytest tests/integration/ -v -m integration
```

### 运行API测试
```bash
pytest tests/api/ -v -m api
```

### 运行特定测试文件
```bash
pytest tests/unit/test_hotspot_service.py -v
```

### 运行特定测试方法
```bash
pytest tests/unit/test_hotspot_service.py::TestHotspotMonitorService::test_fetch_hotspots_success -v
```

### 使用测试脚本
```bash
cd backend
./tests/run_tests.sh
```

## 测试覆盖

### 单元测试覆盖
- ✅ 数据模型（5个模型）
- ✅ 热点监控服务（8个方法）
- ✅ 视频拆解服务（5个方法）
- ✅ 数据管理服务（10个方法）
- ✅ 脚本生成服务（6个方法）

### 集成测试覆盖
- ✅ 热点发现工作流
- ✅ 视频拆解工作流
- ✅ 脚本生成工作流
- ✅ 完整业务流程（热点->拆解->脚本）

### API测试覆盖
- ✅ 热点监控API（4个端点）
- ✅ 商品管理API（4个端点）
- ✅ 脚本生成API（6个端点）

## 测试数据

测试使用独立的测试数据库或内存数据库，不会影响生产数据。

### Fixtures
- `db_session` - 测试数据库会话
- `client` - FastAPI测试客户端
- `sample_live_room_data` - 示例直播间数据
- `sample_live_room_id` - 示例直播间ID
- `sample_product_data` - 示例商品数据
- `sample_hotspot_data` - 示例热点数据
- `sample_analysis_report_data` - 示例拆解报告数据

## Mock使用

外部服务调用使用Mock，避免实际API调用：
- TrendRadar API
- 视频拆解工具API
- DeepSeek API
- 飞书API

## 注意事项

1. **数据库隔离**：每个测试使用独立的数据库会话
2. **数据清理**：测试后自动清理（通过fixture）
3. **异步测试**：使用`@pytest.mark.asyncio`标记异步测试
4. **环境变量**：测试时设置`TESTING=true`

## 测试报告

运行测试后可以生成HTML报告：
```bash
pytest tests/ --html=report.html --self-contained-html
```

## 持续集成

可以在CI/CD中运行：
```bash
pytest tests/ -v --cov=app --cov-report=html
```

