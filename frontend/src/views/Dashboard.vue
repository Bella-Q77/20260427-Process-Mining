<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #409EFF;">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.eventLogCount }}</div>
              <div class="stat-label">事件日志数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #67C23A;">
              <el-icon size="32"><Share /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.processModelCount }}</div>
              <div class="stat-label">流程模型数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #E6A23C;">
              <el-icon size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCases }}</div>
              <div class="stat-label">总案例数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #F56C6C;">
              <el-icon size="32"><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalEvents }}</div>
              <div class="stat-label">总事件数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速入门</span>
            </div>
          </template>
          <el-steps :active="currentStep" align-center>
            <el-step title="生成模拟数据" description="创建财务单据流程模拟数据">
              <template #icon>
                <el-button type="primary" @click="goToGenerate">
                  <el-icon><Plus /></el-icon>
                  生成数据
                </el-button>
              </template>
            </el-step>
            <el-step title="流程发现" description="使用算法发现流程模型">
              <template #icon>
                <el-button type="primary" @click="goToDiscover">
                  <el-icon><Search /></el-icon>
                  开始挖掘
                </el-button>
              </template>
            </el-step>
            <el-step title="分析优化" description="分析流程性能和瓶颈">
              <template #icon>
                <el-button type="primary" @click="goToAnalysis">
                  <el-icon><DataAnalysis /></el-icon>
                  查看分析
                </el-button>
              </template>
            </el-step>
          </el-steps>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统功能介绍</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="模拟数据生成">
              支持生成多种流程变体的财务单据模拟数据，包括正常流程、返工流程、大额审批流程等。
            </el-descriptions-item>
            <el-descriptions-item label="流程发现">
              提供Alpha算法、归纳挖掘算法、启发式挖掘算法等多种流程发现算法，自动从事件日志中发现业务流程模型。
            </el-descriptions-item>
            <el-descriptions-item label="流程分析">
              支持流程变体分析、性能分析、资源分析、部门分析等多维度分析，帮助识别流程瓶颈和优化点。
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近事件日志</span>
              <el-button type="primary" link @click="goToLogs">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentLogs" v-loading="loading" style="width: 100%">
            <el-table-column prop="name" label="日志名称" width="200" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="case_count" label="案例数" width="100" align="center" />
            <el-table-column prop="event_count" label="事件数" width="100" align="center" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="viewLogDetail(scope.row)">详情</el-button>
                <el-button type="primary" link @click="discoverFromLog(scope.row)">流程发现</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentLogs.length === 0 && !loading" description="暂无事件日志，请先生成模拟数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Share, User, Connection, Plus, Search, DataAnalysis } from '@element-plus/icons-vue'
import { getEventLogs, getProcessModels } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const currentStep = ref(0)
const recentLogs = ref([])
const stats = ref({
  eventLogCount: 0,
  processModelCount: 0,
  totalCases: 0,
  totalEvents: 0
})

const loadData = async () => {
  loading.value = true
  try {
    const [logsRes, modelsRes] = await Promise.all([
      getEventLogs(),
      getProcessModels()
    ])
    
    const logs = logsRes.data || []
    const models = modelsRes.data || []
    
    recentLogs.value = logs.slice(0, 5)
    stats.value.eventLogCount = logs.length
    stats.value.processModelCount = models.length
    
    // 计算总案例数和事件数
    stats.value.totalCases = logs.reduce((sum, log) => sum + (log.case_count || 0), 0)
    stats.value.totalEvents = logs.reduce((sum, log) => sum + (log.event_count || 0), 0)
    
    // 根据数据量设置当前步骤
    if (logs.length > 0) {
      currentStep.value = 1
    }
    if (models.length > 0) {
      currentStep.value = 2
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const goToGenerate = () => router.push('/simulation/generate')
const goToDiscover = () => router.push('/mining/discover')
const goToAnalysis = () => router.push('/mining/performance')
const goToLogs = () => router.push('/simulation/logs')

const viewLogDetail = (row) => {
  router.push(`/simulation/logs?id=${row.id}`)
}

const discoverFromLog = (row) => {
  router.push({ path: '/mining/discover', query: { logId: row.id } })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  margin-left: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
