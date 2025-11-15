<template>
  <div class="products-view">
    <div class="page-header design-card">
      <h2 class="page-title">商品管理</h2>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="handleCreate"
          class="gradient-button"
        >
          <el-icon><Plus /></el-icon>
          新建商品
        </el-button>
        <el-button 
          type="primary" 
          @click="openHotspotDialog(null)"
          class="gradient-button"
        >
          <el-icon><TrendCharts /></el-icon>
          选择热点生成脚本
        </el-button>
      </div>
    </div>
    
    <el-card class="products-list design-card">
      <template #header>
        <div class="card-header">
          <span>商品列表</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="直播间">
          <el-select v-model="filters.live_room_id" placeholder="选择直播间" clearable>
            <el-option
              v-for="room in liveRooms"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProducts">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 商品列表 -->
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="name" label="商品名称" min-width="150" />
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="category" label="品类" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="live_date" label="直播日期" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="success" @click="openHotspotDialog(row)">选择热点</el-button>
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
        @size-change="loadProducts"
        @current-change="loadProducts"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="商品名称" required>
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="formData.brand" />
        </el-form-item>
        <el-form-item label="品类" required>
          <el-input v-model="formData.category" />
        </el-form-item>
        <el-form-item label="直播间" required>
          <el-select v-model="formData.live_room_id" placeholder="选择直播间">
            <el-option
              v-for="room in liveRooms"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" required>
          <el-input-number v-model="formData.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="直播日期" required>
          <el-date-picker
            v-model="formData.live_date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
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
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="说明手卡">
          <el-input v-model="formData.hand_card" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="商品详情" width="800px">
      <el-descriptions :column="2" border v-if="selectedProduct">
        <el-descriptions-item label="商品名称">{{ selectedProduct.name }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ selectedProduct.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="品类">{{ selectedProduct.category }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ selectedProduct.price?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="直播日期">{{ selectedProduct.live_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedProduct.created_at }}</el-descriptions-item>
        <el-descriptions-item label="核心卖点" :span="2">
          <el-tag
            v-for="point in selectedProduct.selling_points"
            :key="point"
            style="margin-right: 8px"
          >
            {{ point }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="商品描述" :span="2">
          {{ selectedProduct.description || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="说明手卡" :span="2">
          {{ selectedProduct.hand_card || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <!-- 热点选择对话框 -->
    <HotspotSelectionDialog
      v-model="hotspotDialogVisible"
      :product="selectedProductForHotspot"
      @script-generated="handleScriptGenerated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { TrendCharts, Plus } from '@element-plus/icons-vue'
import { productsApi, type Product, type ProductCreate } from '@/api/products'
import { liveRoomsApi, type LiveRoom } from '@/api/liveRooms'
import HotspotSelectionDialog from '@/components/HotspotSelectionDialog.vue'

const router = useRouter()

const loading = ref(false)
const products = ref<Product[]>([])
const liveRooms = ref<LiveRoom[]>([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const selectedProduct = ref<Product | null>(null)
const selectedProductForHotspot = ref<Product | null>(null)
const hotspotDialogVisible = ref(false)
const isEdit = ref(false)

const filters = ref({
  live_room_id: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const formData = ref<Partial<ProductCreate>>({
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

const dialogTitle = computed(() => isEdit.value ? '编辑商品' : '新建商品')

const loadProducts = async () => {
  loading.value = true
  try {
    const response = await productsApi.getProducts({
      live_room_id: filters.value.live_room_id || undefined,
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

const handleCreate = () => {
  isEdit.value = false
  formData.value = {
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
  dialogVisible.value = true
}

const handleEdit = (product: Product) => {
  isEdit.value = true
  formData.value = { ...product }
  sellingPointsText.value = product.selling_points?.join('\n') || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.name || !formData.value.category || !formData.value.live_room_id || !formData.value.live_date) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data: ProductCreate = {
      ...formData.value,
      selling_points: sellingPointsText.value.split('\n').filter(s => s.trim()),
      live_date: formData.value.live_date!
    } as ProductCreate

    if (isEdit.value && formData.value.id) {
      await productsApi.updateProduct(formData.value.id, data)
      ElMessage.success('商品更新成功')
    } else {
      await productsApi.createProduct(data)
      ElMessage.success('商品创建成功')
    }
    dialogVisible.value = false
    loadProducts()
  } catch (error: any) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

const viewDetail = async (product: Product) => {
  try {
    const detail = await productsApi.getProductDetail(product.id)
    selectedProduct.value = detail
    detailVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取详情失败: ' + (error.message || '未知错误'))
  }
}

const resetFilters = () => {
  filters.value = { live_room_id: '' }
  loadProducts()
}

const openHotspotDialog = (product: Product) => {
  selectedProductForHotspot.value = product
  hotspotDialogVisible.value = true
}

const handleScriptGenerated = (scriptId: string) => {
  ElMessage.success('脚本生成成功')
  hotspotDialogVisible.value = false
  
  // 跳转到脚本管理页面
  router.push('/scripts')
}

onMounted(() => {
  loadLiveRooms()
  loadProducts()
})
</script>

<style scoped>
.products-view {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.products-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.products-list :deep(.el-card__body) {
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

.products-list :deep(.el-table) {
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.products-list :deep(.el-table__header) {
  background: linear-gradient(to right, #fdf2f8, #fff7ed);
}

.products-list :deep(.el-table__row:hover) {
  background: rgba(249, 250, 251, 0.5);
}
</style>

