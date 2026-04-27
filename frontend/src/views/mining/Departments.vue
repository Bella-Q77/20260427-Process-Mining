<template>
  <div class="department-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门分析</span>
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
            <el-icon><OfficeBuilding /></el-icon>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="deptData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>部门案例统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="14">
          <div ref="deptChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="10">
          <el-table :data="deptCases" max-height="400">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="department" label="部门名称" min-width="120" />
            <el-table-column prop="case_count" label="案例数" width="100" align="center" sortable />
            <el-table-column label="占比" width="150">
              <template #default="scope">
                <el-progress 
                  :percentage="(scope.row.case_count / totalCases * 100)" 
                  :stroke-width="12"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="deptData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>部门金额统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="14">
          <div ref="amountChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="10">
          <el-table :data="deptAmounts" max-height="400">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="department" label="部门名称" min-width="120" />
            <el-table-column prop="total_amount" label="总金额" width="130" align="center">
              <template #default="scope">
                <el-tag :type="getAmountTagType(scope.row.total_amount, maxAmount)" size="small">
                  ¥{{ formatAmount(scope.row.total_amount) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="avg_amount" label="平均金额" width="120" align="center">
              <template #default="scope">
                ¥{{ formatAmount(scope.row.avg_amount) }}
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="deptData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>部门活动分布</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="表格视图" name="table">
          <el-table :data="deptActivityTable" max-height="500" border>
            <el-table-column prop="department" label="部门" width="120" fixed />
            <el-table-column 
              v-for="activity in activities" 
              :key="activity"
              :prop="activity"
              :label="activity"
              min-width="100"
              align="center"
            >
              <template #default="scope">
                <el-tag :type="getActivityTagType(scope.row[activity], maxActivityCount)" size="small">
                  {{ scope.row[activity] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total" label="总计" width="80" align="center" fixed="right">
              <template #default="scope">
                <strong>{{ scope.row.total }}</strong>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="堆叠图视图" name="stack">
          <div ref="stackChart" class="chart-container" style="height: 500px;"></div>
        </el-tab-pane>
      </el-tabs>
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
import { OfficeBuilding } from '@element-plus/icons-vue'
import { getEventLogs, getDepartmentAnalysis } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const loading = ref(false)
const logs = ref([])
const deptData = ref(null)
const activeTab = ref('table')
const deptChartRef = ref(null)
const amountChartRef = ref(null)
const stackChartRef = ref(null)
let deptChart = null
let amountChart = null
let stackChart = null

const form = reactive({
  logId: null
})

const deptCases = ref([])
const deptAmounts = ref([])
const deptActivityTable = ref([])
const activities = ref([])
const maxActivityCount = ref(0)
const maxAmount = ref(0)

const totalCases = computed(() => {
  return deptCases.value.reduce((sum, item) => sum + item.case_count, 0)
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

const formatAmount = (amount) => {
  if (!amount) return '0.00'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getAmountTagType = (value, max) => {
  if (max === 0) return ''
  const ratio = value / max
  if (ratio >= 0.7) return 'danger'
  if (ratio >= 0.4) return 'warning'
  return 'success'
}

const getActivityTagType = (value, max) => {
  if (max === 0) return ''
  const ratio = value / max
  if (ratio >= 0.7) return 'danger'
  if (ratio >= 0.4) return 'warning'
  if (value > 0) return 'success'
  return 'info'
}

const loadAnalysis = async () => {
  if (!form.logId) {
    ElMessage.warning('请先选择事件日志')
    return
  }
  
  loading.value = true
  try {
    const res = await getDepartmentAnalysis(form.logId)
    
    if (res.data.success) {
      deptData.value = res.data.data
      
      // 处理部门案例数据
      deptCases.value = (deptData.value.department_cases || []).sort(
        (a, b) => b.case_count - a.case_count
      )
      
      // 处理部门金额数据
      deptAmounts.value = (deptData.value.department_amounts || []).sort(
        (a, b) => b.total_amount - a.total_amount
      )
      
      if (deptAmounts.value.length > 0) {
        maxAmount.value = Math.max(...deptAmounts.value.map(d => d.total_amount))
      }
      
      // 处理部门活动分布
      const dist = deptData.value.department_activity_distribution || {}
      const departments = Object.keys(dist)
      
      if (departments.length > 0) {
        // 获取所有活动类型
        const allActivities = new Set()
        departments.forEach(d => {
          Object.keys(dist[d]).forEach(a => allActivities.add(a))
        })
        activities.value = Array.from(allActivities)
        
        // 构建表格数据
        deptActivityTable.value = departments.map(department => {
          const row = { department }
          let total = 0
          activities.value.forEach(activity => {
            const count = dist[department][activity] || 0
            row[activity] = count
            total += count
          })
          row.total = total
          return row
        }).sort((a, b) => b.total - a.total)
        
        // 计算最大值
        if (deptActivityTable.value.length > 0) {
          maxActivityCount.value = Math.max(
            ...deptActivityTable.value.flatMap(row => 
              activities.value.map(a => row[a])
            )
          )
        }
      }
      
      await nextTick()
      renderCharts()
    } else {
      ElMessage.error(res.data.error || '分析失败')
    }
  } catch (error) {
    console.error('部门分析失败:', error)
    ElMessage.error(error.response?.data?.error || '分析失败')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderDeptChart()
  renderAmountChart()
  renderStackChart()
}

const renderDeptChart = () => {
  if (!deptChartRef.value || !deptCases.value.length) return
  
  if (deptChart) {
    deptChart.dispose()
  }
  
  deptChart = echarts.init(deptChartRef.value)
  
  const data = deptCases.value.slice(0, 10)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.department),
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '案例数'
    },
    series: [
      {
        name: '案例数',
        type: 'bar',
        data: data.map(d => d.case_count),
        itemStyle: {
          color: '#409EFF'
        },
        label: {
          show: true,
          position: 'top'
        }
      }
    ]
  }
  
  deptChart.setOption(option)
}

const renderAmountChart = () => {
  if (!amountChartRef.value || !deptAmounts.value.length) return
  
  if (amountChart) {
    amountChart.dispose()
  }
  
  amountChart = echarts.init(amountChartRef.value)
  
  const data = deptAmounts.value.slice(0, 10)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const param = params[0]
        return `
          <strong>${param.name}</strong><br/>
          总金额: ¥${formatAmount(param.value)}<br/>
          平均金额: ¥${formatAmount(data.find(d => d.department === param.name)?.avg_amount || 0)}
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.department),
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '金额(元)',
      axisLabel: {
        formatter: (value) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(0) + '万'
          }
          return value
        }
      }
    },
    series: [
      {
        name: '总金额',
        type: 'bar',
        data: data.map(d => d.total_amount),
        itemStyle: {
          color: '#67C23A'
        },
        label: {
          show: true,
          position: 'top',
          formatter: (params) => {
            if (params.value >= 10000) {
              return (params.value / 10000).toFixed(1) + '万'
            }
            return params.value.toFixed(0)
          }
        }
      }
    ]
  }
  
  amountChart.setOption(option)
}

const renderStackChart = () => {
  if (!stackChartRef.value || !deptActivityTable.value.length) return
  
  if (stackChart) {
    stackChart.dispose()
  }
  
  stackChart = echarts.init(stackChartRef.value)
  
  const departments = deptActivityTable.value.map(d => d.department)
  
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#00D4FF', '#FF6B6B']
  
  const series = activities.value.map((activity, index) => ({
    name: activity,
    type: 'bar',
    stack: 'total',
    data: deptActivityTable.value.map(d => d[activity] || 0),
    itemStyle: {
      color: colors[index % colors.length]
    }
  }))
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: activities.value
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: departments,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '活动数'
    },
    series: series
  }
  
  stackChart.setOption(option)
}

onMounted(() => {
  loadLogs()
})

// 窗口大小改变时重绘图表
window.addEventListener('resize', () => {
  if (deptChart) deptChart.resize()
  if (amountChart) amountChart.resize()
  if (stackChart) stackChart.resize()
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
