# Action 系统架构与功能流程匹配文档

## 📋 文档说明

本文档基于 `upgrade.md` 中的重构需求，对当前系统架构和功能流程进行匹配分析，明确需要修改的部分和实现方案。

---

## 🎯 重构需求概览

### 核心重构点

1. **前端布局重构**：从左侧标签式改为铺满屏幕的热点图
2. **直播间选择方式**：从下拉菜单改为 Tab 切换
3. **视频拆解自动化**：改为后台定时自动任务
4. **匹配度排序**：根据与直播间/类目/商品的匹配度降序排列
5. **功能相互关联**：热点监控 ↔ 商品管理双向关联
6. **功能简化**：只保留三个主要功能页
7. **直播间管理**：改为设置功能（齿轮图标）

---

## 1. 热点抓取 - 呈现方式重构

### 📝 需求描述

**当前问题**：
- 用户通过下拉菜单选择直播间
- 不够直观，无法快速找到自己直播间/类目下的核心热点

**重构目标**：
- 所有直播间以 Tab 方式在屏幕上方平铺
- 用户通过点击 Tab 切换直播间
- 专注于第一时间找到自己直播间/类目下的核心热点

### 🔍 当前架构分析

**前端实现**：
- 文件：`frontend/src/views/HotspotsView.vue`
- 当前方式：使用 `el-select` 下拉菜单选择直播间（第22-31行）
- 气泡图组件：`HotspotBubbleChart.vue` 已存在

**后端实现**：
- API：`GET /api/v1/hotspots/visualization` 
- 返回格式：按直播间分组的热点数据
- 支持按 `live_room_id` 筛选

### ✅ 匹配方案

#### 1.1 前端改造

**需要修改的文件**：
- `frontend/src/views/HotspotsView.vue`
- `frontend/src/App.vue`（整体布局）

**实现步骤**：

1. **移除下拉菜单，添加 Tab 组件**
   ```vue
   <!-- 替换原有的 el-select -->
   <el-tabs v-model="activeLiveRoomId" @tab-change="handleLiveRoomChange">
     <el-tab-pane
       v-for="room in liveRooms"
       :key="room.id"
       :label="room.name"
       :name="room.id"
     />
   </el-tabs>
   ```

2. **调整布局，使气泡图铺满屏幕**
   - 移除 `el-card` 的 padding
   - 设置气泡图容器高度为 `calc(100vh - 120px)`
   - Tab 固定在顶部

3. **默认显示第一个直播间**
   - 页面加载时自动选择第一个直播间
   - 切换 Tab 时重新加载对应直播间热点

#### 1.2 后端支持

**当前状态**：✅ 已支持
- `GET /api/v1/hotspots/visualization?live_room_id={id}` 已实现
- 返回格式符合需求

**无需修改**，只需前端调用时传入 `live_room_id` 参数

---

## 2. 视频拆解 - 自动化改造

### 📝 需求描述

**当前问题**：
- 用户需要手动复制 URL 进行视频拆解
- 操作繁琐，不够自动化

**重构目标**：
- 视频拆解应该是后台默认行为，定时自动执行
- 热点视频抓取后，自动触发拆解
- 无需用户手动操作

### 🔍 当前架构分析

**当前实现**：
- 文件：`backend/app/services/analysis/tasks.py`
- 任务：`analyze_video_async` - 手动触发的异步任务
- API：`POST /api/v1/analysis/analyze` - 需要手动传入 `video_url`

**定时任务配置**：
- 文件：`backend/app/celery_app.py`
- 已有定时任务：`fetch-daily-hotspots`（每日8:00）
- 已有定时任务：`push-hotspots-to-feishu`（每日9:00）

### ✅ 匹配方案

#### 2.1 后端改造

**需要修改的文件**：
- `backend/app/services/hotspot/tasks.py`
- `backend/app/celery_app.py`
- `backend/app/services/hotspot/service.py`

**实现步骤**：

1. **在热点抓取任务中自动触发视频拆解**
   ```python
   @celery_app.task
   def fetch_daily_hotspots(platform: str = "douyin", live_room_id: str = None):
       # ... 现有热点抓取逻辑 ...
       
       # 自动拆解热点视频
       for hotspot in filtered_hotspots:
           if hotspot.get('url'):
               # 异步触发视频拆解
               analyze_video_async.delay(hotspot['url'])
   ```

2. **添加批量拆解任务**
   ```python
   @celery_app.task
   def auto_analyze_hotspot_videos(live_room_id: str = None):
       """自动拆解热点视频"""
       # 获取未拆解的热点视频
       # 批量触发拆解任务
   ```

3. **可选：添加定时任务（如果热点抓取和拆解需要分离）**
   ```python
   celery_app.conf.beat_schedule = {
       # ... 现有任务 ...
       "auto-analyze-hotspot-videos": {
           "task": "app.services.hotspot.tasks.auto_analyze_hotspot_videos",
           "schedule": {"hour": 8, "minute": 30},  # 热点抓取后30分钟
       },
   }
   ```

#### 2.2 前端改造

**需要修改的文件**：
- `frontend/src/views/AnalysisView.vue`（可选，如果保留手动拆解功能）

**实现步骤**：

1. **移除或隐藏手动拆解入口**（可选）
   - 如果完全自动化，可以移除手动拆解页面
   - 或者保留为"拆解与生成"功能页的一部分（用于手动上传URL）

2. **在热点监控页面显示拆解状态**
   - 在气泡图上显示已拆解/未拆解状态
   - 点击气泡可查看拆解报告

---

## 3. 视频拆解 - 匹配度排序

### 📝 需求描述

**重构目标**：
- 热点视频拆解后，除了常规内容（脚本文档、3秒完播等）
- 还应该有一个与直播间/主营类目/主营商品的匹配程度
- 根据匹配度降序排列

### 🔍 当前架构分析

**当前实现**：
- 拆解报告模型：`backend/app/models/analysis.py`
- 字段：`basic_info`, `shot_table`, `golden_3s`, `viral_formula`, `production_tips`
- **缺少**：匹配度字段

**匹配度计算**：
- 热点已有 `match_score` 字段（与直播间主推商品的匹配度）
- 但拆解报告中没有存储匹配度

### ✅ 匹配方案

#### 3.1 数据库模型改造

**需要修改的文件**：
- `backend/app/models/analysis.py`

**实现步骤**：

1. **添加匹配度相关字段**
   ```python
   class AnalysisReport(Base):
       # ... 现有字段 ...
       
       # 新增字段
       live_room_id: str = Column(String, nullable=True)  # 关联直播间
       match_score: float = Column(Float, nullable=True)   # 匹配度
       matched_category: str = Column(String, nullable=True)  # 匹配的类目
       matched_product_id: str = Column(String, nullable=True)  # 匹配的商品ID
   ```

2. **创建数据库迁移**
   ```bash
   alembic revision --autogenerate -m "add_match_score_to_analysis_reports"
   alembic upgrade head
   ```

#### 3.2 服务层改造

**需要修改的文件**：
- `backend/app/services/analysis/service.py`
- `backend/app/services/hotspot/service.py`

**实现步骤**：

1. **在拆解时计算匹配度**
   ```python
   async def analyze_and_save(
       self,
       db: Session,
       video_url: str,
       options: Optional[Dict[str, Any]] = None,
       hotspot_id: Optional[str] = None  # 新增参数
   ) -> AnalysisReport:
       # ... 现有拆解逻辑 ...
       
       # 如果有关联的热点，计算匹配度
       if hotspot_id:
           hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
           if hotspot:
               report.live_room_id = hotspot.live_room_id
               report.match_score = hotspot.match_score
               # 计算与商品的匹配度
               # ...
   ```

2. **API 返回时按匹配度排序**
   ```python
   @router.get("/reports")
   async def get_reports(
       live_room_id: Optional[str] = None,
       # ... 其他参数 ...
   ):
       query = db.query(AnalysisReport)
       
       if live_room_id:
           query = query.filter(AnalysisReport.live_room_id == live_room_id)
       
       # 按匹配度降序排列
       reports = query.order_by(
           AnalysisReport.match_score.desc().nulls_last(),
           AnalysisReport.created_at.desc()
       ).all()
   ```

#### 3.3 前端改造

**需要修改的文件**：
- `frontend/src/views/AnalysisView.vue`（如果保留）
- `frontend/src/api/analysis.ts`

**实现步骤**：

1. **在拆解报告列表中显示匹配度**
   - 添加匹配度列
   - 支持按匹配度排序

2. **在热点监控页面显示拆解状态和匹配度**
   - 气泡图上显示已拆解状态
   - 点击气泡查看拆解报告时显示匹配度

---

## 4. 相互关联 - 热点监控 ↔ 商品管理

### 📝 需求描述

**重构目标**：

1. **热点监控 → 商品管理**：
   - 点击气泡图内的对应气泡
   - 直接拉起商品管理的对话框
   - 可以选择已上传的商品或手动上传新商品
   - 点击操作后，直接输出视频脚本

2. **商品管理 → 热点监控**：
   - 上传完新商品后，或针对老产品
   - 通过点击操作按钮
   - 弹出热点监控的对话框
   - 显示对应直播间的气泡图（可切换成列表模式）
   - 点击操作按钮后，直接输出视频脚本

### 🔍 当前架构分析

**当前实现**：
- 热点监控：`frontend/src/views/HotspotsView.vue`
- 商品管理：`frontend/src/views/ProductsView.vue`
- 脚本生成：`frontend/src/views/ScriptsView.vue`
- 三者独立，没有关联

**API 支持**：
- 商品列表：`GET /api/v1/products?live_room_id={id}`
- 热点列表：`GET /api/v1/hotspots?live_room_id={id}`
- 脚本生成：`POST /api/v1/scripts/generate`

### ✅ 匹配方案

#### 4.1 前端组件改造

**需要创建的新组件**：
- `frontend/src/components/ProductSelectionDialog.vue` - 商品选择对话框
- `frontend/src/components/HotspotSelectionDialog.vue` - 热点选择对话框

**需要修改的文件**：
- `frontend/src/components/HotspotBubbleChart.vue` - 添加点击事件
- `frontend/src/views/HotspotsView.vue` - 集成商品选择对话框
- `frontend/src/views/ProductsView.vue` - 集成热点选择对话框

**实现步骤**：

1. **创建商品选择对话框组件**
   ```vue
   <!-- ProductSelectionDialog.vue -->
   <template>
     <el-dialog
       v-model="visible"
       title="选择商品"
       width="800px"
     >
       <!-- 商品列表 -->
       <el-table :data="products">
         <el-table-column prop="name" label="商品名称" />
         <el-table-column label="操作">
           <template #default="{ row }">
             <el-button @click="selectProduct(row)">选择</el-button>
           </template>
         </el-table-column>
       </el-table>
       
       <!-- 上传新商品按钮 -->
       <el-button @click="showUploadDialog = true">上传新商品</el-button>
       
       <!-- 生成脚本按钮 -->
       <el-button 
         type="primary" 
         @click="generateScript"
         :disabled="!selectedProduct"
       >
         生成视频脚本
       </el-button>
     </el-dialog>
   </template>
   ```

2. **修改气泡图组件，添加点击事件**
   ```vue
   <!-- HotspotBubbleChart.vue -->
   <script setup lang="ts">
   const emit = defineEmits<{
     bubbleClick: [hotspot: Hotspot]
   }>()
   
   chartInstance.on('click', (params: any) => {
     emit('bubbleClick', params.data)
   })
   </script>
   ```

3. **在热点监控页面集成商品选择对话框**
   ```vue
   <!-- HotspotsView.vue -->
   <template>
     <HotspotBubbleChart 
       :data="visualizationData" 
       @bubble-click="handleBubbleClick"
     />
     
     <ProductSelectionDialog
       v-model="productDialogVisible"
       :hotspot="selectedHotspot"
       @script-generated="handleScriptGenerated"
     />
   </template>
   
   <script setup lang="ts">
   const handleBubbleClick = (hotspot: Hotspot) => {
     selectedHotspot.value = hotspot
     productDialogVisible.value = true
   }
   </script>
   ```

4. **在商品管理页面集成热点选择对话框**
   ```vue
   <!-- ProductsView.vue -->
   <template>
     <el-table :data="products">
       <el-table-column label="操作">
         <template #default="{ row }">
           <el-button @click="openHotspotDialog(row)">选择热点</el-button>
         </template>
       </el-table-column>
     </el-table>
     
     <HotspotSelectionDialog
       v-model="hotspotDialogVisible"
       :product="selectedProduct"
       @script-generated="handleScriptGenerated"
     />
   </template>
   ```

#### 4.2 后端 API 支持

**需要修改的文件**：
- `backend/app/api/v1/endpoints/scripts.py`

**实现步骤**：

1. **确保脚本生成 API 支持热点+商品组合**
   ```python
   @router.post("/generate")
   async def generate_script(
       hotspot_id: str,
       product_id: str,
       # ... 其他参数 ...
   ):
       # 获取热点信息
       hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
       
       # 获取商品信息
       product = db.query(Product).filter(Product.id == product_id).first()
       
       # 获取拆解报告（如果存在）
       analysis_report = None
       if hotspot.url:
           analysis_report = db.query(AnalysisReport).filter(
               AnalysisReport.video_url == hotspot.url
           ).first()
       
       # 生成脚本
       # ...
   ```

---

## 5. 前端页面重构

### 📝 需求描述

**重构目标**：

1. **系统名称**：Action
2. **布局重构**：
   - 当前：左侧标签式布局
   - 目标：用户进入后直接看到铺满屏幕的热点图
   - 通过 Tab 切换直播间
   - 专注在热点上
3. **功能简化**：
   - 主要功能页只有三个：
     - 热点监控
     - 商品管理
     - 拆解与生成（手动上传URL的拆解和模仿脚本生成）
4. **直播间管理**：
   - 改为设置功能
   - 在页面角落添加齿轮图标
   - 点击后弹出设置对话框

### 🔍 当前架构分析

**当前实现**：
- `frontend/src/App.vue` - 左侧标签式布局
- 路由：5个页面（热点监控、视频拆解、脚本生成、商品管理、直播间管理）

### ✅ 匹配方案

#### 5.1 整体布局重构

**需要修改的文件**：
- `frontend/src/App.vue`
- `frontend/src/router/index.ts`

**实现步骤**：

1. **重构 App.vue，改为全屏布局**
   ```vue
   <template>
     <div class="app-container">
       <!-- 顶部导航栏 -->
       <el-header class="app-header">
         <h1 class="logo">Action</h1>
         <div class="header-actions">
           <!-- 设置按钮（齿轮图标） -->
           <el-button 
             circle 
             @click="settingsVisible = true"
             class="settings-btn"
           >
             <el-icon><Setting /></el-icon>
           </el-button>
         </div>
       </el-header>
       
       <!-- 主内容区 -->
       <el-main class="app-main">
         <router-view />
       </el-main>
       
       <!-- 设置对话框 -->
       <LiveRoomSettingsDialog v-model="settingsVisible" />
     </div>
   </template>
   ```

2. **修改路由，只保留三个主要页面**
   ```typescript
   // router/index.ts
   const routes: RouteRecordRaw[] = [
     {
       path: '/',
       redirect: '/hotspots'  // 默认进入热点监控
     },
     {
       path: '/hotspots',
       name: 'Hotspots',
       component: () => import('@/views/HotspotsView.vue')
     },
     {
       path: '/products',
       name: 'Products',
       component: () => import('@/views/ProductsView.vue')
     },
     {
       path: '/analysis',
       name: 'Analysis',
       component: () => import('@/views/AnalysisView.vue')  // 拆解与生成
     }
   ]
   ```

3. **移除左侧菜单，改为顶部导航（可选）**
   - 如果不需要导航栏，可以完全移除
   - 或者改为顶部简洁导航（只显示当前页面名称）

#### 5.2 热点监控页面全屏化

**需要修改的文件**：
- `frontend/src/views/HotspotsView.vue`

**实现步骤**：

1. **移除 Card 容器，直接全屏显示**
   ```vue
   <template>
     <div class="hotspots-fullscreen">
       <!-- Tab 切换直播间 -->
       <el-tabs 
         v-model="activeLiveRoomId" 
         class="live-room-tabs"
         @tab-change="handleLiveRoomChange"
       >
         <el-tab-pane
           v-for="room in liveRooms"
           :key="room.id"
           :label="room.name"
           :name="room.id"
         />
       </el-tabs>
       
       <!-- 气泡图（铺满剩余空间） -->
       <div class="bubble-chart-container">
         <HotspotBubbleChart 
           :data="visualizationData" 
           @bubble-click="handleBubbleClick"
         />
       </div>
     </div>
   </template>
   
   <style scoped>
   .hotspots-fullscreen {
     height: 100vh;
     display: flex;
     flex-direction: column;
   }
   
   .live-room-tabs {
     flex-shrink: 0;
     background: white;
     padding: 0 20px;
   }
   
   .bubble-chart-container {
     flex: 1;
     overflow: hidden;
   }
   </style>
   ```

#### 5.3 创建设置对话框组件

**需要创建的文件**：
- `frontend/src/components/LiveRoomSettingsDialog.vue`

**实现步骤**：

1. **创建设置对话框组件**
   ```vue
   <!-- LiveRoomSettingsDialog.vue -->
   <template>
     <el-dialog
       v-model="visible"
       title="直播间设置"
       width="900px"
     >
       <!-- 直播间列表 -->
       <el-table :data="liveRooms">
         <el-table-column prop="name" label="直播间名称" />
         <el-table-column prop="category" label="类目" />
         <el-table-column label="操作">
           <template #default="{ row }">
             <el-button @click="editLiveRoom(row)">编辑</el-button>
             <el-button @click="deleteLiveRoom(row)">删除</el-button>
           </template>
         </el-table-column>
       </el-table>
       
       <el-button type="primary" @click="createLiveRoom">
         新建直播间
       </el-button>
     </el-dialog>
   </template>
   ```

---

## 6. 实现优先级建议

### 🔥 高优先级（核心功能）

1. **前端布局重构**（第5节）
   - 影响用户体验，需要优先完成
   - 预计工作量：2-3天

2. **直播间 Tab 切换**（第1节）
   - 核心交互改进
   - 预计工作量：1天

3. **热点监控 ↔ 商品管理关联**（第4节）
   - 核心功能增强
   - 预计工作量：3-4天

### ⚡ 中优先级（功能增强）

4. **视频拆解自动化**（第2节）
   - 提升自动化程度
   - 预计工作量：2天

5. **匹配度排序**（第3节）
   - 数据展示优化
   - 预计工作量：2天

### 📝 低优先级（优化）

6. **其他优化**
   - 配色调整
   - 性能优化
   - 错误处理

---

## 7. 技术栈确认

### 前端技术栈

- **Vue 3** + **TypeScript**
- **Element Plus** - UI 组件库
- **ECharts** - 气泡图可视化
- **Vue Router** - 路由管理

### 后端技术栈

- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **Celery** - 异步任务队列
- **PostgreSQL** - 数据库
- **Redis** - 缓存和消息队列

### 相关文档

- Element Plus Tabs: https://element-plus.org/en-US/component/tabs.html
- Element Plus Dialog: https://element-plus.org/en-US/component/dialog.html
- Vue 3 Composition API: https://vuejs.org/guide/extras/composition-api-faq.html

---

## 8. 数据库迁移计划

### 需要创建的迁移

1. **为 AnalysisReport 添加匹配度字段**
   ```python
   # migrations/versions/xxx_add_match_score_to_analysis_reports.py
   def upgrade():
       op.add_column('analysis_reports', sa.Column('live_room_id', sa.String(), nullable=True))
       op.add_column('analysis_reports', sa.Column('match_score', sa.Float(), nullable=True))
       op.add_column('analysis_reports', sa.Column('matched_category', sa.String(), nullable=True))
       op.add_column('analysis_reports', sa.Column('matched_product_id', sa.String(), nullable=True))
   ```

---

## 9. API 变更总结

### 新增 API（如果需要）

1. **批量生成脚本**
   ```
   POST /api/v1/scripts/generate-batch
   Body: { hotspot_ids: [], product_id: string }
   ```

### 修改的 API

1. **获取拆解报告列表**
   - 添加 `live_room_id` 参数
   - 返回结果按 `match_score` 降序排列

2. **视频拆解**
   - 支持传入 `hotspot_id` 参数
   - 自动关联热点信息并计算匹配度

---

## 10. 测试计划

### 前端测试

1. **布局测试**
   - [ ] 全屏布局是否正确
   - [ ] Tab 切换是否流畅
   - [ ] 对话框交互是否正确

2. **功能测试**
   - [ ] 热点监控 → 商品管理流程
   - [ ] 商品管理 → 热点监控流程
   - [ ] 脚本生成功能

### 后端测试

1. **自动化任务测试**
   - [ ] 热点抓取后自动触发视频拆解
   - [ ] 匹配度计算是否正确

2. **API 测试**
   - [ ] 拆解报告按匹配度排序
   - [ ] 脚本生成 API

---

## 📝 总结

本文档详细匹配了 `upgrade.md` 中的所有重构需求与当前系统架构，提供了具体的实现方案和代码示例。按照优先级逐步实施，可以顺利完成系统重构。

**关键改进点**：
1. ✅ 前端布局从侧边栏改为全屏热点图
2. ✅ 直播间选择从下拉菜单改为 Tab 切换
3. ✅ 视频拆解自动化
4. ✅ 匹配度排序和展示
5. ✅ 热点监控与商品管理双向关联
6. ✅ 功能简化，只保留三个主要页面
7. ✅ 直播间管理改为设置功能

---

---

## 11. E2E测试拟真化改造

### 📝 需求描述

**当前问题**：
- E2E测试全部使用Mock数据
- TrendRadar API调用被Mock
- LLM调用（DeepSeek）被Mock
- 无法验证真实场景下的系统行为

**重构目标**：
- E2E测试改为纯拟真测试
- **真实热点抓取**：如果TrendRadar有安全风险可以Mock，需要根据TrendRadar项目文档中的风险提示决定
- **LLM过程全拟真**：所有LLM调用必须使用真实API，不能Mock
- 确保测试环境能够真实反映生产环境行为

### 🔍 当前架构分析

**当前E2E测试实现**：
- 文件：`backend/tests/e2e/test_e2e_workflow.py`
- 文件：`backend/tests/e2e/test_complete_workflow_e2e.py`
- 文件：`backend/tests/e2e/test_e2e_with_external_apis.py`

**Mock使用情况**：
1. **TrendRadar API**：
   - 使用 `patch.object(service.trendradar_client, 'get_hotspots')` Mock
   - 返回模拟热点数据

2. **DeepSeek API**：
   - 使用 `patch.object(service.deepseek_client, 'generate')` Mock
   - 返回模拟脚本生成结果

3. **视频拆解工具**：
   - 使用 `patch('app.services.analysis.tasks.analyze_video_async.delay')` Mock
   - 返回模拟拆解报告

### ✅ 匹配方案

#### 11.1 TrendRadar API拟真策略

**需要确认的事项**：
1. 查看TrendRadar项目文档，了解安全风险提示
2. 确认是否可以在测试环境使用真实API
3. 如果存在安全风险（如IP封禁、频率限制等），设计Mock策略

**实现步骤**：

1. **检查TrendRadar文档**
   ```bash
   # 需要查看TrendRadar项目的README或文档
   # 确认：
   # - API调用频率限制
   # - IP白名单要求
   # - 测试环境支持
   # - 安全风险提示
   ```

2. **根据风险决定策略**
   ```python
   # backend/tests/conftest.py
   import os
   
   @pytest.fixture
   def use_real_trendradar():
       """根据环境变量决定是否使用真实TrendRadar API"""
       # 如果TrendRadar文档提示有安全风险，则使用Mock
       # 否则使用真实API
       trendradar_risk_level = os.getenv("TRENDRADAR_RISK_LEVEL", "low")
       
       if trendradar_risk_level == "high":
           # 使用Mock
           return False
       else:
           # 使用真实API（需要配置API Key）
           return bool(os.getenv("TRENDRADAR_API_KEY"))
   ```

3. **修改E2E测试，移除TrendRadar Mock**
   ```python
   # backend/tests/e2e/test_e2e_workflow.py
   @pytest.mark.asyncio
   async def test_e2e_hotspot_fetch_real(self, client, db_session, use_real_trendradar):
       """E2E测试：真实热点抓取流程"""
       
       if not use_real_trendradar:
           pytest.skip("TrendRadar API未配置或存在安全风险，跳过真实API测试")
       
       # 不再Mock，直接调用真实API
       response = client.post("/api/v1/hotspots/fetch?platform=douyin")
       assert response.status_code == 200
       
       # 等待任务完成
       # 验证真实数据
   ```

#### 11.2 LLM调用全拟真

**实现步骤**：

1. **移除所有LLM Mock**
   ```python
   # backend/tests/e2e/test_complete_workflow_e2e.py
   @pytest.mark.asyncio
   async def test_complete_workflow_with_real_llm(self, client, db_session):
       """完整业务流程E2E测试（使用真实LLM）"""
       
       # 移除所有DeepSeek Mock
       # 直接调用真实API
       
       # 1. 创建商品
       product_data = {...}
       response = client.post("/api/v1/products", json=product_data)
       product_id = response.json()["id"]
       
       # 2. 抓取热点（可能Mock，取决于TrendRadar风险）
       # ...
       
       # 3. 生成脚本（使用真实DeepSeek API）
       script_request = {
           "hotspot_id": hotspot_id,
           "product_id": product_id,
           "duration": 10
       }
       
       # 不再Mock，等待真实API响应
       response = client.post("/api/v1/scripts/generate", json=script_request)
       assert response.status_code == 200
       
       # 等待异步任务完成
       task_id = response.json()["task_id"]
       # 轮询任务状态，等待完成
       
       # 验证真实生成的脚本
       script = get_script_by_task_id(task_id)
       assert script is not None
       assert len(script.script_content) > 0
   ```

2. **添加测试环境配置**
   ```python
   # backend/tests/conftest.py
   import pytest
   import os
   
   @pytest.fixture(scope="session")
   def llm_config():
       """LLM配置检查"""
       api_key = os.getenv("DEEPSEEK_API_KEY")
       if not api_key:
           pytest.skip("DEEPSEEK_API_KEY未配置，跳过LLM测试")
       return {"api_key": api_key}
   ```

3. **处理异步任务等待**
   ```python
   # backend/tests/utils/task_waiter.py
   import time
   from celery.result import AsyncResult
   from app.celery_app import celery_app
   
   def wait_for_task(task_id, timeout=300):
       """等待Celery任务完成"""
       result = AsyncResult(task_id, app=celery_app)
       
       start_time = time.time()
       while not result.ready():
           if time.time() - start_time > timeout:
               raise TimeoutError(f"任务超时: {task_id}")
           time.sleep(2)
       
       if result.failed():
           raise Exception(f"任务失败: {result.info}")
       
       return result.get()
   ```

#### 11.3 测试环境配置

**需要添加的环境变量**：
```bash
# .env.test
# TrendRadar配置（如果允许真实调用）
TRENDRADAR_API_URL=https://api.trendradar.com
TRENDRADAR_API_KEY=test_key_here

# DeepSeek配置（必须真实）
DEEPSEEK_API_KEY=real_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com

# 测试标记
E2E_USE_REAL_APIS=true
TRENDRADAR_RISK_LEVEL=low  # low/medium/high
```

#### 11.4 测试标记和分类

**实现测试标记**：
```python
# backend/tests/e2e/test_e2e_workflow.py
import pytest

@pytest.mark.e2e
@pytest.mark.real_api  # 标记为真实API测试
@pytest.mark.slow      # 标记为慢速测试
async def test_e2e_with_real_apis(self, client, db_session):
    """使用真实API的E2E测试"""
    pass

@pytest.mark.e2e
@pytest.mark.mock_api  # 标记为Mock API测试
async def test_e2e_with_mock_apis(self, client, db_session):
    """使用Mock API的快速测试"""
    pass
```

**运行测试**：
```bash
# 运行所有E2E测试（包括真实API）
pytest tests/e2e/ -m e2e

# 只运行真实API测试
pytest tests/e2e/ -m "e2e and real_api"

# 只运行Mock测试（快速）
pytest tests/e2e/ -m "e2e and mock_api"
```

---

## 12. Agents架构设计

### 📝 需求描述

**重构目标**：
- 引入Agents架构，将AI功能模块化
- 为以下功能设计专门的Agents：
  1. **视频拆解Agent** - 负责视频内容分析和拆解
  2. **脚本分析Agent** - 负责脚本质量分析和优化建议
  3. **热度分析Agent** - 负责热点热度趋势分析
  4. **关联度分析Agent** - 负责热点与商品/直播间的关联度计算
  5. **脚本生成Agent** - 负责基于多源信息生成脚本

**架构优势**：
- 模块化设计，每个Agent专注单一职责
- 易于扩展和维护
- 支持Agent之间的协作
- 可以独立测试和优化每个Agent

### 🔍 当前架构分析

**当前实现**：
- 所有AI功能直接调用LLM，没有Agent抽象
- 文件：`backend/app/services/script/service.py` - 脚本生成
- 文件：`backend/app/services/analysis/service.py` - 视频拆解
- 文件：`backend/app/services/hotspot/service.py` - 热点分析

**问题**：
- 代码耦合度高
- 难以独立测试和优化
- 缺乏统一的Agent接口

### ✅ 匹配方案

#### 12.1 Agents架构设计

**技术选型**：
- **LangChain** - Agents框架
- **LangGraph** - Agent工作流编排（可选）

**目录结构**：
```
backend/app/
├── agents/
│   ├── __init__.py
│   ├── base.py              # Agent基类
│   ├── video_analysis_agent.py
│   ├── script_analysis_agent.py
│   ├── heat_analysis_agent.py
│   ├── relevance_analysis_agent.py
│   └── script_generation_agent.py
├── tools/                   # Agent工具
│   ├── __init__.py
│   ├── video_tools.py
│   ├── analysis_tools.py
│   └── database_tools.py
```

#### 12.2 Agent基类设计

**实现步骤**：

1. **创建Agent基类**
   ```python
   # backend/app/agents/base.py
   from abc import ABC, abstractmethod
   from langchain.agents import create_agent
   from langchain.tools import tool
   from typing import Dict, Any, List
   from app.utils.deepseek import DeepSeekClient
   
   class BaseAgent(ABC):
       """Agent基类"""
       
       def __init__(self, model_name: str = "deepseek-chat"):
           self.model_name = model_name
           self.llm_client = DeepSeekClient()
           self.tools = self._init_tools()
           self.agent = self._create_agent()
       
       @abstractmethod
       def _init_tools(self) -> List:
           """初始化Agent工具"""
           pass
       
       @abstractmethod
       def _get_system_prompt(self) -> str:
           """获取系统提示词"""
           pass
       
       def _create_agent(self):
           """创建LangChain Agent"""
           from langchain.chat_models import init_chat_model
           
           model = init_chat_model(f"deepseek:{self.model_name}")
           
           return create_agent(
               model,
               tools=self.tools,
               system_prompt=self._get_system_prompt()
           )
       
       @abstractmethod
       async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           """执行Agent任务"""
           pass
   ```

#### 12.3 视频拆解Agent

**实现步骤**：

1. **创建视频拆解Agent**
   ```python
   # backend/app/agents/video_analysis_agent.py
   from app.agents.base import BaseAgent
   from langchain.tools import tool
   from typing import Dict, Any, List
   
   @tool
   def analyze_video_structure(video_url: str) -> Dict[str, Any]:
       """分析视频结构，提取镜头信息"""
       # 调用视频拆解工具API
       from app.utils.video_analyzer import VideoAnalyzerClient
       client = VideoAnalyzerClient()
       return client.analyze(video_url)
   
   @tool
   def extract_golden_3s(video_data: Dict[str, Any]) -> Dict[str, Any]:
       """提取黄金3秒信息"""
       # 分析视频开头3秒
       # ...
       pass
   
   class VideoAnalysisAgent(BaseAgent):
       """视频拆解Agent"""
       
       def _init_tools(self) -> List:
           return [
               analyze_video_structure,
               extract_golden_3s,
           ]
       
       def _get_system_prompt(self) -> str:
           return """你是一位专业的视频分析专家，擅长拆解短视频的结构和技巧。
           你需要：
           1. 分析视频的镜头结构
           2. 提取黄金3秒的钩子技巧
           3. 识别爆款公式和技巧
           4. 提供制作要点建议"""
       
       async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           """执行视频拆解"""
           video_url = input_data.get("video_url")
           
           result = self.agent.invoke({
               "messages": [{
                   "role": "user",
                   "content": f"请分析这个视频：{video_url}"
               }]
           })
           
           return {
               "status": "success",
               "analysis": result["messages"][-1].content
           }
   ```

#### 12.4 关联度分析Agent

**实现步骤**：

1. **创建关联度分析Agent**
   ```python
   # backend/app/agents/relevance_analysis_agent.py
   from app.agents.base import BaseAgent
   from langchain.tools import tool
   from typing import Dict, Any, List
   
   @tool
   def calculate_semantic_similarity(text1: str, text2: str) -> float:
       """计算语义相似度"""
       from app.utils.embedding import EmbeddingClient
       client = EmbeddingClient()
       return client.calculate_semantic_similarity(text1, text2)
   
   @tool
   def analyze_sentiment(text: str) -> Dict[str, Any]:
       """分析情感倾向"""
       from app.utils.sentiment import SentimentClient
       client = SentimentClient()
       return client.analyze_sentiment(text)
   
   class RelevanceAnalysisAgent(BaseAgent):
       """关联度分析Agent"""
       
       def _init_tools(self) -> List:
           return [
               calculate_semantic_similarity,
               analyze_sentiment,
           ]
       
       def _get_system_prompt(self) -> str:
           return """你是一位数据分析专家，擅长分析内容之间的关联度。
           你需要：
           1. 计算热点与商品的语义相似度
           2. 分析情感匹配度
           3. 综合计算匹配度分数
           4. 提供匹配度解释"""
       
       async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           """执行关联度分析"""
           hotspot_text = input_data.get("hotspot_text")
           product_text = input_data.get("product_text")
           
           result = self.agent.invoke({
               "messages": [{
                   "role": "user",
                   "content": f"请分析以下内容的关联度：\n热点：{hotspot_text}\n商品：{product_text}"
               }]
           })
           
           return {
               "status": "success",
               "relevance_score": 0.85,  # 从结果中提取
               "analysis": result["messages"][-1].content
           }
   ```

#### 12.5 脚本生成Agent

**实现步骤**：

1. **创建脚本生成Agent**
   ```python
   # backend/app/agents/script_generation_agent.py
   from app.agents.base import BaseAgent
   from langchain.tools import tool
   from typing import Dict, Any, List
   
   @tool
   def get_hotspot_info(hotspot_id: str) -> Dict[str, Any]:
       """获取热点信息"""
       from app.core.database import SessionLocal
       from app.models.hotspot import Hotspot
       db = SessionLocal()
       hotspot = db.query(Hotspot).filter(Hotspot.id == hotspot_id).first()
       return {
           "title": hotspot.title,
           "tags": hotspot.tags,
           "url": hotspot.url
       }
   
   @tool
   def get_product_info(product_id: str) -> Dict[str, Any]:
       """获取商品信息"""
       # ...
       pass
   
   class ScriptGenerationAgent(BaseAgent):
       """脚本生成Agent"""
       
       def _init_tools(self) -> List:
           return [
               get_hotspot_info,
               get_product_info,
           ]
       
       def _get_system_prompt(self) -> str:
           return """你是一位资深短视频编导，擅长创作引流短视频脚本。
           你需要：
           1. 结合热点话题和商品特性
           2. 运用爆款技巧和公式
           3. 生成高质量的拍摄脚本和分镜
           4. 提供制作要点建议"""
       
       async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           """执行脚本生成"""
           hotspot_id = input_data.get("hotspot_id")
           product_id = input_data.get("product_id")
           duration = input_data.get("duration", 10)
           
           result = self.agent.invoke({
               "messages": [{
                   "role": "user",
                   "content": f"请为以下热点和商品生成一个{duration}秒的脚本：\n热点ID：{hotspot_id}\n商品ID：{product_id}"
               }]
           })
           
           return {
               "status": "success",
               "script": result["messages"][-1].content
           }
   ```

#### 12.6 服务层改造

**修改现有服务，使用Agents**：

```python
# backend/app/services/script/service.py
from app.agents.script_generation_agent import ScriptGenerationAgent

class ScriptGeneratorService:
    """脚本生成服务（使用Agent）"""
    
    def __init__(self):
        self.script_agent = ScriptGenerationAgent()
    
    async def generate_script(
        self,
        hotspot: Hotspot,
        product: Product,
        analysis_report: Optional[AnalysisReport] = None,
        duration: int = 10
    ) -> Dict[str, Any]:
        """生成脚本（使用Agent）"""
        result = await self.script_agent.execute({
            "hotspot_id": hotspot.id,
            "product_id": product.id,
            "analysis_report_id": analysis_report.id if analysis_report else None,
            "duration": duration
        })
        
        # 解析Agent返回的结果
        return self.parse_agent_response(result)
```

#### 12.7 依赖安装

**添加LangChain依赖**：
```bash
# backend/requirements.txt
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.20
```

#### 12.8 Agents协作示例

**多个Agents协作**：
```python
# backend/app/services/hotspot/service.py
from app.agents.relevance_analysis_agent import RelevanceAnalysisAgent
from app.agents.heat_analysis_agent import HeatAnalysisAgent

class HotspotMonitorService:
    """热点监控服务（使用Agents）"""
    
    def __init__(self):
        self.relevance_agent = RelevanceAnalysisAgent()
        self.heat_agent = HeatAnalysisAgent()
    
    async def analyze_hotspot(self, hotspot: Hotspot, product: Product):
        """分析热点（使用多个Agents）"""
        # 1. 使用关联度分析Agent
        relevance_result = await self.relevance_agent.execute({
            "hotspot_text": hotspot.title,
            "product_text": product.name
        })
        
        # 2. 使用热度分析Agent
        heat_result = await self.heat_agent.execute({
            "heat_score": hotspot.heat_score,
            "heat_growth_rate": hotspot.heat_growth_rate
        })
        
        # 3. 综合结果
        return {
            "relevance": relevance_result,
            "heat_analysis": heat_result
        }
```

---

## 13. 实现优先级更新

### 🔥 新增高优先级任务

1. **E2E测试拟真化**（第11节）
   - 影响测试质量，需要优先完成
   - 预计工作量：3-4天

2. **Agents架构设计**（第12节）
   - 影响系统架构，需要优先设计
   - 预计工作量：5-7天

### ⚡ 中优先级任务

3. **前端布局重构**（第5节）
   - 影响用户体验
   - 预计工作量：2-3天

4. **直播间Tab切换**（第1节）
   - 核心交互改进
   - 预计工作量：1天

---

## 14. 技术栈更新

### 新增技术栈

- **LangChain** - Agents框架
- **LangGraph** - Agent工作流编排（可选）

### 相关文档

- LangChain Agents: https://docs.langchain.com/oss/python/langchain/agents
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- LangGraph: https://docs.langchain.com/oss/python/langgraph

---

**最后更新**：2024年12月

