# Figma 设计实施指南

## 快速开始

基于分析文档，本指南提供具体的实施步骤和代码示例。

## 第一步：应用基础样式（30分钟）

### 1.1 创建设计变量文件

创建 `frontend/src/styles/design-tokens.css`：

```css
:root {
  /* 渐变背景 */
  --gradient-bg: linear-gradient(to bottom right, #fdf2f8, #ffffff, #fff7ed);
  
  /* 玻璃态效果 */
  --glass-bg: rgba(255, 255, 255, 0.85);
  --glass-blur: blur(20px);
  
  /* 渐变按钮 */
  --gradient-button: linear-gradient(to right, #f472b6, #fb923c);
  --gradient-button-hover: linear-gradient(to right, #ec4899, #f97316);
  
  /* 圆角 */
  --radius-3xl: 1.5rem;
  --radius-2xl: 1rem;
  --radius-xl: 0.75rem;
  
  /* 阴影 */
  --shadow-pink: 0 10px 15px -3px rgba(244, 114, 182, 0.2);
  --shadow-pink-lg: 0 20px 25px -5px rgba(244, 114, 182, 0.3);
  --shadow-card: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  
  /* Pantone 暖色调（用于图表） */
  --pantone-warm-1: rgba(255, 111, 97, 0.6);
  --pantone-warm-2: rgba(255, 158, 121, 0.6);
  --pantone-warm-3: rgba(255, 192, 120, 0.6);
  --pantone-warm-4: rgba(255, 214, 122, 0.6);
  --pantone-warm-5: rgba(247, 127, 127, 0.6);
  --pantone-warm-6: rgba(230, 126, 161, 0.6);
  --pantone-warm-7: rgba(218, 142, 204, 0.6);
}

/* 玻璃态效果类 */
.glass {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.7);
}

.glass-strong {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.85);
}

/* 渐变按钮类 */
.gradient-button {
  background: var(--gradient-button);
  border: none;
  color: white;
  box-shadow: var(--shadow-pink);
  transition: all 0.2s;
}

.gradient-button:hover {
  background: var(--gradient-button-hover);
  box-shadow: var(--shadow-pink-lg);
  transform: translateY(-1px);
}

/* 设计卡片类 */
.design-card {
  border-radius: var(--radius-3xl);
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(0, 0, 0, 0.05);
  background: white;
}
```

### 1.2 在 main.ts 中引入

```typescript
// frontend/src/main.ts
import './styles/design-tokens.css'
```

### 1.3 更新 App.vue

```vue
<template>
  <div class="app-container">
    <!-- 现有内容 -->
  </div>
</template>

<style scoped>
.app-container {
  background: var(--gradient-bg);
  min-height: 100vh;
}

.app-header {
  backdrop-filter: var(--glass-blur);
  background: var(--glass-bg);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
```

## 第二步：优化 Header 组件（1小时）

### 2.1 更新 App.vue 的 Header 部分

```vue
<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header glass-strong">
      <div class="header-content">
        <div class="logo-section">
          <h1 class="logo">Action</h1>
          <p class="slogan">抓取全网热点，创意脚本生成</p>
        </div>
        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          class="header-menu"
          router
        >
          <!-- 现有菜单项 -->
        </el-menu>
        <div class="header-actions">
          <el-button 
            circle 
            @click="settingsVisible = true"
            class="settings-btn"
            :icon="Setting"
          />
        </div>
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

<style scoped>
.logo-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.logo {
  margin: 0;
  font-size: 32px;
  font-weight: 500;
  letter-spacing: -0.025em;
  color: #030213;
}

.slogan {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
}

.app-header {
  padding: 24px 32px;
  height: auto;
  min-height: 80px;
}
</style>
```

## 第三步：优化热点监控页面（2小时）

### 3.1 更新 HotspotsView.vue

```vue
<template>
  <div class="hotspots-fullscreen">
    <!-- Tab 切换直播间 -->
    <div class="live-room-tabs-container glass-strong">
      <div class="tabs-header">
        <h3 class="tabs-title">直播间选择</h3>
        <el-button 
          type="primary" 
          @click="handleFetchHotspots" 
          :loading="fetching"
          class="gradient-button"
        >
          <el-icon><Refresh /></el-icon>
          抓取热点
        </el-button>
      </div>
      
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
    </div>
    
    <!-- 气泡图（铺满剩余空间） -->
    <div class="bubble-chart-container design-card">
      <h3 class="chart-title">热点分布气泡图</h3>
      <HotspotBubbleChart 
        v-if="visualizationData" 
        :data="visualizationData"
        @bubble-click="handleBubbleClick"
      />
    </div>
    
    <!-- 商品选择对话框 -->
    <ProductSelectionDialog
      v-model="productDialogVisible"
      :hotspot="selectedHotspot"
      @script-generated="handleScriptGenerated"
    />
  </div>
</template>

<style scoped>
.hotspots-fullscreen {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 32px;
  gap: 24px;
}

.live-room-tabs-container {
  padding: 24px 32px;
  border-radius: var(--radius-3xl);
  margin-bottom: 0;
}

.tabs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tabs-title {
  font-size: 20px;
  font-weight: 500;
  color: #030213;
}

.bubble-chart-container {
  flex: 1;
  padding: 32px;
  min-height: 500px;
}

.chart-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 24px;
  color: #030213;
}
</style>
```

### 3.2 更新 HotspotBubbleChart.vue 的配色

```typescript
// 在组件中使用设计配色
const chartColors = [
  'rgba(255, 111, 97, 0.6)',   // Living Coral
  'rgba(255, 158, 121, 0.6)',  // Peach
  'rgba(255, 192, 120, 0.6)',  // Apricot
  'rgba(255, 214, 122, 0.6)',  // Yellow
  'rgba(247, 127, 127, 0.6)',  // Salmon
  'rgba(230, 126, 161, 0.6)',  // Pink
  'rgba(218, 142, 204, 0.6)',  // Orchid
]
```

## 第四步：优化商品管理页面（1.5小时）

### 4.1 更新 ProductsView.vue

```vue
<template>
  <div class="products-page">
    <div class="page-header design-card">
      <h2 class="page-title">商品管理</h2>
      <el-button 
        type="primary" 
        @click="handleSelectHotspot"
        class="gradient-button"
      >
        <el-icon><Plus /></el-icon>
        选择热点生成脚本
      </el-button>
    </div>
    
    <!-- 商品列表 -->
    <div class="products-list design-card">
      <!-- 现有商品列表 -->
    </div>
  </div>
</template>

<style scoped>
.products-page {
  padding: 32px;
  max-width: 1280px;
  margin: 0 auto;
}

.page-header {
  padding: 24px 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 500;
  color: #030213;
}

.products-list {
  padding: 24px;
}
</style>
```

## 第五步：优化脚本管理页面（1.5小时）

### 5.1 更新 ScriptsView.vue

```vue
<template>
  <div class="scripts-page">
    <div class="page-header design-card">
      <h2 class="page-title">脚本管理</h2>
    </div>
    
    <!-- 脚本列表 -->
    <div class="scripts-list design-card">
      <el-table :data="scripts" class="design-table">
        <!-- 表格列 -->
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.scripts-page {
  padding: 32px;
  max-width: 1280px;
  margin: 0 auto;
}

.design-table {
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.design-table :deep(.el-table__header) {
  background: linear-gradient(to right, #fdf2f8, #fff7ed);
}

.design-table :deep(.el-table__row:hover) {
  background: rgba(249, 250, 251, 0.5);
}
</style>
```

## 第六步：优化按钮和状态标签（1小时）

### 6.1 创建通用按钮组件（可选）

```vue
<!-- frontend/src/components/DesignButton.vue -->
<template>
  <el-button
    :type="type"
    :class="['design-button', { 'gradient-button': gradient }]"
    v-bind="$attrs"
  >
    <slot />
  </el-button>
</template>

<script setup lang="ts">
defineProps<{
  type?: string
  gradient?: boolean
}>()
</script>

<style scoped>
.design-button {
  border-radius: var(--radius-xl);
  font-weight: 500;
  transition: all 0.2s;
}

.design-button.gradient-button {
  background: var(--gradient-button);
  border: none;
  color: white;
  box-shadow: var(--shadow-pink);
}

.design-button.gradient-button:hover {
  background: var(--gradient-button-hover);
  box-shadow: var(--shadow-pink-lg);
  transform: translateY(-1px);
}
</style>
```

### 6.2 优化状态标签

```vue
<style scoped>
.status-badge {
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-processing {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}
</style>
```

## 实施检查清单

### 基础样式
- [ ] 创建 `design-tokens.css` 文件
- [ ] 在 `main.ts` 中引入设计变量
- [ ] 更新 `App.vue` 应用渐变背景
- [ ] 更新 `App.vue` Header 应用玻璃态效果

### 组件优化
- [ ] 更新 `HotspotsView.vue` 应用设计样式
- [ ] 更新 `ProductsView.vue` 应用设计样式
- [ ] 更新 `ScriptsView.vue` 应用设计样式
- [ ] 更新图表配色方案

### 细节优化
- [ ] 优化按钮样式（渐变按钮）
- [ ] 优化状态标签样式
- [ ] 添加过渡动画
- [ ] 优化卡片样式（大圆角）

### 测试验证
- [ ] 测试所有页面显示正常
- [ ] 测试响应式布局
- [ ] 测试交互功能
- [ ] 验证视觉效果

## 预期效果

改造完成后，预期效果：

1. **视觉提升**：
   - ✅ 渐变背景（粉色→白色→橙色）
   - ✅ 玻璃态效果（Header）
   - ✅ 大圆角卡片（1.5rem）
   - ✅ 渐变按钮（粉色→橙色）

2. **用户体验**：
   - ✅ 更清晰的视觉层次
   - ✅ 更友好的交互反馈
   - ✅ 更统一的设计语言

3. **功能保持**：
   - ✅ 所有功能正常
   - ✅ 性能不受影响
   - ✅ 兼容性良好

## 注意事项

1. **保持功能完整性**：改造过程中确保所有功能正常工作
2. **渐进式改造**：可以分阶段实施，逐步优化
3. **测试验证**：每个阶段完成后进行测试
4. **性能考虑**：玻璃态效果可能影响性能，注意优化

## 参考资源

- [Figma 设计文件](https://www.figma.com/design/7lEcNHZT8q6sb4q039NCPR/Action-Web-App-Design)
- [设计分析文档](./FIGMA_DESIGN_ANALYSIS.md)
- [Element Plus 主题定制](https://element-plus.org/zh-CN/guide/theming.html)

