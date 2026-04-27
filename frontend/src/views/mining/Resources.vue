<template>
  <div class="resource-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资源分析</span>
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
            <el-icon><User /></el-icon>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="resourceData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>资源工作负载统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="14">
          <div ref="resourceChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="10">
          <el-table :data="resourceStats" max-height="400">
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="org:resource" label="资源名称" min-width="120" />
            <el-table-column prop="case_count" label="处理案例数" width="100" align="center" sortable />
            <el-table-column prop="activity_count" label="执行活动数" width="100" align="center" sortable />
            <el-table-column label="效率" width="100">
              <template #default="scope">
                <el-progress 
                  :percentage="getEfficiency(scope.row.activity_count, scope.row.case_count)" 
                  :stroke-width="10"
                  :show-text="false"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="resourceData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>资源活动分布</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="表格视图" name="table">
          <el-table :data="resourceActivityTable" max-height="500" border>
            <el-table-column prop="resource" label="资源" width="120" fixed />
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
        
        <el-tab-pane label="热力图视图" name="heatmap">
          <div ref="heatmapChart" class="chart-container" style="height: 500px;"></div>
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
import { User } from '@element-plus/icons-vue'
import { getEventLogs, getResourceAnalysis } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const loading = ref(false)
const logs = ref([])
const resourceData = ref(null)
const activeTab = ref('table')
const resourceChartRef = ref(null)
const heatmapChartRef = ref(null)
let resourceChart = null
let heatmapChart = null

const form = reactive({
  logId: null
})

const resourceStats = ref([])
const resourceActivityTable = ref([])
const activities = ref([])
const maxActivityCount = ref(0)

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

const getEfficiency = (activityCount, caseCount) => {
  if (caseCount === 0) return 0
  const ratio = activityCount / caseCount
  return Math.min(100, Math.max(0, ratio * 20))
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
    const res = await getResourceAnalysis(form.logId)
    
    if (res.data.success) {
      resourceData.value = res.data.data
      
      // 处理资源统计数据
      resourceStats.value = (resourceData.value.resource_statistics || []).sort(
        (a, b) => b.activity_count - a.activity_count
      )
      
      // 处理资源活动分布
      const dist = resourceData.value.resource_activity_distribution || {}
      const resources = Object.keys(dist)
      
      if (resources.length > 0) {
        // 获取所有活动类型
        const allActivities = new Set()
        resources.forEach(r => {
          Object.keys(dist[r]).forEach(a => allActivities.add(a))
        })
        activities.value = Array.from(allActivities)
        
        // 构建表格数据
        resourceActivityTable.value = resources.map(resource => {
          const row = { resource }
          let total = 0
          activities.value.forEach(activity => {
            const count = dist[resource][activity] || 0
            row[activity] = count
            total += count
          })
          row.total = total
          return row
        }).sort((a, b) => b.total - a.total)
        
        // 计算最大值
        if (resourceActivityTable.value.length > 0) {
          maxActivityCount.value = Math.max(
            ...resourceActivityTable.value.flatMap(row => 
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
    console.error('资源分析失败:', error)
    ElMessage.error(error.response?.data?.error || '分析失败')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderResourceChart()
  renderHeatmapChart()
}

const renderResourceChart = () => {
  if (!resourceChartRef.value || !resourceStats.value.length) return
  
  if (resourceChart) {
    resourceChart.dispose()
  }
  
  resourceChart = echarts.init(resourceChartRef.value)
  
  const data = resourceStats.value.slice(0, 15)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['执行活动数', '处理案例数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d['org:resource']),
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '执行活动数',
        type: 'bar',
        data: data.map(d => d.activity_count),
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '处理案例数',
        type: 'bar',
        data: data.map(d => d.case_count),
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  resourceChart.setOption(option)
}

const renderHeatmapChart = () => {
  if (!heatmapChartRef.value || !resourceActivityTable.value.length) return
  
  if (heatmapChart) {
    heatmapChart.dispose()
  }
  
  heatmapChart = echarts.init(heatmapChartRef.value)
  
  const resources = resourceActivityTable.value.map(r => r.resource)
  const acts = activities.value
  
  // 构建热力图数据
  const heatmapData = []
  resources.forEach((resource, i) => {
    acts.forEach((activity, j) => {
      const count = resourceActivityTable.value[i][activity] || 0
      if (count > 0) {
        heatmapData.push([j, i, count])
      }
    })
  })
  
  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        if (params.value) {
          return `
            资源: ${resources[params.value[1]]}<br/>
            活动: ${acts[params.value[0]]}<br/>
            次数: ${params.value[2]}
          `
        }
        return ''
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: acts,
      splitArea: {
        show: true
      },
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'category',
      data: resources,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: maxActivityCount.value,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
      }
    },
    series: [
      {
        name: '资源活动热力图',
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: true,
          fontSize: 10
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  heatmapChart.setOption(option)
}

onMounted(() => {
  loadLogs()
})

// 窗口大小改变时重绘图表
window.addEventListener('resize', () => {
  if (resourceChart) resourceChart.resize()
  if (heatmapChart) heatmapChart.resize()
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
