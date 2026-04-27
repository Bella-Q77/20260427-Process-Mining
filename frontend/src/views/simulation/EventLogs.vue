<template>
  <div class="event-logs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>事件日志列表</span>
          <el-button type="primary" @click="goToGenerate">
            <el-icon><Plus /></el-icon>
            生成新数据
          </el-button>
        </div>
      </template>
      
      <el-table :data="logs" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="日志名称" min-width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="case_count" label="案例数" width="100" align="center" />
        <el-table-column prop="event_count" label="事件数" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="viewDetail(scope.row)">详情</el-button>
            <el-button type="success" link @click="discoverProcess(scope.row)">流程发现</el-button>
            <el-button type="warning" link @click="viewStatistics(scope.row)">统计</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="logs.length === 0 && !loading" description="暂无事件日志，请先生成模拟数据">
        <el-button type="primary" @click="goToGenerate">生成模拟数据</el-button>
      </el-empty>
    </el-card>

    <el-dialog v-model="detailVisible" title="日志详情" width="800px">
      <el-descriptions :column="2" border v-if="selectedLog">
        <el-descriptions-item label="日志名称">{{ selectedLog.name }}</el-descriptions-item>
        <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
        <el-descriptions-item label="案例数" :span="1">{{ selectedLog.case_count }}</el-descriptions-item>
        <el-descriptions-item label="事件数" :span="1">{{ selectedLog.event_count }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ selectedLog.description || '暂无描述' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatTime(selectedLog.created_at) }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="section-title" style="margin-top: 20px;">事件列表（前50条）</div>
      <el-table :data="events" v-loading="eventsLoading" size="small" max-height="300">
        <el-table-column prop="case_id" label="案例ID" width="120" />
        <el-table-column prop="activity" label="活动" width="100" />
        <el-table-column prop="resource" label="执行人" width="100" />
        <el-table-column prop="document_type" label="单据类型" width="120" />
        <el-table-column prop="department" label="部门" width="100" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="scope">
            ¥{{ scope.row.amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="statsVisible" title="统计信息" width="800px">
      <div v-if="statistics">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总案例数" :value="statistics.total_cases" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="总事件数" :value="statistics.total_events" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="活动种类数" :value="statistics.activity_statistics?.length || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="部门数" :value="statistics.department_statistics?.length || 0" />
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div class="section-title">活动统计</div>
        <el-table :data="statistics.activity_statistics || []" size="small">
          <el-table-column prop="activity" label="活动名称" />
          <el-table-column prop="count" label="事件数" align="center" />
          <el-table-column prop="case_count" label="涉及案例数" align="center" />
        </el-table>
        
        <el-divider />
        
        <div class="section-title">金额统计</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="最小金额">
            ¥{{ statistics.amount_statistics?.min?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="最大金额">
            ¥{{ statistics.amount_statistics?.max?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="平均金额">
            ¥{{ statistics.amount_statistics?.avg?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="总金额">
            ¥{{ statistics.amount_statistics?.total?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="section-title">部门统计</div>
        <el-table :data="statistics.department_statistics || []" size="small">
          <el-table-column prop="department" label="部门" />
          <el-table-column prop="case_count" label="案例数" align="center" />
        </el-table>
        
        <el-divider />
        
        <div class="section-title">单据类型统计</div>
        <el-table :data="statistics.document_type_statistics || []" size="small">
          <el-table-column prop="document_type" label="单据类型" />
          <el-table-column prop="case_count" label="案例数" align="center" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getEventLogs, getEventLogDetail, getEvents, getSimulationStatistics, deleteEventLog } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const eventsLoading = ref(false)
const logs = ref([])
const selectedLog = ref(null)
const events = ref([])
const statistics = ref(null)
const detailVisible = ref(false)
const statsVisible = ref(false)

const loadLogs = async () => {
  loading.value = true
  try {
    const res = await getEventLogs()
    logs.value = res.data || []
  } catch (error) {
    console.error('加载事件日志失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const goToGenerate = () => {
  router.push('/simulation/generate')
}

const viewDetail = async (row) => {
  selectedLog.value = row
  eventsLoading.value = true
  try {
    const res = await getEvents(row.id, { page: 1, per_page: 50 })
    events.value = res.data?.events || []
  } catch (error) {
    console.error('加载事件失败:', error)
  } finally {
    eventsLoading.value = false
  }
  detailVisible.value = true
}

const viewStatistics = async (row) => {
  try {
    const res = await getSimulationStatistics(row.id)
    if (res.data.success) {
      statistics.value = res.data.statistics
      statsVisible.value = true
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
    ElMessage.error('加载失败')
  }
}

const discoverProcess = (row) => {
  router.push({ path: '/mining/discover', query: { logId: row.id } })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除事件日志 "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteEventLog(row.id)
    if (res.data.success) {
      ElMessage.success(res.data.message)
      loadLogs()
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
  loadLogs()
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
</style>
