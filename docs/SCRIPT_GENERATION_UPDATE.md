# 脚本生成功能更新：一次性生成5个不同脚本

## 更新内容

### 功能变更

**之前**：每次生成脚本时，只生成1个脚本

**现在**：每次生成脚本时，默认生成5个不同的脚本

### 实现方式

1. **后端修改**：
   - `generate_script_async` 任务支持 `script_count` 参数（默认5）
   - 循环生成多个脚本，每个脚本都有不同的创意角度
   - 通过 `script_index` 和 `total_scripts` 参数确保每个脚本都不同

2. **AI提示词优化**：
   - 在提示词中添加多样性要求
   - 每个脚本使用不同的切入角度（疑问式、对比式、故事化等）
   - 确保每个脚本都有独特的创意点

3. **前端更新**：
   - 生成脚本对话框中添加"生成数量"选项（1-10个）
   - 默认值为5个
   - 显示提示信息："将生成 X 个不同版本的脚本"

## 使用场景

### 场景1：从热点关联商品生成脚本

1. 在热点监控页面选择热点
2. 选择关联的商品
3. 点击"生成脚本"
4. **系统会自动生成5个不同版本的脚本**

### 场景2：从商品关联热点生成脚本

1. 在商品管理页面选择商品
2. 选择关联的热点
3. 点击"生成脚本"
4. **系统会自动生成5个不同版本的脚本**

### 场景3：手动生成脚本

1. 在脚本管理页面点击"+生成脚本"
2. 选择热点和商品
3. 设置生成数量（默认5个，可调整1-10个）
4. 点击"生成"
5. **系统会生成指定数量的不同脚本**

## 脚本多样性保证

### 不同切入角度

- **脚本1**：疑问式开场（"你知道吗？..."）
- **脚本2**：对比式开场（"别人...，我们..."）
- **脚本3**：故事化开场（"今天遇到..."）
- **脚本4**：数据化开场（"99%的人不知道..."）
- **脚本5**：情感化开场（"太感动了..."）

### 不同叙事结构

- 问题-解决方案
- 对比展示
- 故事叙述
- 数据证明
- 情感共鸣

### 不同卖点突出

- 每个脚本可以侧重不同的商品卖点
- 使用不同的表达方式
- 采用不同的节奏感

## 技术实现

### 后端代码修改

1. **`backend/app/services/script/tasks.py`**：
   - 添加 `script_count` 参数（默认5）
   - 循环生成多个脚本
   - 返回所有脚本ID

2. **`backend/app/services/script/service.py`**：
   - `generate_script` 方法添加 `script_index` 和 `total_scripts` 参数
   - `build_prompt` 方法添加多样性提示

3. **`backend/app/agents/script_generation_agent.py`**：
   - `_build_prompt` 方法添加多样性要求
   - 根据脚本序号使用不同的切入角度

4. **`backend/app/api/v1/endpoints/scripts.py`**：
   - `GenerateScriptRequest` 添加 `script_count` 字段（默认5）
   - 验证脚本数量范围（1-10）

### 前端代码修改

1. **`frontend/src/api/scripts.ts`**：
   - `GenerateScriptRequest` 接口添加 `script_count` 字段

2. **`frontend/src/views/ScriptsView.vue`**：
   - 生成脚本对话框添加"生成数量"输入框
   - 默认值设为5

3. **`frontend/src/components/ProductSelectionDialog.vue`**：
   - 生成脚本时传递 `script_count: 5`

4. **`frontend/src/components/HotspotSelectionDialog.vue`**：
   - 生成脚本时传递 `script_count: 5`

## 注意事项

### 重新生成脚本

- **重新生成时只生成1个脚本**（不是5个）
- 因为重新生成是基于调整意见的，通常只需要1个新版本

### API调用

```typescript
// 生成5个脚本（默认）
await scriptsApi.generateScript({
  hotspot_id: "...",
  product_id: "...",
  script_count: 5  // 可选，默认5
})

// 生成1个脚本
await scriptsApi.generateScript({
  hotspot_id: "...",
  product_id: "...",
  script_count: 1
})

// 生成10个脚本（最多）
await scriptsApi.generateScript({
  hotspot_id: "...",
  product_id: "...",
  script_count: 10
})
```

### 性能考虑

- 生成5个脚本需要调用5次AI API
- 预计耗时：每个脚本约10-20秒，总共约50-100秒
- 使用异步任务，不会阻塞用户操作

### 成本考虑

- 生成5个脚本的Token消耗约为单个脚本的5倍
- 但提供了更多选择，提高脚本质量

## 测试建议

1. **功能测试**：
   - 测试生成5个脚本是否都能成功
   - 验证每个脚本是否确实不同
   - 检查脚本列表是否正确显示所有脚本

2. **性能测试**：
   - 测试生成5个脚本的耗时
   - 验证异步任务是否正常工作

3. **边界测试**：
   - 测试生成1个脚本
   - 测试生成10个脚本（最大值）
   - 测试生成0个或负数（应该报错）

## 更新日期

- **2025-01-14**：实现一次性生成5个不同脚本的功能

