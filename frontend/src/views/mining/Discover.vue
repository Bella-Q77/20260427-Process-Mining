<template>
  <div class="process-discover">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程发现</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择事件日志">
          <el-select 
            v-model="form.logId" 
            placeholder="请选择事件日志" 
            style="width: 400px;"
            @change="handleLogChange"
          >
            <el-option 
              v-for="log in logs" 
              :key="log.id" 
              :label="log.name" 
              :value="log.id"
            >
              <span style="float: left">{{ log.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ log.case_count }}案例 / {{ log.event_count }}事件
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择算法">
          <el-radio-group v-model="form.algorithm">
            <el-radio v-for="algo in algorithms" :key="algo.id" :value="algo.id">
              <div class="radio-content">
                <div class="radio-title">{{ algo.name }}</div>
                <div class="radio-desc">{{ algo.description }}</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="模型名称">
          <el-input 
            v-model="form.modelName" 
            placeholder="请输入模型名称（可选）" 
            style="width: 400px;"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleDiscover" 
            :loading="loading"
            :disabled="!form.logId"
          >
            <el-icon><Search /></el-icon>
            开始流程发现
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="discoverResult" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>发现结果</span>
          <div>
            <el-tag type="success" style="margin-right: 10px;">
              算法: {{ discoverResult.algorithm_name }}
            </el-tag>
            <el-button type="primary" link @click="refreshDiscover">重新发现</el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="section-title">流程模型图</div>
          <div class="model-image-container">
            <img 
              v-if="discoverResult.image_path" 
              :src="discoverResult.image_path" 
              alt="流程模型"
              class="model-image"
            />
            <el-empty v-else description="模型图生成中..." />
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="section-title">质量指标</div>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="适应度 (Fitness)">
              <el-progress 
                :percentage="discoverResult.metrics.fitness * 100" 
                :color="getMetricColor(discoverResult.metrics.fitness)"
                :stroke-width="15"
              />
            </el-descriptions-item>
            <el-descriptions-item label="精确度 (Precision)">
              <el-progress 
                :percentage="discoverResult.metrics.precision * 100" 
                :color="getMetricColor(discoverResult.metrics.precision)"
                :stroke-width="15"
              />
            </el-descriptions-item>
            <el-descriptions-item label="泛化度 (Generalization)">
              <el-progress 
                :percentage="discoverResult.metrics.generalization * 100" 
                :color="getMetricColor(discoverResult.metrics.generalization)"
                :stroke-width="15"
              />
            </el-descriptions-item>
            <el-descriptions-item label="简单度 (Simplicity)">
              <el-progress 
                :percentage="discoverResult.metrics.simplicity * 100" 
                :color="getMetricColor(discoverResult.metrics.simplicity)"
                :stroke-width="15"
              />
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="section-title" style="margin-top: 20px;">指标说明</div>
          <el-alert type="info" :closable="false" size="small">
            <template #title>
              <div style="font-weight: normal; font-size: 12px; line-height: 1.6;">
                <strong>适应度</strong>: 衡量日志中轨迹能够被模型重放的程度<br/>
                <strong>精确度</strong>: 衡量模型不允许额外行为的程度<br/>
                <strong>泛化度</strong>: 衡量模型能够处理日志中未见过的行为的程度<br/>
                <strong>简单度</strong>: 衡量模型的简洁程度
              </div>
            </template>
          </el-alert>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <div class="section-title">活动分析</div>
      <el-table :data="discoverResult.activities || []" size="small">
        <el-table-column prop="name" label="活动名称" />
        <el-table-column prop="count" label="出现次数" align="center" />
        <el-table-column label="案例覆盖率" align="center">
          <template #default="scope">
            {{ (scope.row.trace_coverage * 100).toFixed(1) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-if="!logs.length && !loading" style="margin-top: 20px;">
      <el-empty description="暂无事件日志，请先生成模拟数据">
        <el-button type="primary" @click="$router.push('/simulation/generate')">生成模拟数据</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getEventLogs, discoverProcess, getAlgorithmsInfo } from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const logs = ref([])
const algorithms = ref([])
const discoverResult = ref(null)

const form = reactive({
  logId: null,
  algorithm: 'heuristics',
  modelName: ''
})

const loadLogs = async () => {
  try {
    const res = await getEventLogs()
    logs.value = res.data || []
    
    // 如果URL中有logId参数，自动选择
    if (route.query.logId) {
      const logId = parseInt(route.query.logId)
      const log = logs.value.find(l => l.id === logId)
      if (log) {
        form.logId = logId
      }
    }
  } catch (error) {
    console.error('加载事件日志失败:', error)
  }
}

const loadAlgorithms = async () => {
  try {
    const res = await getAlgorithmsInfo()
    if (res.data.success) {
      algorithms.value = res.data.algorithms
    }
  } catch (error) {
    console.error('加载算法信息失败:', error)
    // 使用默认算法信息
    algorithms.value = [
      { id: 'alpha', name: 'Alpha算法', description: '基于关系的流程发现算法，适用于结构化程度较好的流程' },
      { id: 'inductive', name: '归纳挖掘算法', description: '基于流程树的发现算法，保证模型健全性，能处理复杂结构' },
      { id: 'heuristics', name: '启发式挖掘算法', description: '基于频率的启发式方法，考虑活动依赖频率，能过滤噪声' }
    ]
  }
}

const getMetricColor = (value) => {
  if (value >= 0.8) return '#67C23A'
  if (value >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

const handleLogChange = () => {
  discoverResult.value = null
}

const handleDiscover = async () => {
  if (!form.logId) {
    ElMessage.warning('请先选择事件日志')
    return
  }
  
  loading.value = true
  try {
    const res = await discoverProcess({
      event_log_id: form.logId,
      algorithm: form.algorithm,
      model_name: form.modelName || undefined
    })
    
    if (res.data.success) {
      discoverResult.value = res.data.data
      ElMessage.success('流程发现成功')
    } else {
      ElMessage.error(res.data.error || '流程发现失败')
    }
  } catch (error) {
    console.error('流程发现失败:', error)
    ElMessage.error(error.response?.data?.error || '流程发现失败')
  } finally {
    loading.value = false
  }
}

const refreshDiscover = () => {
  discoverResult.value = null
}

onMounted(() => {
  loadLogs()
  loadAlgorithms()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.radio-content {
  padding: 5px 0;
}

.radio-title {
  font-weight: bold;
}

.radio-desc {
  font-size: 12px;
  color: #909399;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.model-image-container {
  width: 100%;
  min-height: 300px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.model-image {
  max-width: 100%;
  max-height: 500px;
}
</style>
