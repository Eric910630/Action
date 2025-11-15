<template>
  <div class="analysis-view">
    <div class="page-header design-card">
      <h2 class="page-title">拆解与生成</h2>
      <el-button 
        type="primary" 
        @click="handleAnalyze"
        class="gradient-button"
      >
        <el-icon><Plus /></el-icon>
        手动拆解视频
      </el-button>
    </div>
    
    <el-card class="analysis-list design-card">
      <template #header>
        <div class="card-header">
          <span>拆解报告列表</span>
        </div>
      </template>

      <!-- 分析表单 -->
      <el-alert
        title="说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          此页面用于手动上传视频URL进行拆解和模仿脚本生成。热点视频的拆解已自动在后台完成。
        </template>
      </el-alert>
      
      <!-- 拆解任务进度提示 -->
      <div v-if="analyzingVideo || currentAnalysisTaskId" class="analysis-progress-card design-card glass-strong" style="margin-bottom: 20px;">
        <div class="task-progress-content">
          <div class="task-status-header">
            <div class="task-status-left">
              <div class="task-status-icon-wrapper">
                <el-icon v-if="analyzingVideo || analysisTaskStatus?.state === 'PROGRESS' || analysisTaskStatus?.state === 'PENDING'" class="spinning-icon">
                  <Loading />
                </el-icon>
                <el-icon v-else-if="analysisTaskStatus?.state === 'SUCCESS'" class="success-icon">
                  <CircleCheck />
                </el-icon>
                <el-icon v-else-if="analysisTaskStatus?.state === 'FAILURE'" class="error-icon">
                  <CircleClose />
                </el-icon>
              </div>
              <span class="task-status-text">{{ analysisTaskStatusText }}</span>
            </div>
          </div>
          
          <!-- 自定义进度条 -->
          <div class="custom-progress-wrapper">
            <div class="custom-progress-track">
              <div 
                class="custom-progress-bar"
                :class="{
                  'progress-indeterminate': analyzingVideo && (!analysisTaskStatus || analysisTaskStatus.state === 'PENDING'),
                  'progress-success': analysisTaskStatus?.state === 'SUCCESS',
                  'progress-error': analysisTaskStatus?.state === 'FAILURE'
                }"
                :style="{
                  width: analysisTaskStatus?.current && analysisTaskStatus?.total 
                    ? `${Math.round((analysisTaskStatus.current / analysisTaskStatus.total) * 100)}%` 
                    : '100%'
                }"
              ></div>
            </div>
          </div>
          
          <div v-if="analysisTaskStatus?.status" class="task-detail">{{ analysisTaskStatus.status }}</div>
        </div>
      </div>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="视频URL">
          <el-input
            v-model="analyzeForm.video_url"
            placeholder="请输入视频URL（支持抖音、微博等平台）"
            style="width: 500px"
            :disabled="analyzingVideo"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitAnalyze"
            :loading="analyzingVideo"
            :disabled="analyzingVideo"
          >
            拆解视频
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 报告列表 -->
      <el-table :data="reports" v-loading="loading" stripe>
        <el-table-column prop="video_url" label="视频URL" min-width="200">
          <template #default="{ row }">
            <el-link :href="row.video_url" target="_blank">{{ row.video_url }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="video_info.title" label="视频标题" min-width="150">
          <template #default="{ row }">
            {{ row.video_info?.title || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadReports"
        @current-change="loadReports"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="拆解报告详情" width="1000px">
      <div v-if="selectedReport">
        <el-tabs>
          <el-tab-pane label="基本信息">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="视频URL" :span="2">
                <el-link :href="selectedReport.video_url" target="_blank">
                  {{ selectedReport.video_url }}
                </el-link>
              </el-descriptions-item>
              <el-descriptions-item label="视频标题">
                {{ selectedReport.video_info?.title || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ selectedReport.created_at }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          <el-tab-pane label="爆款技巧">
            <el-card v-for="(technique, index) in selectedReport.techniques" :key="index" style="margin-bottom: 10px">
              <template #header>
                <strong>{{ technique.name }}</strong>
                <el-tag size="small" style="margin-left: 10px">{{ technique.type }}</el-tag>
              </template>
              <p>{{ technique.description }}</p>
              <p v-if="technique.reason" style="color: #666; margin-top: 8px">
                <strong>原因：</strong>{{ technique.reason }}
              </p>
            </el-card>
          </el-tab-pane>
          <el-tab-pane label="分镜表格">
            <el-table :data="selectedReport.shot_table" stripe>
              <el-table-column prop="shot_number" label="镜头" width="80" />
              <el-table-column prop="time_range" label="时间" width="100" />
              <el-table-column prop="dialogue" label="台词" min-width="150" />
              <el-table-column prop="content" label="内容" min-width="150" />
              <el-table-column prop="viral_technique" label="爆款技巧" width="150" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="黄金3秒">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="钩子类型">
                {{ selectedReport.golden_3s?.hook_type || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="开头台词">
                {{ selectedReport.golden_3s?.opening_line || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          <el-tab-pane label="爆款公式">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="公式名称">
                {{ selectedReport.viral_formula?.formula_name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="公式结构">
                {{ selectedReport.viral_formula?.formula_structure || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="运用方式">
                {{ selectedReport.viral_formula?.application_method || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { analysisApi, type AnalysisReport } from '@/api/analysis'
import { tasksApi, type TaskStatus } from '@/api/tasks'

const loading = ref(false)
const reports = ref<AnalysisReport[]>([])
const detailVisible = ref(false)
const selectedReport = ref<AnalysisReport | null>(null)

// 拆解任务状态
const analyzingVideo = ref(false) // 是否正在拆解视频
const currentAnalysisTaskId = ref<string | null>(null) // 当前拆解任务ID
const analysisTaskStatus = ref<TaskStatus | null>(null) // 拆解任务状态
let analysisTaskPollingInterval: number | null = null // 任务轮询定时器

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const analyzeForm = ref({
  video_url: ''
})

const loadReports = async () => {
  loading.value = true
  try {
    const response = await analysisApi.getReports({
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    })
    reports.value = response.items
    pagination.value.total = response.total
  } catch (error: any) {
    ElMessage.error('加载报告失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleAnalyze = () => {
  analyzeForm.value.video_url = ''
}

const submitAnalyze = async () => {
  if (!analyzeForm.value.video_url) {
    ElMessage.warning('请输入视频URL')
    return
  }

  try {
    const response = await analysisApi.analyzeVideo(analyzeForm.value.video_url)
    currentAnalysisTaskId.value = response.task_id
    analyzingVideo.value = true
    
    // 开始轮询任务状态
    startAnalysisTaskPolling()
    
    ElMessage.success('视频拆解任务已启动')
    analyzeForm.value.video_url = ''
  } catch (error: any) {
    ElMessage.error('分析视频失败: ' + (error.message || '未知错误'))
    analyzingVideo.value = false
    currentAnalysisTaskId.value = null
  }
}

// 开始轮询拆解任务状态
const startAnalysisTaskPolling = () => {
  if (analysisTaskPollingInterval) {
    clearInterval(analysisTaskPollingInterval)
  }
  
  analysisTaskPollingInterval = window.setInterval(async () => {
    if (!currentAnalysisTaskId.value) {
      stopAnalysisTaskPolling()
      return
    }
    
    try {
      const status = await tasksApi.getTaskStatus(currentAnalysisTaskId.value)
      analysisTaskStatus.value = status
      
      if (status.state === 'SUCCESS') {
        ElMessage.success('视频拆解完成！')
        stopAnalysisTaskPolling()
        analyzingVideo.value = false
        currentAnalysisTaskId.value = null
        analysisTaskStatus.value = null
        
        // 延迟刷新报告列表，确保数据已保存
        setTimeout(async () => {
          // 重置到第一页
          pagination.value.page = 1
          await loadReports()
        }, 1000)
      } else if (status.state === 'FAILURE') {
        ElMessage.error('视频拆解失败: ' + (status.error || '未知错误'))
        stopAnalysisTaskPolling()
        analyzingVideo.value = false
        currentAnalysisTaskId.value = null
        analysisTaskStatus.value = null
      }
    } catch (error) {
      console.error('获取拆解任务状态失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

// 停止轮询拆解任务状态
const stopAnalysisTaskPolling = () => {
  if (analysisTaskPollingInterval) {
    clearInterval(analysisTaskPollingInterval)
    analysisTaskPollingInterval = null
  }
}

// 拆解任务状态文本
const analysisTaskStatusText = computed(() => {
  if (analyzingVideo.value && !analysisTaskStatus.value) {
    return '视频拆解任务已启动...'
  }
  
  if (!analysisTaskStatus.value) {
    return ''
  }
  
  if (analysisTaskStatus.value.status) {
    return analysisTaskStatus.value.status
  }
  
  switch (analysisTaskStatus.value.state) {
    case 'PENDING':
      return '等待拆解...'
    case 'PROGRESS':
      return analysisTaskStatus.value.status || '正在拆解视频...'
    case 'SUCCESS':
      return '视频拆解完成！'
    case 'FAILURE':
      return '视频拆解失败: ' + (analysisTaskStatus.value.error || '未知错误')
    default:
      return `任务状态: ${analysisTaskStatus.value.state || '未知'}`
  }
})

const viewDetail = async (report: AnalysisReport) => {
  try {
    const detail = await analysisApi.getReportDetail(report.id)
    selectedReport.value = detail
    detailVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取详情失败: ' + (error.message || '未知错误'))
  }
}

onMounted(() => {
  loadReports()
})

onBeforeUnmount(() => {
  stopAnalysisTaskPolling()
})
</script>

<style scoped>
.analysis-view {
  height: 100%;
  padding: 32px;
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.analysis-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.analysis-list :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.analysis-list :deep(.el-table) {
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.analysis-list :deep(.el-table__header) {
  background: linear-gradient(to right, #fdf2f8, #fff7ed);
}

.analysis-list :deep(.el-table__row:hover) {
  background: rgba(249, 250, 251, 0.5);
}

/* 拆解任务进度提示样式 */
.analysis-progress-card {
  padding: 16px 20px;
  border-radius: var(--radius-xl);
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

/* 自定义进度条 */
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
  background: linear-gradient(90deg, #f472b6, #ec4899);
  border-radius: var(--radius-lg);
  transition: width 0.3s ease;
}

.progress-indeterminate {
  animation: progress-indeterminate 1.5s ease-in-out infinite;
  width: 100% !important;
}

@keyframes progress-indeterminate {
  0% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(0%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-success {
  background: linear-gradient(90deg, #10b981, #059669);
}

.progress-error {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.task-detail {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}
</style>

