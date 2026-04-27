<template>
  <div class="process-variants">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程变体分析</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="form">
        <el-form-item label="选择事件日志">
          <el-select 
            v-model="form.logId" 
            placeholder="请选择事件日志" 
            style="width: 300px;"
            @change="handleLogChange"
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
            @click="loadVariants" 
            :loading="loading"
            :disabled="!form.logId"
          >
            <el-icon><Search /></el-icon>
            分析流程变体
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="variantsData" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>分析结果</span>
          <div>
            <el-tag type="info">共 {{ variantsData.total_variants }} 种变体</el-tag>
            <el-tag type="success" style="margin-left: 10px;">共 {{ variantsData.total_cases }} 个案例</el-tag>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="section-title">变体分布</div>
          <div ref="variantsChart" class="chart-container"></div>
        </el-col>
        
        <el-col :span="12">
          <div class="section-title">主要流程变体</div>
          <el-table :data="topVariants" max-height="400">
            <el-table-column prop="rank" label="排名" width="60" align="center">
              <template #default="scope">
                <el-tag v-if="scope.$index < 3" :type="getRankType(scope.$index)">
                  {{ scope.$index + 1 }}
                </el-tag>
                <span v-else>{{ scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="case_count" label="案例数" width="100" align="center" />
            <el-table-column prop="percentage" label="占比" width="100">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.percentage" 
                  :stroke-width="12"
                  :show-text="true"
                />
              </template>
            </el-table-column>
            <el-table-column prop="variant" label="流程路径" min-width="200">
              <template #default="scope">
                <div class="path-display">
                  <el-tag 
                    v-for="(activity, index) in scope.row.variant" 
                    :key="index"
                    size="small"
                    :type="getStepType(index, scope.row.variant.length)"
                    style="margin-right: 3px; margin-bottom: 3px;"
                  >
                    {{ activity }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <div class="section-title">所有变体详情</div>
      <el-table :data="variantsData.variants || []" max-height="400">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="case_count" label="案例数量" width="100" align="center" sortable />
        <el-table-column prop="percentage" label="占比(%)" width="100" sortable>
          <template #default="scope">
            {{ scope.row.percentage.toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="variant" label="流程路径">
          <template #default="scope">
            <div class="path-display">
              <span 
                v-for="(activity, index) in scope.row.variant" 
                :key="index"
                class="path-step"
              >
                {{ activity }}
                <span v-if="index < scope.row.variant.length - 1" class="path-arrow">→</span>
              </span>
            </div>
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
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getEventLogs, getProcessVariants } from '@/api'
import * as echarts from 'echarts'

const route = useRoute()
const loading = ref(false)
const logs = ref([])
const variantsData = ref(null)
const variantsChartRef = ref(null)
let chart = null

const form = reactive({
  logId: null
})

const topVariants = ref([])

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
        await loadVariants()
      }
    }
  } catch (error) {
    console.error('加载事件日志失败:', error)
  }
}

const handleLogChange = () => {
  variantsData.value = null
}

const getRankType = (index) => {
  if (index === 0) return 'success'
  if (index === 1) return 'warning'
  if (index === 2) return 'info'
  return ''
}

const getStepType = (index, total) => {
  if (index === 0) return 'success'
  if (index === total - 1) return 'danger'
  return 'primary'
}

const loadVariants = async () => {
  if (!form.logId) {
    ElMessage.warning('请先选择事件日志')
    return
  }
  
  loading.value = true
  try {
    const res = await getProcessVariants(form.logId)
    
    if (res.data.success) {
      variantsData.value = res.data.data
      topVariants.value = variantsData.value.variants?.slice(0, 5) || []
      
      await nextTick()
      renderChart()
    } else {
      ElMessage.error(res.data.error || '分析失败')
    }
  } catch (error) {
    console.error('流程变体分析失败:', error)
    ElMessage.error(error.response?.data?.error || '分析失败')
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!variantsChartRef.value || !variantsData.value) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(variantsChartRef.value)
  
  const variants = variantsData.value.variants || []
  const chartData = variants.slice(0, 10).map((v, i) => ({
    name: `变体${i + 1}`,
    value: v.case_count,
    path: v.variant.join(' → ')
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const variant = variants[params.dataIndex]
        if (variant) {
          return `
            <strong>${params.name}</strong><br/>
            案例数: ${params.value}<br/>
            占比: ${params.percent.toFixed(1)}%<br/>
            路径: ${variant.variant.join(' → ')}
          `
        }
        return params.name
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '流程变体',
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
          formatter: '{b}: {c}例 ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: chartData
      }
    ]
  }
  
  chart.setOption(option)
}

onMounted(() => {
  loadLogs()
})

// 窗口大小改变时重绘图表
window.addEventListener('resize', () => {
  if (chart) {
    chart.resize()
  }
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

.path-display {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.path-step {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.path-arrow {
  margin: 0 5px;
  color: #909399;
}
</style>
