<template>
  <div class="process-models">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程模型列表</span>
          <el-button type="primary" @click="$router.push('/mining/discover')">
            <el-icon><Plus /></el-icon>
            新建模型
          </el-button>
        </div>
      </template>
      
      <el-table :data="models" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="模型名称" min-width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="algorithm" label="算法" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getAlgorithmTagType(scope.row.algorithm)" size="small">
              {{ getAlgorithmName(scope.row.algorithm) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="event_log_id" label="关联日志" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="viewDetail(scope.row)">查看</el-button>
            <el-button type="success" link @click="viewImage(scope.row)">流程图</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="models.length === 0 && !loading" description="暂无流程模型，请先进行流程发现">
        <el-button type="primary" @click="$router.push('/mining/discover')">去流程发现</el-button>
      </el-empty>
    </el-card>

    <el-dialog v-model="detailVisible" title="模型详情" width="700px">
      <div v-if="selectedModel">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ selectedModel.name }}</el-descriptions-item>
          <el-descriptions-item label="ID">{{ selectedModel.id }}</el-descriptions-item>
          <el-descriptions-item label="使用算法">
            <el-tag :type="getAlgorithmTagType(selectedModel.algorithm)" size="small">
              {{ getAlgorithmName(selectedModel.algorithm) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="关联日志ID">{{ selectedModel.event_log_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedModel.description || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatTime(selectedModel.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="section-title" v-if="modelMetrics">质量指标</div>
        <el-row :gutter="20" v-if="modelMetrics">
          <el-col :span="6">
            <el-statistic title="适应度" :value="modelMetrics.fitness * 100" :precision="1">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="精确度" :value="modelMetrics.precision * 100" :precision="1">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="泛化度" :value="modelMetrics.generalization * 100" :precision="1">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="简单度" :value="modelMetrics.simplicity * 100" :precision="1">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>
    </el-dialog>

    <el-dialog v-model="imageVisible" title="流程模型图" width="900px">
      <div v-if="selectedModel && selectedModel.image_path" class="image-container">
        <img 
          :src="`/api/mining/model-image/${selectedModel.image_path}`" 
          alt="流程模型图"
          class="model-image"
        />
      </div>
      <el-empty v-else description="暂无模型图片" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProcessModels, deleteProcessModel } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const models = ref([])
const selectedModel = ref(null)
const modelMetrics = ref(null)
const detailVisible = ref(false)
const imageVisible = ref(false)

const loadModels = async () => {
  loading.value = true
  try {
    const res = await getProcessModels()
    models.value = res.data || []
  } catch (error) {
    console.error('加载流程模型失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getAlgorithmName = (algorithm) => {
  const names = {
    'alpha': 'Alpha算法',
    'inductive': '归纳挖掘算法',
    'heuristics': '启发式挖掘算法'
  }
  return names[algorithm] || algorithm
}

const getAlgorithmTagType = (algorithm) => {
  const types = {
    'alpha': 'primary',
    'inductive': 'success',
    'heuristics': 'warning'
  }
  return types[algorithm] || 'info'
}

const viewDetail = (row) => {
  selectedModel.value = row
  
  // 解析模型数据中的指标
  if (row.model_data) {
    try {
      const modelData = JSON.parse(row.model_data)
      modelMetrics.value = modelData.metrics
    } catch (e) {
      modelMetrics.value = null
    }
  }
  
  detailVisible.value = true
}

const viewImage = (row) => {
  selectedModel.value = row
  imageVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除流程模型 "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteProcessModel(row.id)
    if (res.data.success) {
      ElMessage.success(res.data.message)
      loadModels()
    } else {
      ElMessage.error(res.data.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.image-container {
  width: 100%;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.model-image {
  max-width: 100%;
  max-height: 600px;
}
</style>
