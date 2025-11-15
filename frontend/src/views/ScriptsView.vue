<template>
  <div class="scripts-view">
    <div class="page-header design-card">
      <h2 class="page-title">脚本管理</h2>
      <el-button 
        type="primary" 
        @click="handleGenerate"
        class="gradient-button"
      >
        <el-icon><Plus /></el-icon>
        生成脚本
      </el-button>
    </div>
    
    <!-- 脚本生成进度提示 -->
    <div v-if="generatingScript || currentScriptTaskId" class="script-generating-card design-card glass-strong" style="margin-bottom: 20px;">
      <div class="task-progress-content">
        <div class="task-status-header">
          <div class="task-status-left">
            <div class="task-status-icon-wrapper">
              <el-icon v-if="generatingScript || scriptTaskStatus?.state === 'PROGRESS' || scriptTaskStatus?.state === 'PENDING'" class="spinning-icon">
                <Loading />
              </el-icon>
              <el-icon v-else-if="scriptTaskStatus?.state === 'SUCCESS'" class="success-icon">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="scriptTaskStatus?.state === 'FAILURE'" class="error-icon">
                <CircleClose />
              </el-icon>
            </div>
            <span class="task-status-text">{{ scriptTaskStatusText }}</span>
          </div>
        </div>
        
        <!-- 自定义进度条 -->
        <div class="custom-progress-wrapper">
          <div class="custom-progress-track">
            <div 
              class="custom-progress-bar"
              :class="{
                'progress-indeterminate': generatingScript && (!scriptTaskStatus || scriptTaskStatus.state === 'PENDING'),
                'progress-success': scriptTaskStatus?.state === 'SUCCESS',
                'progress-error': scriptTaskStatus?.state === 'FAILURE'
              }"
              :style="{
                width: scriptTaskStatus?.current && scriptTaskStatus?.total 
                  ? `${Math.round((scriptTaskStatus.current / scriptTaskStatus.total) * 100)}%` 
                  : '100%'
              }"
            ></div>
          </div>
        </div>
        
        <div v-if="scriptTaskStatus?.status" class="task-detail">{{ scriptTaskStatus.status }}</div>
      </div>
    </div>

    <el-card class="scripts-list design-card">
      <template #header>
        <div class="card-header">
          <span>脚本列表</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="商品">
          <el-select v-model="filters.product_id" placeholder="选择商品" clearable>
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已审核" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadScripts">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 脚本列表 -->
      <el-table :data="scripts" v-loading="loading" stripe>
        <el-table-column prop="video_info.title" label="视频标题" min-width="150">
          <template #default="{ row }">
            {{ row.video_info?.title || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-badge', `status-${row.status || 'draft'}`]">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="handleOptimize(row)">优化</el-button>
            <el-button link type="warning" @click="handleRegenerate(row)">重新生成</el-button>
            <el-button
              v-if="row.status === 'draft'"
              link
              type="success"
              @click="handleReview(row, 'approve')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              link
              type="danger"
              @click="handleReview(row, 'reject')"
            >
              拒绝
            </el-button>
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
        @size-change="loadScripts"
        @current-change="loadScripts"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 生成脚本对话框 -->
    <el-dialog v-model="generateVisible" title="生成脚本" width="600px">
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="热点" required>
          <el-select v-model="generateForm.hotspot_id" placeholder="选择热点">
            <el-option
              v-for="hotspot in hotspots"
              :key="hotspot.id"
              :label="hotspot.title"
              :value="hotspot.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品" required>
          <el-select v-model="generateForm.product_id" placeholder="选择商品">
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="拆解报告">
          <el-select v-model="generateForm.analysis_report_id" placeholder="选择拆解报告（可选）" clearable>
            <el-option
              v-for="report in reports"
              :key="report.id"
              :label="report.video_url"
              :value="report.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="视频时长（秒）" required>
          <el-input-number v-model="generateForm.duration" :min="5" :max="15" />
        </el-form-item>
        <el-form-item label="生成数量" required>
          <el-input-number v-model="generateForm.script_count" :min="1" :max="10" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            将生成 {{ generateForm.script_count }} 个不同版本的脚本
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGenerate">生成</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="脚本详情" width="1000px" class="script-detail-dialog">
      <div v-if="selectedScript">
        <el-tabs>
          <el-tab-pane label="基本信息">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="视频标题">
                {{ selectedScript.video_info?.title || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="时长">
                {{ selectedScript.video_info?.duration || '-' }}秒
              </el-descriptions-item>
              <el-descriptions-item label="主题">
                {{ selectedScript.video_info?.theme || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="核心卖点">
                {{ selectedScript.video_info?.core_selling_point || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <span :class="['status-badge', `status-${selectedScript.status || 'draft'}`]">
                  {{ getStatusText(selectedScript.status) }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ selectedScript.created_at }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          <el-tab-pane label="脚本内容">
            <div class="edit-toolbar">
              <el-button
                v-if="!isEditing"
                type="primary"
                size="small"
                @click="startEdit('content')"
              >
                编辑
              </el-button>
              <div v-else class="edit-actions">
                <el-button type="success" size="small" @click="saveEdit">保存</el-button>
                <el-button size="small" @click="cancelEdit">取消</el-button>
              </div>
            </div>
            
            <!-- 如果有分镜列表，优先展示分镜卡片 -->
            <div v-if="(isEditing ? editingScript : selectedScript).shot_list && (isEditing ? editingScript : selectedScript).shot_list.length > 0" class="shot-list-container">
              <el-card
                v-for="(shot, index) in (isEditing ? editingScript : selectedScript).shot_list"
                :key="index"
                class="shot-card"
                shadow="hover"
              >
                <template #header>
                  <div class="shot-header">
                    <el-tag type="primary" size="large">镜头 {{ shot.shot_number || index + 1 }}</el-tag>
                    <el-tag type="info">{{ shot.time_range || '-' }}</el-tag>
                    <el-tag v-if="shot.shot_type" type="success">{{ shot.shot_type }}</el-tag>
                    <el-button
                      v-if="isEditing"
                      type="danger"
                      size="small"
                      text
                      @click="removeShot(index)"
                      style="margin-left: auto"
                    >
                      删除
                    </el-button>
                  </div>
                </template>
                
                <div class="shot-content">
                  <div class="shot-item" v-if="shot.content || isEditing">
                    <div class="shot-label">画面内容：</div>
                    <div v-if="!isEditing" class="shot-value">{{ shot.content }}</div>
                    <el-input
                      v-else
                      v-model="shot.content"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入画面内容"
                    />
                  </div>
                  
                  <div class="shot-item" v-if="shot.dialogue || isEditing">
                    <div class="shot-label">台词：</div>
                    <div v-if="!isEditing" class="shot-value dialogue-text">{{ shot.dialogue }}</div>
                    <el-input
                      v-else
                      v-model="shot.dialogue"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入台词"
                    />
                  </div>
                  
                  <div class="shot-item" v-if="shot.action || isEditing">
                    <div class="shot-label">动作：</div>
                    <div v-if="!isEditing" class="shot-value">{{ shot.action }}</div>
                    <el-input
                      v-else
                      v-model="shot.action"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入动作"
                    />
                  </div>
                  
                  <div class="shot-item" v-if="shot.music || isEditing">
                    <div class="shot-label">音乐：</div>
                    <div v-if="!isEditing" class="shot-value">{{ shot.music }}</div>
                    <el-input
                      v-else
                      v-model="shot.music"
                      placeholder="请输入音乐"
                    />
                  </div>
                  
                  <div class="shot-item" v-if="shot.purpose || isEditing">
                    <div class="shot-label">作用：</div>
                    <div v-if="!isEditing" class="shot-value">{{ shot.purpose }}</div>
                    <el-input
                      v-else
                      v-model="shot.purpose"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入作用"
                    />
                  </div>
                  
                  <div class="shot-item" v-if="shot.shaping_point || isEditing">
                    <div class="shot-label">塑造点：</div>
                    <div v-if="!isEditing" class="shot-value">{{ shot.shaping_point }}</div>
                    <el-input
                      v-else
                      v-model="shot.shaping_point"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入塑造点"
                    />
                  </div>
                  
                  <div v-if="isEditing" class="shot-item">
                    <div class="shot-label">时间区间：</div>
                    <el-input
                      v-model="shot.time_range"
                      placeholder="如：0-3秒"
                      style="width: 150px"
                    />
                  </div>
                  
                  <div v-if="isEditing" class="shot-item">
                    <div class="shot-label">景别：</div>
                    <el-select v-model="shot.shot_type" placeholder="选择景别" style="width: 150px">
                      <el-option label="全景" value="全景" />
                      <el-option label="中景" value="中景" />
                      <el-option label="近景" value="近景" />
                      <el-option label="特写" value="特写" />
                      <el-option label="大特写" value="大特写" />
                    </el-select>
                  </div>
                </div>
              </el-card>
              
              <!-- 添加新分镜按钮 -->
              <el-button
                v-if="isEditing"
                type="primary"
                plain
                @click="addNewShot"
                style="width: 100%; margin-top: 16px"
              >
                + 添加新分镜
              </el-button>
            </div>
            
            <!-- 如果没有分镜列表，显示原始脚本内容 -->
            <div v-else class="script-content-fallback">
              <el-input
                :model-value="isEditing ? editingScript?.script_content : selectedScript?.script_content"
                @update:model-value="handleScriptContentUpdate"
                type="textarea"
                :rows="15"
                :readonly="!isEditing"
                class="script-textarea"
                placeholder="请输入脚本内容"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="分镜表格">
            <div class="edit-toolbar">
              <el-button
                v-if="!isEditing"
                type="primary"
                size="small"
                @click="startEdit('shots')"
              >
                编辑
              </el-button>
              <div v-else class="edit-actions">
                <el-button type="success" size="small" @click="saveEdit">保存</el-button>
                <el-button size="small" @click="cancelEdit">取消</el-button>
              </div>
            </div>
            
            <el-table :data="(isEditing ? editingScript : selectedScript).shot_list" stripe>
              <el-table-column prop="shot_number" label="镜头" width="80" />
              <el-table-column prop="time_range" label="时间" width="100">
                <template #default="{ row, $index }">
                  <span v-if="!isEditing">{{ row.time_range }}</span>
                  <el-input
                    v-else
                    v-model="row.time_range"
                    size="small"
                    placeholder="0-3秒"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="shot_type" label="景别" width="100">
                <template #default="{ row }">
                  <span v-if="!isEditing">{{ row.shot_type }}</span>
                  <el-select
                    v-else
                    v-model="row.shot_type"
                    size="small"
                    placeholder="景别"
                  >
                    <el-option label="全景" value="全景" />
                    <el-option label="中景" value="中景" />
                    <el-option label="近景" value="近景" />
                    <el-option label="特写" value="特写" />
                    <el-option label="大特写" value="大特写" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="画面内容" min-width="150">
                <template #default="{ row }">
                  <span v-if="!isEditing">{{ row.content }}</span>
                  <el-input
                    v-else
                    v-model="row.content"
                    type="textarea"
                    :rows="2"
                    placeholder="画面内容"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="dialogue" label="台词" min-width="150">
                <template #default="{ row }">
                  <span v-if="!isEditing">{{ row.dialogue }}</span>
                  <el-input
                    v-else
                    v-model="row.dialogue"
                    type="textarea"
                    :rows="2"
                    placeholder="台词"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="action" label="动作" width="120">
                <template #default="{ row }">
                  <span v-if="!isEditing">{{ row.action }}</span>
                  <el-input
                    v-else
                    v-model="row.action"
                    placeholder="动作"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="purpose" label="作用" width="120">
                <template #default="{ row }">
                  <span v-if="!isEditing">{{ row.purpose }}</span>
                  <el-input
                    v-else
                    v-model="row.purpose"
                    placeholder="作用"
                  />
                </template>
              </el-table-column>
              <el-table-column v-if="isEditing" label="操作" width="100" fixed="right">
                <template #default="{ $index }">
                  <el-button
                    type="danger"
                    size="small"
                    text
                    @click="removeShot($index)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 添加新分镜按钮 -->
            <el-button
              v-if="isEditing"
              type="primary"
              plain
              @click="addNewShot"
              style="width: 100%; margin-top: 16px"
            >
              + 添加新分镜
            </el-button>
          </el-tab-pane>
          <el-tab-pane label="制作要点">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="拍摄要点">
                <ul>
                  <li v-for="tip in selectedScript.production_notes?.shooting_tips" :key="tip">
                    {{ tip }}
                  </li>
                </ul>
              </el-descriptions-item>
              <el-descriptions-item label="剪辑要点">
                <ul>
                  <li v-for="tip in selectedScript.production_notes?.editing_tips" :key="tip">
                    {{ tip }}
                  </li>
                </ul>
              </el-descriptions-item>
              <el-descriptions-item label="关键要点">
                <ul>
                  <li v-for="point in selectedScript.production_notes?.key_points" :key="point">
                    {{ point }}
                  </li>
                </ul>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 重新生成对话框 -->
    <el-dialog v-model="regenerateVisible" title="重新生成脚本" width="600px">
      <el-form :model="regenerateForm" label-width="100px">
        <el-form-item label="调整意见" required>
          <el-input
            v-model="regenerateForm.adjustment_feedback"
            type="textarea"
            :rows="6"
            placeholder="请输入您对当前脚本的调整意见，例如：&#10;1. 希望增加更多商品卖点的展示&#10;2. 开头钩子需要更有吸引力&#10;3. 台词需要更加简洁有力&#10;4. 希望增加特写镜头展示细节"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="regenerateVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitRegenerate"
          :loading="regenerating"
          :disabled="!regenerateForm.adjustment_feedback || !regenerateForm.adjustment_feedback.trim()"
        >
          确定重新生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 优化建议对话框 -->
    <el-dialog v-model="optimizeVisible" title="优化建议" width="700px">
      <div v-if="optimizing" class="optimizing-loading">
        <el-skeleton :rows="3" animated />
        <div style="text-align: center; margin-top: 20px; color: #909399;">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span style="margin-left: 8px;">AI正在分析脚本，请稍候...</span>
        </div>
      </div>
      <div v-else-if="optimizeSuggestions && optimizeSuggestions.length > 0" class="optimize-suggestions">
        <div class="suggestions-header">
          <span class="suggestions-count">共 {{ optimizeSuggestions.length }} 条优化建议</span>
          <el-button
            type="primary"
            :loading="applying"
            @click="applyAllSuggestions"
          >
            <el-icon><Check /></el-icon>
            一键应用所有建议
          </el-button>
        </div>
        <el-alert
          v-for="(suggestion, index) in optimizeSuggestions"
          :key="index"
          :title="suggestion.message || suggestion.name || `建议 ${index + 1}`"
          :type="getSuggestionType(suggestion.level)"
          :closable="false"
          style="margin-bottom: 12px"
        >
          <template #default>
            <div class="suggestion-content">
              <div class="suggestion-message">{{ suggestion.message || suggestion.description || '' }}</div>
              <div v-if="suggestion.suggestion" class="suggestion-advice">
                <strong>建议：</strong>{{ suggestion.suggestion }}
              </div>
              <div class="suggestion-actions">
                <el-button
                  type="primary"
                  size="small"
                  text
                  :loading="applying"
                  @click="applySingleSuggestion(suggestion, index)"
                >
                  应用此建议
                </el-button>
              </div>
            </div>
          </template>
        </el-alert>
      </div>
      <div v-else class="no-suggestions">
        <el-empty description="暂无优化建议，脚本质量良好！" :image-size="100" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Check, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { scriptsApi, type Script, type GenerateScriptRequest } from '@/api/scripts'
import { hotspotsApi, type Hotspot } from '@/api/hotspots'
import { productsApi, type Product } from '@/api/products'
import { analysisApi, type AnalysisReport } from '@/api/analysis'
import { tasksApi, type TaskStatus } from '@/api/tasks'

const loading = ref(false)
const scripts = ref<Script[]>([])
const hotspots = ref<Hotspot[]>([])
const products = ref<Product[]>([])
const reports = ref<AnalysisReport[]>([])
const detailVisible = ref(false)
const generateVisible = ref(false)
const optimizeVisible = ref(false)
const regenerateVisible = ref(false) // 重新生成对话框显示状态
const regenerating = ref(false) // 重新生成加载状态
const currentRegeneratingScript = ref<Script | null>(null) // 当前正在重新生成的脚本
const regenerateForm = ref({
  adjustment_feedback: ''
})
const selectedScript = ref<Script | null>(null)
const editingScript = ref<Script | null>(null) // 编辑中的脚本副本
const isEditing = ref(false)
const editingTab = ref('content') // 当前编辑的tab: 'content' | 'shots'
const optimizeSuggestions = ref<any[]>([])
const optimizing = ref(false) // 优化建议加载状态
const applying = ref(false) // 应用建议加载状态
const currentOptimizingScript = ref<Script | null>(null) // 当前正在优化的脚本
const router = useRouter()

// 脚本生成任务状态
const generatingScript = ref(false) // 是否正在生成脚本
const currentScriptTaskId = ref<string | null>(null) // 当前脚本生成任务ID
const scriptTaskStatus = ref<TaskStatus | null>(null) // 脚本生成任务状态
let scriptTaskPollingInterval: number | null = null // 任务轮询定时器

const filters = ref({
  product_id: '',
  status: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const generateForm = ref<GenerateScriptRequest>({
  hotspot_id: '',
  product_id: '',
  analysis_report_id: '',
  duration: 10,
  script_count: 5  // 默认生成5个不同的脚本
})

const loadScripts = async () => {
  loading.value = true
  try {
    const response = await scriptsApi.getScripts({
      product_id: filters.value.product_id || undefined,
      status: filters.value.status || undefined,
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    })
    scripts.value = response.items
    pagination.value.total = response.total
  } catch (error: any) {
    ElMessage.error('加载脚本失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadHotspots = async () => {
  try {
    const response = await hotspotsApi.getHotspots({ limit: 100 })
    hotspots.value = response.items
  } catch (error) {
    console.error('加载热点失败:', error)
  }
}

const loadProducts = async () => {
  try {
    const response = await productsApi.getProducts({ limit: 100 })
    products.value = response.items
  } catch (error) {
    console.error('加载商品失败:', error)
  }
}

const loadReports = async () => {
  try {
    const response = await analysisApi.getReports({ limit: 100 })
    reports.value = response.items
  } catch (error) {
    console.error('加载报告失败:', error)
  }
}

const handleGenerate = () => {
  generateForm.value = {
    hotspot_id: '',
    product_id: '',
    analysis_report_id: '',
    duration: 10,
    script_count: 5  // 默认生成5个不同的脚本
  }
  generateVisible.value = true
}

const submitGenerate = async () => {
  if (!generateForm.value.hotspot_id || !generateForm.value.product_id) {
    ElMessage.warning('请选择热点和商品')
    return
  }

  try {
    const response = await scriptsApi.generateScript(generateForm.value)
    currentScriptTaskId.value = response.task_id
    generatingScript.value = true
    generateVisible.value = false
    
    // 开始轮询任务状态
    startScriptTaskPolling()
    
    // 自动跳转到脚本管理页面（如果不在当前页面）
    if (router.currentRoute.value.path !== '/scripts') {
      router.push('/scripts')
    }
  } catch (error: any) {
    ElMessage.error('生成脚本失败: ' + (error.message || '未知错误'))
    generatingScript.value = false
    currentScriptTaskId.value = null
  }
}

// 开始轮询脚本生成任务状态
const startScriptTaskPolling = () => {
  if (scriptTaskPollingInterval) {
    clearInterval(scriptTaskPollingInterval)
  }
  
  scriptTaskPollingInterval = window.setInterval(async () => {
    if (!currentScriptTaskId.value) {
      stopScriptTaskPolling()
      return
    }
    
    try {
      const status = await tasksApi.getTaskStatus(currentScriptTaskId.value)
      scriptTaskStatus.value = status
      
      if (status.state === 'SUCCESS') {
        ElMessage.success('脚本生成完成！')
        stopScriptTaskPolling()
        generatingScript.value = false
        currentScriptTaskId.value = null
        scriptTaskStatus.value = null
        // 刷新脚本列表
        await loadScripts()
      } else if (status.state === 'FAILURE') {
        ElMessage.error('脚本生成失败: ' + (status.error || '未知错误'))
        stopScriptTaskPolling()
        generatingScript.value = false
        currentScriptTaskId.value = null
        scriptTaskStatus.value = null
      }
    } catch (error) {
      console.error('获取脚本生成任务状态失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

// 停止轮询脚本生成任务状态
const stopScriptTaskPolling = () => {
  if (scriptTaskPollingInterval) {
    clearInterval(scriptTaskPollingInterval)
    scriptTaskPollingInterval = null
  }
}

const viewDetail = async (script: Script) => {
  try {
    const detail = await scriptsApi.getScriptDetail(script.id)
    selectedScript.value = detail
    isEditing.value = false
    editingScript.value = null
    detailVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取详情失败: ' + (error.message || '未知错误'))
  }
}

const startEdit = (tab: 'content' | 'shots') => {
  if (!selectedScript.value) return
  
  editingTab.value = tab
  // 深拷贝脚本数据用于编辑
  editingScript.value = JSON.parse(JSON.stringify(selectedScript.value))
  
  // 确保shot_list是数组
  if (!editingScript.value.shot_list) {
    editingScript.value.shot_list = []
  }
  
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editingScript.value = null
  editingTab.value = 'content'
}

const saveEdit = async () => {
  if (!editingScript.value || !selectedScript.value) return
  
  try {
    // 更新shot_list中的shot_number
    if (editingScript.value.shot_list) {
      editingScript.value.shot_list.forEach((shot: any, index: number) => {
        shot.shot_number = shot.shot_number || index + 1
      })
    }
    
    // 调用API保存
    await scriptsApi.updateScript(selectedScript.value.id, {
      script_content: editingScript.value.script_content,
      shot_list: editingScript.value.shot_list
    })
    
    // 更新显示的数据
    selectedScript.value.script_content = editingScript.value.script_content
    selectedScript.value.shot_list = editingScript.value.shot_list
    
    ElMessage.success('保存成功')
    isEditing.value = false
    editingScript.value = null
    
    // 刷新列表
    await loadScripts()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

const addNewShot = () => {
  if (!editingScript.value) return
  
  if (!editingScript.value.shot_list) {
    editingScript.value.shot_list = []
  }
  
  const newShot = {
    shot_number: editingScript.value.shot_list.length + 1,
    time_range: '',
    shot_type: '',
    content: '',
    dialogue: '',
    action: '',
    music: '',
    purpose: '',
    shaping_point: ''
  }
  
  editingScript.value.shot_list.push(newShot)
}

const removeShot = (index: number) => {
  if (!editingScript.value || !editingScript.value.shot_list) return
  
  editingScript.value.shot_list.splice(index, 1)
  
  // 重新编号
  editingScript.value.shot_list.forEach((shot: any, i: number) => {
    shot.shot_number = i + 1
  })
}

const handleScriptContentUpdate = (value: string) => {
  if (isEditing.value && editingScript.value) {
    editingScript.value.script_content = value
  }
}

const handleOptimize = async (script: Script) => {
  // 先打开对话框并显示加载状态
  optimizeVisible.value = true
  optimizing.value = true
  optimizeSuggestions.value = []
  currentOptimizingScript.value = script
  
  try {
    const response = await scriptsApi.optimizeScript(script.id)
    console.log('优化建议响应:', response)
    
    // 确保suggestions是数组
    if (response && response.suggestions) {
      optimizeSuggestions.value = Array.isArray(response.suggestions) 
        ? response.suggestions 
        : [response.suggestions]
    } else {
      optimizeSuggestions.value = []
    }
    
    if (optimizeSuggestions.value.length === 0) {
      ElMessage.info('脚本质量良好，暂无优化建议')
    }
  } catch (error: any) {
    console.error('获取优化建议失败:', error)
    ElMessage.error('获取优化建议失败: ' + (error.message || '未知错误'))
    optimizeSuggestions.value = []
  } finally {
    optimizing.value = false
  }
}

const applyAllSuggestions = async () => {
  if (!currentOptimizingScript.value || optimizeSuggestions.value.length === 0) {
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要应用所有 ${optimizeSuggestions.value.length} 条优化建议吗？这将修改脚本内容。`,
      '确认应用',
      {
        confirmButtonText: '确定应用',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    applying.value = true
    
    // 获取最新的脚本数据
    const script = await scriptsApi.getScriptDetail(currentOptimizingScript.value.id)
    
    // 应用所有建议
    const updatedScript = await applySuggestionsToScript(script, optimizeSuggestions.value)
    
    // 保存到后端
    await scriptsApi.updateScript(script.id, {
      script_content: updatedScript.script_content,
      shot_list: updatedScript.shot_list,
      video_info: updatedScript.video_info
    })
    
    ElMessage.success('所有优化建议已成功应用！')
    
    // 刷新列表
    await loadScripts()
    
    // 如果当前正在查看这个脚本的详情，刷新详情数据
    if (selectedScript.value && selectedScript.value.id === script.id) {
      const updatedDetail = await scriptsApi.getScriptDetail(script.id)
      selectedScript.value = updatedDetail
      // 如果正在编辑，也更新编辑中的数据
      if (isEditing.value && editingScript.value) {
        editingScript.value = JSON.parse(JSON.stringify(updatedDetail))
      }
    }
    
    // 关闭对话框
    optimizeVisible.value = false
    optimizeSuggestions.value = []
    currentOptimizingScript.value = null
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('应用优化建议失败:', error)
      ElMessage.error('应用优化建议失败: ' + (error.message || '未知错误'))
    }
  } finally {
    applying.value = false
  }
}

const applySingleSuggestion = async (suggestion: any, index: number) => {
  if (!currentOptimizingScript.value) {
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要应用这条优化建议吗？\n\n${suggestion.message}\n\n${suggestion.suggestion || ''}`,
      '确认应用',
      {
        confirmButtonText: '确定应用',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    applying.value = true
    
    // 获取最新的脚本数据
    const script = await scriptsApi.getScriptDetail(currentOptimizingScript.value.id)
    
    // 应用单个建议
    const updatedScript = await applySuggestionsToScript(script, [suggestion])
    
    // 保存到后端
    await scriptsApi.updateScript(script.id, {
      script_content: updatedScript.script_content,
      shot_list: updatedScript.shot_list,
      video_info: updatedScript.video_info
    })
    
    ElMessage.success('优化建议已成功应用！')
    
    // 从列表中移除已应用的建议
    optimizeSuggestions.value.splice(index, 1)
    
    // 刷新列表
    await loadScripts()
    
    // 如果当前正在查看这个脚本的详情，刷新详情数据
    if (selectedScript.value && selectedScript.value.id === script.id) {
      const updatedDetail = await scriptsApi.getScriptDetail(script.id)
      selectedScript.value = updatedDetail
      // 如果正在编辑，也更新编辑中的数据
      if (isEditing.value && editingScript.value) {
        editingScript.value = JSON.parse(JSON.stringify(updatedDetail))
      }
    }
    
    // 如果没有建议了，关闭对话框
    if (optimizeSuggestions.value.length === 0) {
      optimizeVisible.value = false
      currentOptimizingScript.value = null
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('应用优化建议失败:', error)
      ElMessage.error('应用优化建议失败: ' + (error.message || '未知错误'))
    }
  } finally {
    applying.value = false
  }
}

const applySuggestionsToScript = async (script: Script, suggestions: any[]): Promise<Script> => {
  // 深拷贝脚本数据
  const updatedScript = JSON.parse(JSON.stringify(script))
  
  // 确保必要字段存在
  if (!updatedScript.shot_list) {
    updatedScript.shot_list = []
  }
  if (!updatedScript.video_info) {
    updatedScript.video_info = {}
  }
  
  // 应用每条建议
  for (const suggestion of suggestions) {
    const suggestionText = (suggestion.suggestion || suggestion.message || '').toLowerCase()
    const type = suggestion.type || ''
    
    // 根据建议类型应用修改
    if (type.includes('时长') || type.includes('节奏') || suggestionText.includes('延长') || suggestionText.includes('缩短')) {
      // 处理时长和节奏相关建议
      if (suggestionText.includes('15秒') || suggestionText.includes('延长至15秒')) {
        updatedScript.video_info.duration = 15
      } else if (suggestionText.includes('10秒')) {
        updatedScript.video_info.duration = 10
      }
      
      // 调整分镜时间
      if (updatedScript.shot_list && updatedScript.shot_list.length > 0) {
        updatedScript.shot_list.forEach((shot: any, index: number) => {
          // 根据建议调整时间区间
          if (suggestionText.includes(`镜头${index + 1}`) || suggestionText.includes(`镜头 ${index + 1}`)) {
            if (suggestionText.includes('4秒')) {
              shot.time_range = `${index * 4}-${(index + 1) * 4}秒`
            } else if (suggestionText.includes('2秒')) {
              shot.time_range = `${index * 2}-${(index + 1) * 2}秒`
            }
          }
        })
      }
    }
    
    if (type.includes('内容') || type.includes('卖点') || suggestionText.includes('卖点') || suggestionText.includes('台词')) {
      // 处理内容相关建议
      if (updatedScript.shot_list && updatedScript.shot_list.length > 0) {
        updatedScript.shot_list.forEach((shot: any, index: number) => {
          if (suggestionText.includes(`镜头${index + 1}`) || suggestionText.includes(`镜头 ${index + 1}`)) {
            // 添加卖点描述
            if (suggestionText.includes('卖点') || suggestionText.includes('优势')) {
              if (!shot.dialogue) shot.dialogue = ''
              if (suggestionText.includes('亲肤') || suggestionText.includes('柔软')) {
                shot.dialogue += ' 亲肤柔软'
              }
              if (suggestionText.includes('保暖') || suggestionText.includes('透气')) {
                shot.dialogue += ' 保暖透气'
              }
              if (suggestionText.includes('不起球')) {
                shot.dialogue += ' 不起球'
              }
              if (suggestionText.includes('性价比')) {
                shot.dialogue += ' 性价比超高'
              }
            }
            
            // 添加引导语
            if (suggestionText.includes('引导') || suggestionText.includes('购买') || suggestionText.includes('小黄车')) {
              if (!shot.dialogue) shot.dialogue = ''
              shot.dialogue += ' 点击下方小黄车立即购买'
            }
          }
        })
      }
    }
    
    if (type.includes('视觉') || suggestionText.includes('画面') || suggestionText.includes('构图')) {
      // 处理视觉相关建议
      if (updatedScript.shot_list && updatedScript.shot_list.length > 0) {
        updatedScript.shot_list.forEach((shot: any, index: number) => {
          if (suggestionText.includes(`镜头${index + 1}`) || suggestionText.includes(`镜头 ${index + 1}`)) {
            // 添加视觉效果描述
            if (suggestionText.includes('慢动作')) {
              if (!shot.action) shot.action = ''
              shot.action += ' 慢动作转身'
            }
            if (suggestionText.includes('微距') || suggestionText.includes('特写')) {
              if (!shot.shot_type) shot.shot_type = '特写'
              if (!shot.content) shot.content = ''
              shot.content += ' 微距特写展示细节'
            }
            if (suggestionText.includes('动画') || suggestionText.includes('箭头')) {
              if (!shot.action) shot.action = ''
              shot.action += ' 添加箭头动画'
            }
          }
        })
      }
    }
  }
  
  return updatedScript
}

const handleRegenerate = (script: Script) => {
  currentRegeneratingScript.value = script
  regenerateForm.value.adjustment_feedback = ''
  regenerateVisible.value = true
}

const submitRegenerate = async () => {
  if (!currentRegeneratingScript.value) return
  
  if (!regenerateForm.value.adjustment_feedback || !regenerateForm.value.adjustment_feedback.trim()) {
    ElMessage.warning('请输入调整意见')
    return
  }

  try {
    regenerating.value = true
    const response = await scriptsApi.regenerateScript(currentRegeneratingScript.value.id, {
      adjustment_feedback: regenerateForm.value.adjustment_feedback.trim()
    })
    
    currentScriptTaskId.value = response.task_id
    generatingScript.value = true
    regenerateVisible.value = false
    regenerateForm.value.adjustment_feedback = ''
    currentRegeneratingScript.value = null
    
    // 开始轮询任务状态
    startScriptTaskPolling()
    
    ElMessage.success('脚本重新生成任务已启动')
  } catch (error: any) {
    ElMessage.error('重新生成脚本失败: ' + (error.message || '未知错误'))
  } finally {
    regenerating.value = false
  }
}

const handleReview = async (script: Script, action: 'approve' | 'reject') => {
  try {
    await scriptsApi.reviewScript(script.id, action)
    ElMessage.success(action === 'approve' ? '审核通过' : '审核拒绝')
    loadScripts()
  } catch (error: any) {
    ElMessage.error('审核失败: ' + (error.message || '未知错误'))
  }
}

const resetFilters = () => {
  filters.value = { product_id: '', status: '' }
  loadScripts()
}

const getStatusType = (status?: string) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status?: string) => {
  switch (status) {
    case 'approved': return '已审核'
    case 'rejected': return '已拒绝'
    default: return '草稿'
  }
}

const getSuggestionType = (level?: string) => {
  switch (level) {
    case 'error': return 'error'
    case 'warning': return 'warning'
    case 'info': 
    default: return 'info'
  }
}

// 脚本生成任务状态文本
const scriptTaskStatusText = computed(() => {
  if (generatingScript.value && !scriptTaskStatus.value) {
    return '脚本生成任务已启动...'
  }
  
  if (!scriptTaskStatus.value) {
    return ''
  }
  
  if (scriptTaskStatus.value.status) {
    return scriptTaskStatus.value.status
  }
  
  switch (scriptTaskStatus.value.state) {
    case 'PENDING':
      return '等待生成...'
    case 'PROGRESS':
      return scriptTaskStatus.value.status || '正在生成脚本...'
    case 'SUCCESS':
      return '脚本生成完成！'
    case 'FAILURE':
      return '脚本生成失败: ' + (scriptTaskStatus.value.error || '未知错误')
    default:
      return `任务状态: ${scriptTaskStatus.value.state || '未知'}`
  }
})

onMounted(() => {
  loadHotspots()
  loadProducts()
  loadReports()
  loadScripts()
})

onBeforeUnmount(() => {
  stopScriptTaskPolling()
})
</script>

<style scoped>
.scripts-view {
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

.scripts-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scripts-list :deep(.el-card__body) {
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

.scripts-list :deep(.el-table) {
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.scripts-list :deep(.el-table__header) {
  background: linear-gradient(to right, #fdf2f8, #fff7ed);
}

.scripts-list :deep(.el-table__row:hover) {
  background: rgba(249, 250, 251, 0.5);
}

/* 状态标签样式 */
.status-badge {
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
}

.status-draft {
  background: #fef3c7;
  color: #92400e;
}

.status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

/* 分镜列表样式 */
.shot-list-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px 0;
}

.shot-card {
  margin-bottom: 16px;
  border-left: 4px solid #409eff;
  transition: all 0.3s;
}

.shot-card:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.shot-card:last-child {
  margin-bottom: 0;
}

.shot-header {
  display: flex;
  gap: 8px;
  align-items: center;
}

.shot-content {
  padding: 8px 0;
}

.shot-item {
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
}

.shot-item:last-child {
  margin-bottom: 0;
}

.shot-label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  flex-shrink: 0;
  margin-right: 8px;
  font-size: 14px;
}

.shot-value {
  flex: 1;
  color: #303133;
  line-height: 1.8;
  word-break: break-word;
  font-size: 14px;
}

.dialogue-text {
  font-size: 15px;
  color: #409eff;
  font-weight: 500;
  padding: 10px 14px;
  background: #ecf5ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  margin-top: 4px;
}

.script-content-fallback {
  padding: 10px 0;
}

.script-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.8;
}

.script-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.8;
  padding: 15px;
}

/* 优化建议对话框样式 */
.optimize-suggestions {
  padding: 10px 0;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.suggestions-count {
  color: #606266;
  font-size: 14px;
}

.suggestion-content {
  padding: 8px 0;
}

.suggestion-actions {
  margin-top: 12px;
  text-align: right;
}

.suggestion-message {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.6;
}

.suggestion-advice {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-top: 8px;
}

.suggestion-advice strong {
  color: #409eff;
  margin-right: 4px;
}

.no-suggestions {
  padding: 40px 0;
  text-align: center;
}

/* 编辑工具栏 */
.edit-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

/* 编辑模式下的样式调整 */
.shot-card :deep(.el-input),
.shot-card :deep(.el-textarea),
.shot-card :deep(.el-select) {
  width: 100%;
}

.shot-item {
  margin-bottom: 12px;
}

.shot-item:last-child {
  margin-bottom: 0;
}

/* 优化建议加载状态 */
.optimizing-loading {
  padding: 20px 0;
}

.optimizing-loading .el-icon {
  font-size: 20px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

