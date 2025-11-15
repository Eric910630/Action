<template>
  <el-dialog
    v-model="visible"
    title="选择商品"
    width="900px"
    @close="handleClose"
  >
    <div class="dialog-content">
      <!-- 热点信息展示 -->
      <el-card v-if="hotspot" class="hotspot-info" shadow="never">
        <template #header>
          <span>关联热点</span>
        </template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="标题">{{ hotspot.title }}</el-descriptions-item>
          <el-descriptions-item label="匹配度">
            <el-tag v-if="hotspot.match_score" :type="getMatchScoreType(hotspot.match_score)">
              {{ (hotspot.match_score * 100).toFixed(0) }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="热度">{{ hotspot.heat_score || '-' }}</el-descriptions-item>
          <el-descriptions-item label="平台">{{ hotspot.platform }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- Tab切换：选择商品 / 上传新商品 -->
      <el-tabs v-model="activeTab" class="content-tabs">
        <el-tab-pane label="选择已有商品" name="select">
          <!-- 商品列表 -->
          <el-table 
            :data="products" 
            v-loading="loading" 
            stripe
            @row-click="handleRowClick"
            highlight-current-row
          >
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="商品名称" min-width="150" />
            <el-table-column prop="brand" label="品牌" width="120" />
            <el-table-column prop="category" label="品类" width="100" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                ¥{{ row.price?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="handleSelectProduct(row)"
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
            @size-change="loadProducts"
            @current-change="loadProducts"
            style="margin-top: 20px"
          />
        </el-tab-pane>
        
        <el-tab-pane label="上传新商品" name="upload">
          <el-form :model="newProductForm" label-width="100px">
            <el-form-item label="商品名称" required>
              <el-input v-model="newProductForm.name" />
            </el-form-item>
            <el-form-item label="品牌">
              <el-input v-model="newProductForm.brand" />
            </el-form-item>
            <el-form-item label="品类" required>
              <el-input v-model="newProductForm.category" />
            </el-form-item>
            <el-form-item label="直播间" required>
              <el-select v-model="newProductForm.live_room_id" placeholder="选择直播间">
                <el-option
                  v-for="room in liveRooms"
                  :key="room.id"
                  :label="room.name"
                  :value="room.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="价格" required>
              <el-input-number v-model="newProductForm.price" :min="0" :precision="2" />
            </el-form-item>
            <el-form-item label="核心卖点">
              <el-input
                v-model="sellingPointsText"
                type="textarea"
                :rows="3"
                placeholder="每行一个卖点"
              />
            </el-form-item>
            <el-form-item label="商品描述">
              <el-input v-model="newProductForm.description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="说明手卡">
              <el-input v-model="newProductForm.hand_card" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="直播日期" required>
              <el-date-picker
                v-model="newProductForm.live_date"
                type="date"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
              />
            </el-form-item>
          </el-form>
          
          <div class="upload-actions">
            <el-button @click="handleResetForm">重置</el-button>
            <el-button type="primary" @click="handleCreateProduct">创建商品并生成脚本</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleGenerateScript"
          :disabled="!selectedProduct"
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
import { productsApi, type Product, type ProductCreate } from '@/api/products'
import { liveRoomsApi, type LiveRoom } from '@/api/liveRooms'
import { scriptsApi } from '@/api/scripts'
import type { Hotspot } from '@/api/hotspots'

interface Props {
  modelValue: boolean
  hotspot: Hotspot | null
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
const products = ref<Product[]>([])
const liveRooms = ref<LiveRoom[]>([])
const selectedProduct = ref<Product | null>(null)
const activeTab = ref('select')

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const newProductForm = ref<Partial<ProductCreate>>({
  name: '',
  brand: '',
  category: '',
  live_room_id: '',
  price: 0,
  selling_points: [],
  description: '',
  hand_card: '',
  live_date: ''
})
const sellingPointsText = ref('')

const loadProducts = async () => {
  loading.value = true
  try {
    const response = await productsApi.getProducts({
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    })
    products.value = response.items
    pagination.value.total = response.total
  } catch (error: any) {
    ElMessage.error('加载商品失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadLiveRooms = async () => {
  try {
    const response = await liveRoomsApi.getLiveRooms()
    liveRooms.value = response.items
  } catch (error) {
    console.error('加载直播间失败:', error)
  }
}

const handleSelectProduct = (product: Product) => {
  selectedProduct.value = product
  ElMessage.success(`已选择商品: ${product.name}`)
}

const handleRowClick = (row: Product) => {
  selectedProduct.value = row
}

const handleCreateProduct = async () => {
  if (!newProductForm.value.name || !newProductForm.value.category || !newProductForm.value.live_room_id) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data: ProductCreate = {
      ...newProductForm.value,
      selling_points: sellingPointsText.value.split('\n').filter(s => s.trim()),
      live_date: newProductForm.value.live_date || new Date().toISOString().split('T')[0]
    } as ProductCreate

    const response = await productsApi.createProduct(data)
    const productId = response.id
    
    ElMessage.success('商品创建成功')
    
    // 自动选择新创建的商品
    selectedProduct.value = await productsApi.getProductDetail(productId)
    
    // 切换到选择标签页
    activeTab.value = 'select'
    
    // 自动生成脚本
    if (props.hotspot) {
      await generateScript(props.hotspot.id, productId)
    }
  } catch (error: any) {
    ElMessage.error('创建商品失败: ' + (error.message || '未知错误'))
  }
}

const handleGenerateScript = async () => {
  if (!selectedProduct.value || !props.hotspot) {
    ElMessage.warning('请选择商品')
    return
  }

  await generateScript(props.hotspot.id, selectedProduct.value.id)
}

const generateScript = async (hotspotId: string, productId: string) => {
  try {
    const response = await scriptsApi.generateScript({
      hotspot_id: hotspotId,
      product_id: productId,
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

const handleResetForm = () => {
  newProductForm.value = {
    name: '',
    brand: '',
    category: '',
    live_room_id: '',
    price: 0,
    selling_points: [],
    description: '',
    hand_card: '',
    live_date: ''
  }
  sellingPointsText.value = ''
}

const handleClose = () => {
  selectedProduct.value = null
  activeTab.value = 'select'
  handleResetForm()
}

const getMatchScoreType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'info'
}

watch(visible, (newVal) => {
  if (newVal) {
    loadProducts()
    loadLiveRooms()
    selectedProduct.value = null
  }
})
</script>

<style scoped>
.dialog-content {
  min-height: 400px;
}

.hotspot-info {
  margin-bottom: 20px;
}

.content-tabs {
  margin-top: 20px;
}

.upload-actions {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

