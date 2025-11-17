<template>
  <div class="app-container gradient-bg">
    <!-- 顶部导航栏 -->
    <el-header class="app-header glass-strong">
      <div class="header-content">
        <div class="logo-section">
          <h1 class="logo">Action 1.0</h1>
          <p class="slogan">抓取全网热点，创意脚本生成</p>
        </div>
        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          class="header-menu"
          router
        >
          <el-menu-item index="/hotspots">
            <el-icon><TrendCharts /></el-icon>
            <span>热点监控</span>
          </el-menu-item>
          <el-menu-item index="/products">
            <el-icon><Goods /></el-icon>
            <span>商品管理</span>
          </el-menu-item>
          <el-menu-item index="/analysis">
            <el-icon><VideoPlay /></el-icon>
            <span>拆解与生成</span>
          </el-menu-item>
          <el-menu-item index="/scripts">
            <el-icon><Document /></el-icon>
            <span>脚本管理</span>
          </el-menu-item>
          <el-menu-item index="/feedback">
            <el-icon><ChatLineRound /></el-icon>
            <span>吐槽与期望</span>
          </el-menu-item>
        </el-menu>
        <div class="header-actions">
          <!-- 设置按钮（齿轮图标） -->
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

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Setting, TrendCharts, Goods, VideoPlay, Document, ChatLineRound } from '@element-plus/icons-vue'
import LiveRoomSettingsDialog from '@/components/LiveRoomSettingsDialog.vue'

const route = useRoute()
const settingsVisible = ref(false)

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 24px 32px;
  flex-shrink: 0;
  min-height: 80px;
  height: auto;
  border-bottom: 1px solid var(--border-medium);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 20px;
}

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
  color: var(--text-primary);
  white-space: nowrap;
}

.slogan {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 400;
}

.header-menu {
  flex: 1;
  background: transparent;
  border-bottom: none;
  min-width: 0;
}

.header-menu :deep(.el-menu-item) {
  color: var(--text-primary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.header-menu :deep(.el-menu-item:hover) {
  background: rgba(244, 114, 182, 0.1);
  color: var(--text-primary);
}

.header-menu :deep(.el-menu-item.is-active) {
  color: var(--text-primary);
  border-bottom-color: #f472b6;
  background: rgba(244, 114, 182, 0.05);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-btn {
  background: rgba(244, 114, 182, 0.1);
  border: 1px solid rgba(244, 114, 182, 0.2);
  color: var(--text-primary);
  transition: all 0.2s;
}

.settings-btn:hover {
  background: rgba(244, 114, 182, 0.2);
  border-color: rgba(244, 114, 182, 0.3);
  transform: translateY(-1px);
}

.app-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  background: transparent;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>

