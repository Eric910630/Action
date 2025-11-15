# 测试指南

## 测试运行

### 快速开始

1. **安装测试依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **运行所有测试**
   ```bash
   pytest tests/ -v
   ```

3. **运行特定类型测试**
   ```bash
   # 单元测试
   pytest tests/unit/ -v -m unit
   
   # 集成测试
   pytest tests/integration/ -v -m integration
   
   # API测试
   pytest tests/api/ -v -m api
   ```

## 测试分类

### 单元测试（单一功能测试）

测试单个服务方法或数据模型，不依赖外部服务。

**位置**: `tests/unit/`

**示例**:
- `test_models.py` - 测试数据模型的CRUD操作
- `test_hotspot_service.py` - 测试热点服务的每个方法
- `test_analysis_service.py` - 测试拆解服务的每个方法
- `test_data_service.py` - 测试数据服务的每个方法
- `test_script_service.py` - 测试脚本服务的每个方法

### 集成测试（关联节点联合测试）

测试多个服务协同工作，验证完整业务流程。

**位置**: `tests/integration/`

**示例**:
- `test_hotspot_workflow.py` - 热点发现完整流程
- `test_analysis_workflow.py` - 视频拆解完整流程
- `test_script_workflow.py` - 脚本生成完整流程
- `test_full_workflow.py` - 从热点到脚本的完整流程

### API测试

测试API端点的请求和响应。

**位置**: `tests/api/`

**示例**:
- `test_hotspots_api.py` - 热点API端点测试
- `test_products_api.py` - 商品API端点测试
- `test_scripts_api.py` - 脚本API端点测试

## 测试用例示例

### 单元测试示例

```python
def test_create_hotspot(self, db_session: Session):
    """测试创建热点"""
    hotspot = Hotspot(
        id=str(uuid.uuid4()),
        title="测试热点",
        url="https://test.com",
        platform="douyin",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(hotspot)
    db_session.commit()
    
    assert hotspot.id is not None
    assert hotspot.title == "测试热点"
```

### 集成测试示例

```python
@pytest.mark.asyncio
async def test_complete_hotspot_workflow(self, service, db_session):
    """测试完整热点工作流：抓取 -> 筛选 -> 保存"""
    # 1. 获取热点
    hotspots = await service.fetch_hotspots()
    
    # 2. 筛选热点
    filtered = service.filter_hotspots(hotspots, keywords)
    
    # 3. 保存热点
    saved_count = service.save_hotspots(db_session, filtered)
    
    assert saved_count > 0
```

### API测试示例

```python
def test_get_hotspots(self, client):
    """测试获取热点列表"""
    response = client.get("/api/v1/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
```

## 测试标记

使用pytest标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.slow` - 慢速测试

## Mock使用

外部服务调用使用Mock：

```python
with patch.object(
    service.trendradar_client,
    'get_hotspots',
    new_callable=AsyncMock,
    return_value=mock_data
):
    result = await service.fetch_hotspots()
```

## 测试数据

使用fixtures提供测试数据：

- `db_session` - 数据库会话
- `client` - FastAPI测试客户端
- `sample_live_room_id` - 示例直播间ID
- `sample_hotspot_data` - 示例热点数据

## 运行特定测试

```bash
# 运行特定文件
pytest tests/unit/test_hotspot_service.py -v

# 运行特定类
pytest tests/unit/test_hotspot_service.py::TestHotspotMonitorService -v

# 运行特定方法
pytest tests/unit/test_hotspot_service.py::TestHotspotMonitorService::test_fetch_hotspots_success -v
```

## 测试覆盖率

生成测试覆盖率报告：

```bash
pytest tests/ --cov=app --cov-report=html
```

查看报告：打开 `htmlcov/index.html`

## 持续集成

在CI/CD中运行测试：

```bash
pytest tests/ -v --tb=short --cov=app --cov-report=xml
```

## 常见问题

### 1. 数据库连接失败
- 检查数据库配置
- 确保测试数据库存在
- 检查环境变量

### 2. 导入错误
- 确保在backend目录下运行
- 检查Python路径

### 3. 异步测试失败
- 确保使用`@pytest.mark.asyncio`
- 检查异步函数是否正确标记

## 测试最佳实践

1. **单一职责**：每个测试只测试一个功能
2. **独立性**：测试之间不相互依赖
3. **可重复**：测试结果应该一致
4. **快速**：单元测试应该快速执行
5. **清晰命名**：测试名称应该描述测试内容

