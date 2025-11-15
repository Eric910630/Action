<template>
  <div class="live-rooms-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>直播间管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建直播间
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="类别">
          <el-select v-model="filters.category" placeholder="选择类别" clearable>
            <el-option label="女装" value="女装" />
            <el-option label="童装" value="童装" />
            <el-option label="家具" value="家具" />
            <el-option label="家电" value="家电" />
            <el-option label="奢侈品" value="奢侈品" />
            <el-option label="美妆" value="美妆" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLiveRooms">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 直播间列表 -->
      <el-table :data="liveRooms" v-loading="loading" stripe>
        <el-table-column prop="name" label="直播间名称" min-width="150" />
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="ip_character" label="IP人设" width="120" />
        <el-table-column prop="style" label="风格" width="120" />
        <el-table-column prop="keywords" label="关键词" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="keyword in row.keywords?.slice(0, 5)"
              :key="keyword"
              size="small"
              style="margin-right: 4px"
            >
              {{ keyword }}
            </el-tag>
            <span v-if="(row.keywords?.length || 0) > 5">...</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
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
            :rows="3"
            placeholder="每行一个关键词，支持+必须词和!过滤词"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="直播间详情" width="800px">
      <el-descriptions :column="2" border v-if="selectedLiveRoom">
        <el-descriptions-item label="直播间名称">{{ selectedLiveRoom.name }}</el-descriptions-item>
        <el-descriptions-item label="类别">{{ selectedLiveRoom.category }}</el-descriptions-item>
        <el-descriptions-item label="IP人设">{{ selectedLiveRoom.ip_character || '-' }}</el-descriptions-item>
        <el-descriptions-item label="风格">{{ selectedLiveRoom.style || '-' }}</el-descriptions-item>
        <el-descriptions-item label="关键词" :span="2">
          <el-tag
            v-for="keyword in selectedLiveRoom.keywords"
            :key="keyword"
            style="margin-right: 8px"
          >
            {{ keyword }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedLiveRoom.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { liveRoomsApi, type LiveRoom, type LiveRoomCreate } from '@/api/liveRooms'

const loading = ref(false)
const liveRooms = ref<LiveRoom[]>([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const selectedLiveRoom = ref<LiveRoom | null>(null)
const isEdit = ref(false)

const filters = ref({
  category: ''
})

const formData = ref<Partial<LiveRoomCreate>>({
  name: '',
  category: '',
  keywords: [],
  ip_character: '',
  style: ''
})

const keywordsText = ref('')

const dialogTitle = computed(() => isEdit.value ? '编辑直播间' : '新建直播间')

const loadLiveRooms = async () => {
  loading.value = true
  try {
    const response = await liveRoomsApi.getLiveRooms(filters.value.category || undefined)
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
  dialogVisible.value = true
}

const handleEdit = (room: LiveRoom) => {
  isEdit.value = true
  formData.value = { ...room }
  keywordsText.value = room.keywords?.join('\n') || ''
  dialogVisible.value = true
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
    dialogVisible.value = false
    loadLiveRooms()
  } catch (error: any) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

const viewDetail = async (room: LiveRoom) => {
  try {
    const detail = await liveRoomsApi.getLiveRoomDetail(room.id)
    selectedLiveRoom.value = detail
    detailVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取详情失败: ' + (error.message || '未知错误'))
  }
}

const resetFilters = () => {
  filters.value = { category: '' }
  loadLiveRooms()
}

onMounted(() => {
  loadLiveRooms()
})
</script>

<style scoped>
.live-rooms-view {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}
</style>

