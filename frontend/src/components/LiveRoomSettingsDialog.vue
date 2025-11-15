<template>
  <el-dialog
    v-model="visible"
    title="设置"
    width="900px"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 直播间设置 -->
      <el-tab-pane label="直播间设置" name="liveRooms">
        <div class="settings-content">
          <!-- 直播间列表 -->
          <el-table :data="liveRooms" v-loading="loading" stripe>
        <el-table-column prop="name" label="直播间名称" min-width="150" />
        <el-table-column prop="category" label="类目" width="120" />
        <el-table-column prop="ip_character" label="IP人设" width="150" />
        <el-table-column prop="style" label="风格" width="120" />
        <el-table-column label="关键词" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="keyword in row.keywords?.slice(0, 3)"
              :key="keyword"
              size="small"
              style="margin-right: 4px"
            >
              {{ keyword }}
            </el-tag>
            <span v-if="row.keywords && row.keywords.length > 3">
              +{{ row.keywords.length - 3 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
          <div class="actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建直播间
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 系统设置 -->
      <el-tab-pane label="系统设置" name="system">
        <div class="settings-content">
          <el-card shadow="never" class="setting-card">
            <template #header>
              <div class="setting-header">
                <span class="setting-title">DeepSeek API Key</span>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleConfigureDeepSeek"
                >
                  <el-icon><Setting /></el-icon>
                  配置
                </el-button>
              </div>
            </template>
            <div class="setting-description">
              <p>用于AI内容分析和脚本生成功能。如果未配置，相关功能将无法使用。</p>
              <p v-if="deepSeekApiKeyStatus.configured" class="status-text">
                <el-icon class="success-icon"><CircleCheck /></el-icon>
                已配置：{{ deepSeekApiKeyStatus.masked_key }}
              </p>
              <p v-else class="status-text">
                <el-icon class="warning-icon"><Warning /></el-icon>
                未配置
              </p>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- DeepSeek API Key配置对话框 -->
    <el-dialog
      v-model="deepSeekConfigVisible"
      title="配置DeepSeek API Key"
      width="700px"
      append-to-body
    >
      <div class="deepseek-config-content">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #title>
            <div class="alert-content">
              <p><strong>如何获取DeepSeek API Key：</strong></p>
              <ol class="guide-steps">
                <li>访问 <a href="https://platform.deepseek.com/" target="_blank" class="link">DeepSeek官网</a> 并注册/登录账号</li>
                <li>进入控制台，找到"API Keys"或"密钥管理"页面</li>
                <li>点击"创建新密钥"或"Generate API Key"</li>
                <li>复制生成的API Key（格式为：sk-xxxxxxxxxxxxx）</li>
                <li>将API Key粘贴到下方输入框中并保存</li>
              </ol>
              <p style="margin-top: 12px; color: #909399; font-size: 13px;">
                <el-icon><InfoFilled /></el-icon>
                提示：API Key将保存到本地配置文件，请妥善保管，不要泄露给他人。
              </p>
            </div>
          </template>
        </el-alert>
        
        <el-form :model="deepSeekForm" label-width="120px">
          <el-form-item label="API Key" required>
            <el-input
              v-model="deepSeekForm.api_key"
              type="password"
              placeholder="请输入DeepSeek API Key（格式：sk-xxxxxxxxxxxxx）"
              show-password
              :maxlength="200"
            />
            <div class="form-tip">
              <el-icon><InfoFilled /></el-icon>
              API Key格式应以"sk-"开头
            </div>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="deepSeekConfigVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitDeepSeekConfig"
          :loading="savingDeepSeek"
          :disabled="!deepSeekForm.api_key || !deepSeekForm.api_key.trim()"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editDialogTitle"
      width="600px"
      append-to-body
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="直播间名称" required>
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="类别" required>
          <el-select v-model="formData.category" placeholder="选择类别">
            <el-option label="女装" value="女装" />
            <el-option label="童装" value="童装" />
            <el-option label="家具" value="家具" />
            <el-option label="家电" value="家电" />
            <el-option label="奢侈品" value="奢侈品" />
            <el-option label="美妆" value="美妆" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP人设">
          <el-input v-model="formData.ip_character" />
        </el-form-item>
        <el-form-item label="风格">
          <el-input v-model="formData.style" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="keywordsText"
            type="textarea"
            :rows="4"
            placeholder="每行一个关键词"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Setting, CircleCheck, Warning, InfoFilled } from '@element-plus/icons-vue'
import { liveRoomsApi, type LiveRoom, type LiveRoomCreate } from '@/api/liveRooms'
import { settingsApi, type DeepSeekApiKeyResponse } from '@/api/settings'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const activeTab = ref('liveRooms') // 当前激活的tab
const loading = ref(false)
const liveRooms = ref<LiveRoom[]>([])
const editDialogVisible = ref(false)
const isEdit = ref(false)
const formData = ref<Partial<LiveRoomCreate>>({
  name: '',
  category: '',
  keywords: [],
  ip_character: '',
  style: ''
})
const keywordsText = ref('')

// DeepSeek API Key配置相关
const deepSeekConfigVisible = ref(false)
const savingDeepSeek = ref(false)
const deepSeekApiKeyStatus = ref<DeepSeekApiKeyResponse>({ configured: false })
const deepSeekForm = ref({
  api_key: ''
})

const editDialogTitle = computed(() => isEdit.value ? '编辑直播间' : '新建直播间')

const loadLiveRooms = async () => {
  loading.value = true
  try {
    const response = await liveRoomsApi.getLiveRooms()
    liveRooms.value = response.items
  } catch (error: any) {
    ElMessage.error('加载直播间失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEdit.value = false
  formData.value = {
    name: '',
    category: '',
    keywords: [],
    ip_character: '',
    style: ''
  }
  keywordsText.value = ''
  editDialogVisible.value = true
}

const handleEdit = (room: LiveRoom) => {
  isEdit.value = true
  formData.value = { ...room }
  keywordsText.value = room.keywords?.join('\n') || ''
  editDialogVisible.value = true
}

const handleDelete = async (room: LiveRoom) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除直播间"${room.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await liveRoomsApi.deleteLiveRoom(room.id)
    ElMessage.success('删除成功')
    loadLiveRooms()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleSubmit = async () => {
  if (!formData.value.name || !formData.value.category) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data: LiveRoomCreate = {
      ...formData.value,
      keywords: keywordsText.value.split('\n').filter(s => s.trim())
    } as LiveRoomCreate

    if (isEdit.value && formData.value.id) {
      await liveRoomsApi.updateLiveRoom(formData.value.id, data)
      ElMessage.success('直播间更新成功')
    } else {
      await liveRoomsApi.createLiveRoom(data)
      ElMessage.success('直播间创建成功')
    }
    editDialogVisible.value = false
    loadLiveRooms()
  } catch (error: any) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

const handleClose = () => {
  editDialogVisible.value = false
}

const loadDeepSeekApiKeyStatus = async () => {
  try {
    const response = await settingsApi.getDeepSeekApiKey()
    deepSeekApiKeyStatus.value = response
  } catch (error: any) {
    console.error('获取DeepSeek API Key状态失败:', error)
  }
}

const handleConfigureDeepSeek = () => {
  deepSeekForm.value.api_key = ''
  deepSeekConfigVisible.value = true
}

const submitDeepSeekConfig = async () => {
  if (!deepSeekForm.value.api_key || !deepSeekForm.value.api_key.trim()) {
    ElMessage.warning('请输入API Key')
    return
  }

  const apiKey = deepSeekForm.value.api_key.trim()
  
  // 验证格式
  if (!apiKey.startsWith('sk-')) {
    ElMessage.warning('API Key格式不正确，应以"sk-"开头')
    return
  }

  try {
    savingDeepSeek.value = true
    await settingsApi.setDeepSeekApiKey({ api_key: apiKey })
    ElMessage.success('API Key已保存')
    deepSeekConfigVisible.value = false
    deepSeekForm.value.api_key = ''
    // 重新加载状态
    await loadDeepSeekApiKeyStatus()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    savingDeepSeek.value = false
  }
}

watch(visible, (newVal) => {
  if (newVal) {
    loadLiveRooms()
    loadDeepSeekApiKeyStatus()
  }
})
</script>

<style scoped>
.settings-tabs {
  min-height: 400px;
}

.settings-content {
  padding: 10px 0;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

.setting-card {
  margin-bottom: 20px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.setting-description {
  color: var(--text-secondary);
  line-height: 1.8;
}

.setting-description p {
  margin: 8px 0;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 14px;
}

.success-icon {
  color: #67c23a;
}

.warning-icon {
  color: #e6a23c;
}

.deepseek-config-content {
  padding: 10px 0;
}

.alert-content {
  padding: 8px 0;
}

.guide-steps {
  margin: 12px 0;
  padding-left: 24px;
  line-height: 2;
}

.guide-steps li {
  margin: 8px 0;
}

.link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>

