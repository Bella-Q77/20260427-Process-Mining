<template>
  <div class="performance-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>性能分析</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="form">
        <el-form-item label="选择事件日志">
          <el-select 
            v-model="form.logId" 
            placeholder="请选择事件日志" 
            style="width: 300px;"
          >
            <el-option 
              v-for="log in logs" 
              :key="log.id" 
              :label="log.name" 
              :value="log.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="loadAnalysis" 
            :loading="loading"
            :disabled="!form.logId"
          >
            <el-icon><Timer /></el-icon>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="performanceData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>案例持续时间统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="最短时间(小时)" :value="durationStats.min" :precision="2">
            <template #suffix>
              <span style="font-size: 14px;">小时</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="最长时间(小时)" :value="durationStats.max" :precision="2">
            <template #suffix>
              <span style="font-size: 14px;">小时</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均时间(小时)" :value="durationStats.mean" :precision="2">
            <template #suffix>
              <span style="font-size: 14px;">小时</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="中位数(小时)" :value="durationStats.median" :precision="2">
            <template #suffix>
              <span style="font-size: 14px;">小时</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="performanceData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>活动等待时间分析（最慢的10个路径）</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="14">
          <div ref="waitTimeChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="10">
          <el-table :data="waitTimeData" max-height="400">
            <el-table-column prop="path" label="路径" min-width="150" />
            <el-table-column prop="count" label="次数" width="80" align="center" />
            <el-table-column prop="mean" label="平均(小时)" width="100" align="center">
              <template #default="scope">
                <el-tag :type="getTimeTagType(scope.row.mean, maxWaitTime)" size="small">
                  {{ scope.row.mean.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="max" label="最长(小时)" width="100" align="center" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="performanceData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>活动频率统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="activityChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="12">
          <el-table :data="activityTableData" max-height="400">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="name" label="活动名称" width="150" />
            <el-table-column prop="count" label="出现次数" width="120" align="center" sortable />
            <el-table-column label="占比" width="150">
              <template #default="scope">
                <el-progress 
                  :percentage="(scope.row.count / totalEvents * 100)" 
                  :stroke-width="12"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="!logs.length && !loading" style="margin-top: 20px;">
      <el-empty description="暂无事件日志，请先生成模拟数据">
        <el-button type="primary" @click="$router.push('/simulation/generate')">生成模拟数据</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Timer } from '@element-plus/icons-vue'
import { getEventLogs, getPerformanceAnalysis } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const loading = ref(false)
const logs = ref([])
const performanceData = ref(null)
const waitTimeChartRef = ref(null)
const activityChartRef = ref(null)
let waitTimeChart = null
let activityChart = null

const form = reactive({
  logId: null
})

const waitTimeData = ref([])
const maxWaitTime = ref(0)
const activityTableData = ref([])
const totalEvents = ref(0)

const durationStats = computed(() => {
  if (!performanceData.value) return { min: 0, max: 0, mean: 0, median: 0 }
  const stats = performanceData.value.case_duration_statistics || {}
  return {
    min: stats.min || 0,
    max: stats.max || 0,
    mean: stats.mean || 0,
    median: stats.median || 0
  }
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
        await loadAnalysis()
      }
    }
  } catch (error) {
    console.error('加载事件日志失败:', error)
  }
}

const getTimeTagType = (value, max) => {
  if (max === 0) return ''
  const ratio = value / max
  if (ratio >= 0.7) return 'danger'
  if (ratio >= 0.4) return 'warning'
  return 'success'
}

const loadAnalysis = async () => {
  if (!form.logId) {
    ElMessage.warning('请先选择事件日志')
    return
  }
  
  loading.value = true
  try {
    const res = await getPerformanceAnalysis(form.logId)
    
    if (res.data.success) {
      performanceData.value = res.data.data
      
      // 处理等待时间数据
      waitTimeData.value = performanceData.value.activity_wait_times || []
      if (waitTimeData.value.length > 0) {
        maxWaitTime.value = Math.max(...waitTimeData.value.map(d => d.mean))
      }
      
      // 处理活动频率数据
      const activityCounts = performanceData.value.activity_counts || {}
      activityTableData.value = Object.entries(activityCounts).map(([name, count]) => ({
        name,
        count
      })).sort((a, b) => b.count - a.count)
      
      totalEvents.value = activityTableData.value.reduce((sum, item) => sum + item.count, 0)
      
      await nextTick()
      renderCharts()
    } else {
      ElMessage.error(res.data.error || '分析失败')
    }
  } catch (error) {
    console.error('性能分析失败:', error)
    ElMessage.error(error.response?.data?.error || '分析失败')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderWaitTimeChart()
  renderActivityChart()
}

const renderWaitTimeChart = () => {
  if (!waitTimeChartRef.value || !waitTimeData.value.length) return
  
  if (waitTimeChart) {
    waitTimeChart.dispose()
  }
  
  waitTimeChart = echarts.init(waitTimeChartRef.value)
  
  const data = waitTimeData.value.slice(0, 10).reverse()
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const param = params[0]
        const item = waitTimeData.value.find(d => d.path === param.name)
        if (item) {
          return `
            <strong>${param.name}</strong><br/>
            平均等待时间: ${item.mean.toFixed(2)} 小时<br/>
            最长等待时间: ${item.max.toFixed(2)} 小时<br/>
            最短等待时间: ${item.min.toFixed(2)} 小时<br/>
            发生次数: ${item.count} 次
          `
        }
        return param.name
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '平均等待时间(小时)'
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.path)
    },
    series: [
      {
        name: '平均等待时间',
        type: 'bar',
        data: data.map(d => d.mean),
        itemStyle: {
          color: (params) => {
            const value = params.value
            if (value >= maxWaitTime.value * 0.7) return '#F56C6C'
            if (value >= maxWaitTime.value * 0.4) return '#E6A23C'
            return '#67C23A'
          }
        }
      }
    ]
  }
  
  waitTimeChart.setOption(option)
}

const renderActivityChart = () => {
  if (!activityChartRef.value || !activityTableData.value.length) return
  
  if (activityChart) {
    activityChart.dispose()
  }
  
  activityChart = echarts.init(activityChartRef.value)
  
  const data = activityTableData.value.slice(0, 10)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '活动频率',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}次 ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: data.map(d => ({ name: d.name, value: d.count }))
      }
    ]
  }
  
  activityChart.setOption(option)
}

onMounted(() => {
  loadLogs()
})

// 窗口大小改变时重绘图表
window.addEventListener('resize', () => {
  if (waitTimeChart) waitTimeChart.resize()
  if (activityChart) activityChart.resize()
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

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
