<template>
  <el-dialog
    v-model="visible"
    title="选择热点"
    width="1000px"
    @close="handleClose"
  >
    <div class="dialog-content">
      <!-- 商品信息展示 -->
      <el-card v-if="product" class="product-info" shadow="never">
        <template #header>
          <span>关联商品</span>
        </template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="商品名称">{{ product.name }}</el-descriptions-item>
          <el-descriptions-item label="品类">{{ product.category }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ product.brand || '-' }}</el-descriptions-item>
          <el-descriptions-item label="价格">¥{{ product.price?.toFixed(2) }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- Tab切换：气泡图 / 列表 -->
      <el-tabs v-model="viewMode" class="content-tabs">
        <el-tab-pane label="气泡图" name="chart">
          <div class="chart-wrapper">
            <HotspotBubbleChart 
              v-if="visualizationData" 
              :data="visualizationData"
              @bubble-click="handleBubbleClick"
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="列表" name="list">
          <!-- 筛选条件 -->
          <el-form :inline="true" class="filter-form">
            <el-form-item label="平台">
              <el-select v-model="filters.platform" placeholder="选择平台" clearable>
                <el-option label="抖音" value="douyin" />
                <el-option label="微博" value="weibo" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadHotspots">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>
          
          <!-- 热点列表 -->
          <el-table 
            :data="hotspots" 
            v-loading="loading" 
            stripe
            @row-click="handleRowClick"
            highlight-current-row
          >
            <el-table-column type="index" width="50" />
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="platform" label="平台" width="100" />
            <el-table-column prop="heat_score" label="热度" width="100" />
            <el-table-column prop="match_score" label="匹配度" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.match_score" :type="getMatchScoreType(row.match_score)">
                  {{ (row.match_score * 100).toFixed(0) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="handleSelectHotspot(row)"
                >
                  选择
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadHotspots"
            @current-change="loadHotspots"
            style="margin-top: 20px"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleGenerateScript"
          :disabled="!selectedHotspot"
        >
          生成视频脚本
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { hotspotsApi, type Hotspot } from '@/api/hotspots'
import { scriptsApi } from '@/api/scripts'
import HotspotBubbleChart from '@/components/HotspotBubbleChart.vue'
import type { Product } from '@/api/products'

interface Props {
  modelValue: boolean
  product: Product | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'script-generated': [scriptId: string]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const hotspots = ref<Hotspot[]>([])
const selectedHotspot = ref<Hotspot | null>(null)
const viewMode = ref('chart')
const visualizationData = ref<any>(null)

const filters = ref({
  platform: '',
  live_room_id: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadHotspots = async () => {
  loading.value = true
  try {
    const response = await hotspotsApi.getHotspots({
      platform: filters.value.platform || undefined,
      live_room_id: filters.value.live_room_id || undefined,
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    })
    hotspots.value = response.items
    pagination.value.total = response.total
  } catch (error: any) {
    ElMessage.error('加载热点失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadVisualizationData = async () => {
  try {
    // 如果商品有直播间ID，可以按直播间筛选
    const liveRoomId = props.product?.live_room_id
    const data = await hotspotsApi.getVisualization(liveRoomId)
    visualizationData.value = data
  } catch (error) {
    console.error('加载可视化数据失败:', error)
  }
}

const handleSelectHotspot = (hotspot: Hotspot) => {
  selectedHotspot.value = hotspot
  ElMessage.success(`已选择热点: ${hotspot.title}`)
}

const handleRowClick = (row: Hotspot) => {
  selectedHotspot.value = row
}

const handleBubbleClick = async (hotspot: any) => {
  try {
    const detail = await hotspotsApi.getHotspotDetail(hotspot.id)
    selectedHotspot.value = detail
    ElMessage.success(`已选择热点: ${detail.title}`)
  } catch (error: any) {
    ElMessage.error('获取热点详情失败: ' + (error.message || '未知错误'))
  }
}

const handleGenerateScript = async () => {
  if (!selectedHotspot.value || !props.product) {
    ElMessage.warning('请选择热点')
    return
  }

  try {
    const response = await scriptsApi.generateScript({
      hotspot_id: selectedHotspot.value.id,
      product_id: props.product.id,
      duration: 10,
      script_count: 5  // 默认生成5个不同的脚本
    })
    
    ElMessage.success('脚本生成任务已启动')
    emit('script-generated', response.task_id)
    visible.value = false
  } catch (error: any) {
    ElMessage.error('生成脚本失败: ' + (error.message || '未知错误'))
  }
}

const resetFilters = () => {
  filters.value = {
    platform: '',
    live_room_id: ''
  }
  loadHotspots()
}

const handleClose = () => {
  selectedHotspot.value = null
  viewMode.value = 'chart'
}

const getMatchScoreType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'info'
}

watch(visible, (newVal) => {
  if (newVal) {
    if (viewMode.value === 'chart') {
      loadVisualizationData()
    } else {
      loadHotspots()
    }
    selectedHotspot.value = null
  }
})

watch(viewMode, (newMode) => {
  if (visible.value) {
    if (newMode === 'chart') {
      loadVisualizationData()
    } else {
      loadHotspots()
    }
  }
})
</script>

<style scoped>
.dialog-content {
  min-height: 500px;
}

.product-info {
  margin-bottom: 20px;
}

.content-tabs {
  margin-top: 20px;
}

.chart-wrapper {
  height: 500px;
  width: 100%;
}

.filter-form {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

