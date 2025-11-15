<template>
  <div class="hotspots-fullscreen">
    <!-- Tab 切换直播间 -->
    <div class="live-room-tabs-container design-card glass-strong">
      <div class="tabs-header">
        <h3 class="tabs-title">直播间选择</h3>
        <div class="header-buttons">
          <el-button 
            type="default" 
            @click="handleViewHotspots"
            class="view-hotspots-button"
          >
            <el-icon><DataAnalysis /></el-icon>
            查看已有热点
          </el-button>
          <el-button 
            type="primary" 
            @click="handleFetchHotspots" 
            :loading="fetching"
            :disabled="fetching"
            class="gradient-button"
          >
            <el-icon><Refresh /></el-icon>
            抓取热点
          </el-button>
        </div>
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
      
      <!-- 任务进度提示 - 使用设计语言 -->
      <div v-if="currentTaskId || fetching" class="task-progress-card glass-strong">
        <div class="task-progress-content">
          <div class="task-status-header">
            <div class="task-status-left">
              <div class="task-status-icon-wrapper">
                <el-icon v-if="fetching || taskProgress.status === 'active'" class="spinning-icon">
                  <Loading />
                </el-icon>
                <el-icon v-else-if="taskProgress.status === 'success'" class="success-icon">
                  <CircleCheck />
                </el-icon>
                <el-icon v-else-if="taskProgress.status === 'exception'" class="error-icon">
                  <CircleClose />
                </el-icon>
              </div>
              <span class="task-status-text">{{ taskStatusText }}</span>
            </div>
          </div>
          
          <!-- 自定义进度条 -->
          <div class="custom-progress-wrapper">
            <div class="custom-progress-track">
              <div 
                class="custom-progress-bar"
                :class="{
                  'progress-indeterminate': fetching && taskProgress.percentage === 0,
                  'progress-success': taskProgress.status === 'success',
                  'progress-error': taskProgress.status === 'exception'
                }"
                :style="{
                  width: taskProgress.percentage > 0 ? `${taskProgress.percentage}%` : '100%'
                }"
              ></div>
            </div>
          </div>
          
          <div v-if="taskProgress.detail" class="task-detail">{{ taskProgress.detail }}</div>
        </div>
      </div>
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
    
    <!-- 查看已有热点对话框 -->
    <el-dialog
      v-model="hotspotsListVisible"
      title="已有热点列表"
      width="90%"
      :close-on-click-modal="false"
      class="hotspots-list-dialog"
    >
      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form" style="margin-bottom: 20px;">
        <el-form-item label="平台">
          <el-select v-model="hotspotsFilters.platform" placeholder="选择平台" clearable style="width: 150px;">
            <el-option label="抖音" value="douyin" />
            <el-option label="微博" value="weibo" />
            <el-option label="知乎" value="zhihu" />
            <el-option label="B站" value="bilibili" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="hotspotsFilters.startDate"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="hotspotsFilters.endDate"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHotspotsList">查询</el-button>
          <el-button @click="resetHotspotsFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 热点列表 -->
      <el-table
        :data="hotspotsList"
        v-loading="hotspotsListLoading"
        stripe
        max-height="600"
        style="width: 100%"
      >
        <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformTagType(row.platform)">
              {{ getPlatformName(row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="heat_score" label="热度" width="80" sortable />
        <el-table-column prop="match_score" label="匹配度" width="100" sortable>
          <template #default="{ row }">
            {{ row.match_score ? (row.match_score * 100).toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="抓取时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewHotspotDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="hotspotsPagination.page"
        v-model:page-size="hotspotsPagination.pageSize"
        :total="hotspotsPagination.total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadHotspotsList"
        @current-change="loadHotspotsList"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-dialog>
    
    <!-- 热点详情对话框 -->
    <el-dialog
      v-model="hotspotDetailVisible"
      :title="selectedHotspotDetail?.title || '热点详情'"
      width="80%"
      class="hotspot-detail-dialog"
    >
      <div v-if="selectedHotspotDetail" class="hotspot-detail-content">
        <!-- 基本信息 -->
        <el-card class="detail-section" shadow="never">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          <div class="detail-item">
            <span class="detail-label">标题：</span>
            <span class="detail-value">{{ selectedHotspotDetail.title }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">URL：</span>
            <a :href="selectedHotspotDetail.url" target="_blank" class="detail-link">{{ selectedHotspotDetail.url }}</a>
          </div>
          <div class="detail-item">
            <span class="detail-label">平台：</span>
            <el-tag :type="getPlatformTagType(selectedHotspotDetail.platform)">
              {{ getPlatformName(selectedHotspotDetail.platform) }}
            </el-tag>
          </div>
          <div class="detail-item">
            <span class="detail-label">热度：</span>
            <span class="detail-value">{{ selectedHotspotDetail.heat_score || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">匹配度：</span>
            <span class="detail-value">{{ selectedHotspotDetail.match_score ? (selectedHotspotDetail.match_score * 100).toFixed(1) + '%' : '-' }}</span>
          </div>
          <div class="detail-item" v-if="selectedHotspotDetail.tags && selectedHotspotDetail.tags.length > 0">
            <span class="detail-label">标签：</span>
            <el-tag v-for="tag in selectedHotspotDetail.tags" :key="tag" style="margin-right: 8px;">{{ tag }}</el-tag>
          </div>
          <div class="detail-item">
            <span class="detail-label">抓取时间：</span>
            <span class="detail-value">{{ formatDateTime(selectedHotspotDetail.created_at) }}</span>
          </div>
        </el-card>
        
        <!-- ContentStructureAgent输出 -->
        <el-card v-if="selectedHotspotDetail.video_structure" class="detail-section" shadow="never">
          <template #header>
            <span class="section-title">ContentStructureAgent 输出</span>
          </template>
          <div class="agent-output">
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.duration !== undefined">
              <span class="detail-label">视频时长：</span>
              <span class="detail-value">{{ selectedHotspotDetail.video_structure.duration }}秒</span>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.scenes">
              <span class="detail-label">场景数：</span>
              <span class="detail-value">{{ selectedHotspotDetail.video_structure.scenes.length }}</span>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.key_frames">
              <span class="detail-label">关键帧数：</span>
              <span class="detail-value">{{ selectedHotspotDetail.video_structure.key_frames.length }}</span>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.tags && selectedHotspotDetail.video_structure.tags.length > 0">
              <span class="detail-label">标签：</span>
              <el-tag v-for="tag in selectedHotspotDetail.video_structure.tags" :key="tag" style="margin-right: 8px;">{{ tag }}</el-tag>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.transcript">
              <span class="detail-label">转录文本：</span>
              <div class="detail-text">{{ selectedHotspotDetail.video_structure.transcript }}</div>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.visual_elements">
              <span class="detail-label">视觉元素：</span>
              <div class="detail-visual-elements">
                <div v-if="selectedHotspotDetail.video_structure.visual_elements.characters && selectedHotspotDetail.video_structure.visual_elements.characters.length > 0">
                  <strong>人物：</strong>
                  <el-tag v-for="char in selectedHotspotDetail.video_structure.visual_elements.characters" :key="char" style="margin-right: 8px; margin-bottom: 4px;">{{ char }}</el-tag>
                </div>
                <div v-if="selectedHotspotDetail.video_structure.visual_elements.objects && selectedHotspotDetail.video_structure.visual_elements.objects.length > 0" style="margin-top: 8px;">
                  <strong>物品：</strong>
                  <el-tag v-for="obj in selectedHotspotDetail.video_structure.visual_elements.objects" :key="obj" style="margin-right: 8px; margin-bottom: 4px;">{{ obj }}</el-tag>
                </div>
                <div v-if="selectedHotspotDetail.video_structure.visual_elements.background" style="margin-top: 8px;">
                  <strong>背景：</strong>
                  <span class="detail-value">{{ selectedHotspotDetail.video_structure.visual_elements.background }}</span>
                </div>
              </div>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.video_structure.audio_elements">
              <span class="detail-label">音频元素：</span>
              <div class="detail-audio-elements">
                <div v-if="selectedHotspotDetail.video_structure.audio_elements.music" style="margin-bottom: 8px;">
                  <strong>音乐：</strong>
                  <span class="detail-value">{{ selectedHotspotDetail.video_structure.audio_elements.music }}</span>
                </div>
                <div v-if="selectedHotspotDetail.video_structure.audio_elements.voiceover" style="margin-bottom: 8px;">
                  <strong>旁白：</strong>
                  <span class="detail-value">{{ selectedHotspotDetail.video_structure.audio_elements.voiceover }}</span>
                </div>
                <div v-if="selectedHotspotDetail.video_structure.audio_elements.sound_effects && selectedHotspotDetail.video_structure.audio_elements.sound_effects.length > 0">
                  <strong>音效：</strong>
                  <el-tag v-for="effect in selectedHotspotDetail.video_structure.audio_elements.sound_effects" :key="effect" style="margin-right: 8px; margin-bottom: 4px;">{{ effect }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- ContentAnalysisAgent输出 -->
        <el-card v-if="selectedHotspotDetail.content_analysis" class="detail-section" shadow="never">
          <template #header>
            <span class="section-title">ContentAnalysisAgent 输出</span>
          </template>
          <div class="agent-output">
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.summary">
              <span class="detail-label">内容摘要：</span>
              <div class="detail-text">{{ selectedHotspotDetail.content_analysis.summary }}</div>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.style">
              <span class="detail-label">视频风格：</span>
              <span class="detail-value">{{ selectedHotspotDetail.content_analysis.style }}</span>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.ecommerce_fit">
              <span class="detail-label">电商适配性评分：</span>
              <span class="detail-value">{{ selectedHotspotDetail.content_analysis.ecommerce_fit.score ? (selectedHotspotDetail.content_analysis.ecommerce_fit.score * 100).toFixed(1) + '%' : '-' }}</span>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.ecommerce_fit?.reasoning">
              <span class="detail-label">适配性原因：</span>
              <div class="detail-text">{{ selectedHotspotDetail.content_analysis.ecommerce_fit.reasoning }}</div>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.ecommerce_fit?.applicable_categories">
              <span class="detail-label">适用类目：</span>
              <el-tag v-for="cat in selectedHotspotDetail.content_analysis.ecommerce_fit.applicable_categories" :key="cat" style="margin-right: 8px;">{{ cat }}</el-tag>
            </div>
            <div class="detail-item" v-if="selectedHotspotDetail.content_analysis.script_structure">
              <span class="detail-label">脚本结构：</span>
              <div class="detail-script-structure">
                <div v-if="selectedHotspotDetail.content_analysis.script_structure.hook" style="margin-bottom: 12px;">
                  <strong>开头钩子：</strong>
                  <div class="detail-text" style="margin-top: 4px;">{{ selectedHotspotDetail.content_analysis.script_structure.hook }}</div>
                </div>
                <div v-if="selectedHotspotDetail.content_analysis.script_structure.body" style="margin-bottom: 12px;">
                  <strong>主体内容：</strong>
                  <div class="detail-text" style="margin-top: 4px;">{{ selectedHotspotDetail.content_analysis.script_structure.body }}</div>
                </div>
                <div v-if="selectedHotspotDetail.content_analysis.script_structure.cta">
                  <strong>行动号召：</strong>
                  <div class="detail-text" style="margin-top: 4px;">{{ selectedHotspotDetail.content_analysis.script_structure.cta }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 内容摘要 -->
        <el-card v-if="selectedHotspotDetail.content_compact" class="detail-section" shadow="never">
          <template #header>
            <span class="section-title">内容摘要</span>
          </template>
          <div class="detail-text">{{ selectedHotspotDetail.content_compact }}</div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, CircleCheck, CircleClose, DataAnalysis } from '@element-plus/icons-vue'
import { hotspotsApi, type Hotspot } from '@/api/hotspots'
import { liveRoomsApi, type LiveRoom } from '@/api/liveRooms'
import { tasksApi, type TaskStatus } from '@/api/tasks'
import HotspotBubbleChart from '@/components/HotspotBubbleChart.vue'
import ProductSelectionDialog from '@/components/ProductSelectionDialog.vue'

const router = useRouter()

const liveRooms = ref<LiveRoom[]>([])
const activeLiveRoomId = ref<string>('')
const visualizationData = ref<any>(null)
const productDialogVisible = ref(false)
const selectedHotspot = ref<Hotspot | null>(null)
const fetching = ref(false)
const currentTaskId = ref<string | null>(null)
const taskStatus = ref<TaskStatus | null>(null)
let taskPollingInterval: number | null = null

// 查看已有热点相关
const hotspotsListVisible = ref(false)
const hotspotsList = ref<any[]>([])
const hotspotsListLoading = ref(false)
const hotspotsFilters = ref({
  platform: '',
  startDate: '',
  endDate: ''
})
const hotspotsPagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})
const hotspotDetailVisible = ref(false)
const selectedHotspotDetail = ref<any>(null)

const loadLiveRooms = async () => {
  try {
    const response = await liveRoomsApi.getLiveRooms()
    // 过滤掉测试直播间（双重保护，即使数据库中有也过滤掉）
    liveRooms.value = response.items.filter(room => 
      !room.name.includes('测试') && !room.name.toLowerCase().includes('test')
    )
    
    // 默认选择第一个直播间
    if (liveRooms.value.length > 0 && !activeLiveRoomId.value) {
      activeLiveRoomId.value = liveRooms.value[0].id
    }
  } catch (error) {
    console.error('加载直播间失败:', error)
    ElMessage.error('加载直播间失败')
  }
}

const loadVisualizationData = async (liveRoomId?: string) => {
  try {
    // 先清空数据，避免显示上一个直播间的数据
    visualizationData.value = null
    
    const data = await hotspotsApi.getVisualization(liveRoomId)
    visualizationData.value = data
    
    // 如果没有数据，设置为空结构，避免卡在上一个直播间的数据
    if (!data || !data.categories || data.categories.length === 0) {
      visualizationData.value = {
        categories: []
      }
    }
  } catch (error) {
    console.error('加载可视化数据失败:', error)
    ElMessage.error('加载热点数据失败')
    // 确保即使出错也清空数据
    visualizationData.value = {
      categories: []
    }
  }
}

const handleLiveRoomChange = (liveRoomId: string) => {
  // 切换直播间时重新加载数据
  loadVisualizationData(liveRoomId)
}

const handleFetchHotspots = async () => {
  fetching.value = true
  try {
    // 不传platform参数，让后端抓取多个平台（douyin, zhihu, weibo, bilibili）
    const response = await hotspotsApi.fetchHotspots()
    currentTaskId.value = response.task_id
    ElMessage.success('热点抓取任务已启动（多平台）')
    
    // 开始轮询任务状态
    startTaskPolling()
  } catch (error: any) {
    ElMessage.error('触发热点抓取失败: ' + (error.message || '未知错误'))
    fetching.value = false
  }
}

const startTaskPolling = () => {
  if (!currentTaskId.value) return
  
  // 立即查询一次
  checkTaskStatus()
  
  // 每2秒轮询一次
  taskPollingInterval = window.setInterval(() => {
    checkTaskStatus()
  }, 2000)
}

const checkTaskStatus = async () => {
  if (!currentTaskId.value) return
  
  try {
    const status = await tasksApi.getTaskStatus(currentTaskId.value)
    taskStatus.value = status
    
    // 调试日志（减少输出频率）
    // console.log('任务状态:', status)
    
    if (status.state === 'SUCCESS') {
      // 任务完成
      stopTaskPolling()
      fetching.value = false
      ElMessage.success(`热点抓取完成！共抓取 ${status.result?.count || 0} 个热点`)
      
      // 刷新数据（延迟更长时间，确保数据已保存）
      setTimeout(() => {
        loadVisualizationData(activeLiveRoomId.value)
      }, 1000)
      
      // 5秒后清除任务状态（延长显示时间，让用户看到完成状态）
      setTimeout(() => {
        currentTaskId.value = null
        taskStatus.value = null
      }, 5000)
    } else if (status.state === 'FAILURE') {
      // 任务失败
      stopTaskPolling()
      fetching.value = false
      ElMessage.error('热点抓取失败: ' + (status.error || '未知错误'))
      
      // 3秒后清除任务状态
      setTimeout(() => {
        currentTaskId.value = null
        taskStatus.value = null
      }, 3000)
    }
  } catch (error: any) {
    console.error('查询任务状态失败:', error)
    // 如果查询失败，可能是任务不存在或已过期，停止轮询
    if (error.response?.status === 404 || error.message?.includes('404')) {
      stopTaskPolling()
      fetching.value = false
      currentTaskId.value = null
      taskStatus.value = null
    }
  }
}

const stopTaskPolling = () => {
  if (taskPollingInterval !== null) {
    clearInterval(taskPollingInterval)
    taskPollingInterval = null
  }
}

const taskStatusText = computed(() => {
  // 如果正在抓取但还没有任务状态
  if (fetching.value && !taskStatus.value) {
    return '正在启动热点抓取任务...'
  }
  
  if (!taskStatus.value) {
    return '任务启动中...'
  }
  
  // 使用后端返回的status字段，如果没有则根据state生成
  if (taskStatus.value.status) {
    return taskStatus.value.status
  }
  
  switch (taskStatus.value.state) {
    case 'PENDING':
      return '任务等待中...'
    case 'PROGRESS':
    case 'STARTED':
      return taskStatus.value.status || '任务进行中...'
    case 'SUCCESS':
      return `任务完成！共抓取 ${taskStatus.value.result?.count || 0} 个热点`
    case 'FAILURE':
      return '任务失败: ' + (taskStatus.value.error || '未知错误')
    default:
      return `任务状态: ${taskStatus.value.state || '未知'}`
  }
})

const taskAlertType = computed(() => {
  if (!taskStatus.value) return 'info'
  
  switch (taskStatus.value.state) {
    case 'SUCCESS':
      return 'success'
    case 'FAILURE':
      return 'error'
    case 'PROGRESS':
    case 'PENDING':
      return 'info'
    default:
      return 'info'
  }
})

const taskProgress = computed(() => {
  // 如果正在抓取但还没有任务状态，显示不确定进度
  if (fetching.value && !taskStatus.value) {
    return { percentage: 0, status: 'active' as const, detail: '正在启动任务...' }
  }
  
  if (!taskStatus.value) {
    return { percentage: 0, status: 'active' as const, detail: '' }
  }
  
  if (taskStatus.value.state === 'PROGRESS' && taskStatus.value.current !== undefined && taskStatus.value.total) {
    const percentage = Math.round((taskStatus.value.current / taskStatus.value.total) * 100)
    // 优先使用后端返回的详细状态信息
    const detail = taskStatus.value.status || `处理中: ${taskStatus.value.current}/${taskStatus.value.total}`
    return {
      percentage,
      status: 'active' as const,
      detail
    }
  } else if (taskStatus.value.state === 'STARTED' || taskStatus.value.state === 'PENDING') {
    // 任务已启动但还没有进度信息，显示不确定进度
    return {
      percentage: 0,
      status: 'active' as const,
      detail: taskStatus.value.status || '任务已启动，等待处理...'
    }
  } else if (taskStatus.value.state === 'SUCCESS') {
    return {
      percentage: 100,
      status: 'success' as const,
      detail: `完成！共抓取 ${taskStatus.value.result?.count || 0} 个热点`
    }
  } else if (taskStatus.value.state === 'FAILURE') {
    return {
      percentage: 0,
      status: 'exception' as const,
      detail: taskStatus.value.error || '任务失败'
    }
  }
  
  return {
    percentage: 0,
    status: 'active' as const,
    detail: taskStatus.value.status || ''
  }
})

const handleBubbleClick = async (hotspot: any) => {
  // 点击气泡时，打开商品选择对话框
  try {
    const detail = await hotspotsApi.getHotspotDetail(hotspot.id)
    selectedHotspot.value = detail
    productDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取热点详情失败: ' + (error.message || '未知错误'))
  }
}

const handleScriptGenerated = (scriptId: string) => {
  ElMessage.success('脚本生成成功')
  productDialogVisible.value = false
  
  // 跳转到脚本管理页面
  router.push('/scripts')
}

// 查看已有热点
const handleViewHotspots = () => {
  hotspotsListVisible.value = true
  loadHotspotsList()
}

// 加载热点列表
const loadHotspotsList = async () => {
  hotspotsListLoading.value = true
  try {
    const params: any = {
      limit: hotspotsPagination.value.pageSize,
      offset: (hotspotsPagination.value.page - 1) * hotspotsPagination.value.pageSize
    }
    
    if (hotspotsFilters.value.platform) {
      params.platform = hotspotsFilters.value.platform
    }
    
    if (hotspotsFilters.value.startDate) {
      params.start_date = hotspotsFilters.value.startDate
    }
    
    if (hotspotsFilters.value.endDate) {
      params.end_date = hotspotsFilters.value.endDate
    }
    
    const response = await hotspotsApi.getHotspots(params)
    hotspotsList.value = response.items
    hotspotsPagination.value.total = response.total
  } catch (error: any) {
    ElMessage.error('加载热点列表失败: ' + (error.message || '未知错误'))
  } finally {
    hotspotsListLoading.value = false
  }
}

// 重置筛选条件
const resetHotspotsFilters = () => {
  hotspotsFilters.value = {
    platform: '',
    startDate: '',
    endDate: ''
  }
  hotspotsPagination.value.page = 1
  loadHotspotsList()
}

// 查看热点详情
const viewHotspotDetail = async (hotspot: any) => {
  try {
    const detail = await hotspotsApi.getHotspotDetail(hotspot.id)
    selectedHotspotDetail.value = detail
    hotspotDetailVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取热点详情失败: ' + (error.message || '未知错误'))
  }
}

// 平台相关工具函数
const getPlatformName = (platform: string) => {
  const platformMap: Record<string, string> = {
    'douyin': '抖音',
    'weibo': '微博',
    'zhihu': '知乎',
    'bilibili': 'B站'
  }
  return platformMap[platform] || platform
}

const getPlatformTagType = (platform: string) => {
  const typeMap: Record<string, string> = {
    'douyin': 'danger',
    'weibo': 'warning',
    'zhihu': 'success',
    'bilibili': 'info'
  }
  return typeMap[platform] || ''
}

// 格式化时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 监听直播间列表变化，自动选择第一个
watch(liveRooms, (newRooms) => {
  if (newRooms.length > 0 && !activeLiveRoomId.value) {
    activeLiveRoomId.value = newRooms[0].id
  }
})

// 监听选中的直播间，加载对应数据
watch(activeLiveRoomId, (newId) => {
  if (newId) {
    loadVisualizationData(newId)
  }
})

onMounted(() => {
  loadLiveRooms()
})

onBeforeUnmount(() => {
  stopTaskPolling()
})
</script>

<style scoped>
.hotspots-fullscreen {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 32px;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.live-room-tabs-container {
  flex-shrink: 0;
  padding: 24px 32px;
  margin-bottom: 0;
  position: relative;
  z-index: 2;
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
  color: var(--text-primary);
  margin: 0;
}

.live-room-tabs {
  flex: 1;
}

.live-room-tabs :deep(.el-tabs__header) {
  margin: 0;
}

.live-room-tabs :deep(.el-tabs__item) {
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.live-room-tabs :deep(.el-tabs__item:hover) {
  color: var(--text-primary);
}

.live-room-tabs :deep(.el-tabs__item.is-active) {
  color: white;
  background: var(--gradient-button);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-pink);
  position: relative;
  z-index: 1;
}

.live-room-tabs :deep(.el-tabs__active-bar) {
  display: none;
}

/* 任务进度卡片 - 使用设计语言 */
.task-progress-card {
  margin-top: 16px;
  padding: 16px 20px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.task-progress-card:hover {
  box-shadow: var(--shadow-md);
}

.task-progress-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.task-status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.task-status-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.task-status-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.spinning-icon {
  color: #f472b6;
  font-size: 20px;
  animation: rotate 1s linear infinite;
}

.success-icon {
  color: #10b981;
  font-size: 20px;
}

.error-icon {
  color: #ef4444;
  font-size: 20px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.task-status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
}

/* 自定义进度条 - 使用设计语言 */
.custom-progress-wrapper {
  width: 100%;
  margin-top: 4px;
}

.custom-progress-track {
  width: 100%;
  height: 8px;
  background: rgba(244, 114, 182, 0.1);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
}

.custom-progress-bar {
  height: 100%;
  background: var(--gradient-button);
  border-radius: var(--radius-lg);
  transition: width 0.3s ease;
  position: relative;
  box-shadow: 0 2px 4px rgba(244, 114, 182, 0.3);
}

/* 不确定进度条动画 */
.custom-progress-bar.progress-indeterminate {
  width: 30% !important;
  animation: progress-indeterminate 1.5s ease-in-out infinite;
  background: linear-gradient(
    90deg,
    rgba(244, 114, 182, 0.3) 0%,
    var(--gradient-button) 50%,
    rgba(244, 114, 182, 0.3) 100%
  );
  background-size: 200% 100%;
}

@keyframes progress-indeterminate {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.custom-progress-bar.progress-success {
  background: linear-gradient(to right, #10b981, #34d399);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.custom-progress-bar.progress-error {
  background: linear-gradient(to right, #ef4444, #f87171);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.task-detail {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  opacity: 0.8;
  line-height: 1.5;
}

.bubble-chart-container {
  flex: 1;
  overflow: hidden;
  padding: 32px;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.chart-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.empty-chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.header-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.view-hotspots-button {
  margin-right: 0;
}

/* 热点列表对话框样式 */
.hotspots-list-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.filter-form {
  margin-bottom: 20px;
}

/* 热点详情对话框样式 */
.hotspot-detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.hotspot-detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-item {
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 120px;
  flex-shrink: 0;
  margin-right: 8px;
}

.detail-value {
  color: var(--text-primary);
  flex: 1;
}

.detail-link {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
}

.detail-link:hover {
  text-decoration: underline;
}

.detail-text {
  color: var(--text-primary);
  line-height: 1.8;
  word-break: break-word;
  white-space: pre-wrap;
}

.detail-visual-elements,
.detail-audio-elements,
.detail-script-structure {
  flex: 1;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
}

.agent-output {
  padding: 10px 0;
}
</style>
