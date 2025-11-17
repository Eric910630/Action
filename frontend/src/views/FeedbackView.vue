<template>
  <div class="feedback-view">
    <div class="page-header design-card">
      <h2 class="page-title">吐槽与期望</h2>
      <p class="page-subtitle">记录所有用户的真实反馈，帮助我们持续改进</p>
    </div>

    <!-- 反馈输入区 -->
    <el-card class="feedback-input-card design-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📝 写下你的反馈</span>
        </div>
      </template>
      
      <el-form :model="newFeedback" label-width="100px">
        <el-form-item label="用户名（可选）">
          <el-input
            v-model="newFeedback.user_name"
            placeholder="留空则显示为匿名用户"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="反馈类型">
          <el-select v-model="newFeedback.feedback_type" placeholder="选择反馈类型">
            <el-option label="一般反馈" value="general" />
            <el-option label="问题/Bug" value="bug" />
            <el-option label="建议" value="suggestion" />
            <el-option label="表扬" value="praise" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="反馈内容" required>
          <el-input
            v-model="newFeedback.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述你的反馈、问题或建议..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="标签（可选）">
          <el-select
            v-model="newFeedback.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入标签，如：UI、匹配算法、脚本质量等"
            style="width: 100%"
          >
            <el-option label="UI界面" value="UI" />
            <el-option label="匹配算法" value="匹配算法" />
            <el-option label="脚本质量" value="脚本质量" />
            <el-option label="性能问题" value="性能问题" />
            <el-option label="功能建议" value="功能建议" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="submitting"
            class="gradient-button"
          >
            <el-icon><Check /></el-icon>
            提交反馈
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 反馈列表 -->
    <el-card class="feedback-list-card design-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📋 所有反馈</span>
          <div class="header-actions">
            <el-select
              v-model="filters.status"
              placeholder="筛选状态"
              clearable
              style="width: 150px; margin-right: 10px;"
              @change="loadFeedbacks"
            >
              <el-option label="全部" value="" />
              <el-option label="新反馈" value="new" />
              <el-option label="已查看" value="reviewed" />
              <el-option label="已解决" value="resolved" />
            </el-select>
            <el-select
              v-model="filters.feedback_type"
              placeholder="筛选类型"
              clearable
              style="width: 150px; margin-right: 10px;"
              @change="loadFeedbacks"
            >
              <el-option label="全部" value="" />
              <el-option label="一般反馈" value="general" />
              <el-option label="问题/Bug" value="bug" />
              <el-option label="建议" value="suggestion" />
              <el-option label="表扬" value="praise" />
            </el-select>
            <el-button @click="loadFeedbacks" :icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading" class="feedback-list">
        <div v-if="feedbacks.length === 0" class="empty-state">
          <el-empty description="暂无反馈" />
        </div>
        
        <div v-else class="feedback-items">
          <div
            v-for="feedback in feedbacks"
            :key="feedback.id"
            class="feedback-item"
            :class="{
              'feedback-new': feedback.status === 'new',
              'feedback-reviewed': feedback.status === 'reviewed',
              'feedback-resolved': feedback.status === 'resolved'
            }"
          >
            <div class="feedback-header">
              <div class="feedback-meta">
                <span class="feedback-user">
                  {{ feedback.user_name || '匿名用户' }}
                </span>
                <el-tag
                  :type="getFeedbackTypeTagType(feedback.feedback_type)"
                  size="small"
                  style="margin-left: 8px;"
                >
                  {{ getFeedbackTypeText(feedback.feedback_type) }}
                </el-tag>
                <el-tag
                  :type="getStatusTagType(feedback.status)"
                  size="small"
                  style="margin-left: 8px;"
                >
                  {{ getStatusText(feedback.status) }}
                </el-tag>
                <span class="feedback-time">
                  {{ formatTime(feedback.created_at) }}
                </span>
              </div>
              <div class="feedback-actions">
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="handleEdit(feedback)"
                >
                  编辑
                </el-button>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleDelete(feedback)"
                >
                  删除
                </el-button>
              </div>
            </div>
            
            <div class="feedback-content">
              {{ feedback.content }}
            </div>
            
            <div v-if="feedback.tags && feedback.tags.length > 0" class="feedback-tags">
              <el-tag
                v-for="tag in feedback.tags"
                :key="tag"
                size="small"
                type="info"
                style="margin-right: 6px;"
              >
                {{ tag }}
              </el-tag>
            </div>
            
            <div v-if="feedback.response" class="feedback-response">
              <div class="response-header">
                <strong>管理员回复：</strong>
                <span class="response-time">{{ formatTime(feedback.updated_at) }}</span>
              </div>
              <div class="response-content">{{ feedback.response }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑反馈"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editingFeedback" label-width="100px">
        <el-form-item label="状态">
          <el-select v-model="editingFeedback.status">
            <el-option label="新反馈" value="new" />
            <el-option label="已查看" value="reviewed" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="管理员回复">
          <el-input
            v-model="editingFeedback.response"
            type="textarea"
            :rows="4"
            placeholder="输入回复内容..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updating">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Refresh } from '@element-plus/icons-vue'
import { feedbackApi, type Feedback, type FeedbackCreateRequest } from '@/api/feedback'

const loading = ref(false)
const submitting = ref(false)
const updating = ref(false)
const feedbacks = ref<Feedback[]>([])
const editDialogVisible = ref(false)
const editingFeedback = ref<Feedback | null>(null)

const filters = ref({
  status: '',
  feedback_type: ''
})

const newFeedback = ref<FeedbackCreateRequest>({
  user_name: '',
  content: '',
  feedback_type: 'general',
  tags: []
})

const loadFeedbacks = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.feedback_type) {
      params.feedback_type = filters.value.feedback_type
    }
    
    const response = await feedbackApi.getFeedbacks(params)
    feedbacks.value = response.items
  } catch (error: any) {
    ElMessage.error('加载反馈列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!newFeedback.value.content.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }
  
  submitting.value = true
  try {
    await feedbackApi.createFeedback(newFeedback.value)
    ElMessage.success('反馈提交成功！感谢你的反馈')
    handleReset()
    loadFeedbacks()
  } catch (error: any) {
    ElMessage.error('提交反馈失败: ' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const handleReset = () => {
  newFeedback.value = {
    user_name: '',
    content: '',
    feedback_type: 'general',
    tags: []
  }
}

const handleEdit = (feedback: Feedback) => {
  editingFeedback.value = { ...feedback }
  editDialogVisible.value = true
}

const handleUpdate = async () => {
  if (!editingFeedback.value) return
  
  updating.value = true
  try {
    await feedbackApi.updateFeedback(editingFeedback.value.id, {
      status: editingFeedback.value.status,
      response: editingFeedback.value.response
    })
    ElMessage.success('反馈已更新')
    editDialogVisible.value = false
    loadFeedbacks()
  } catch (error: any) {
    ElMessage.error('更新反馈失败: ' + (error.message || '未知错误'))
  } finally {
    updating.value = false
  }
}

const handleDelete = async (feedback: Feedback) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条反馈吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await feedbackApi.deleteFeedback(feedback.id)
    ElMessage.success('反馈已删除')
    loadFeedbacks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除反馈失败: ' + (error.message || '未知错误'))
    }
  }
}

const getFeedbackTypeText = (type?: string) => {
  const map: Record<string, string> = {
    general: '一般反馈',
    bug: '问题/Bug',
    suggestion: '建议',
    praise: '表扬'
  }
  return map[type || 'general'] || '一般反馈'
}

const getFeedbackTypeTagType = (type?: string) => {
  const map: Record<string, string> = {
    general: '',
    bug: 'danger',
    suggestion: 'warning',
    praise: 'success'
  }
  return map[type || 'general'] || ''
}

const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    new: '新反馈',
    reviewed: '已查看',
    resolved: '已解决'
  }
  return map[status || 'new'] || '新反馈'
}

const getStatusTagType = (status?: string) => {
  const map: Record<string, string> = {
    new: 'warning',
    reviewed: 'info',
    resolved: 'success'
  }
  return map[status || 'new'] || 'warning'
}

const formatTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadFeedbacks()
})
</script>

<style scoped>
.feedback-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  padding: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.feedback-input-card,
.feedback-list-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
}

.feedback-list {
  min-height: 200px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.feedback-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feedback-item {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: var(--bg-primary);
  transition: all 0.2s;
}

.feedback-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feedback-new {
  border-left: 4px solid #f59e0b;
}

.feedback-reviewed {
  border-left: 4px solid #3b82f6;
}

.feedback-resolved {
  border-left: 4px solid #10b981;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.feedback-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.feedback-user {
  font-weight: 500;
  color: var(--text-primary);
}

.feedback-time {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: 8px;
}

.feedback-actions {
  display: flex;
  gap: 8px;
}

.feedback-content {
  margin: 12px 0;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.feedback-tags {
  margin-top: 12px;
}

.feedback-response {
  margin-top: 16px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.response-content {
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

