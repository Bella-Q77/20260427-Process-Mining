<template>
  <div class="generate-simulation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生成模拟数据</span>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="案例数量" prop="numCases">
          <el-input-number 
            v-model="form.numCases" 
            :min="1" 
            :max="10000" 
            :step="100"
            style="width: 200px;"
          />
          <span class="form-tip">建议数量：100-1000</span>
        </el-form-item>
        
        <el-form-item label="日志名称" prop="logName">
          <el-input v-model="form.logName" placeholder="请输入事件日志名称" style="width: 400px;" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleGenerate" :loading="loading">
            <el-icon><Plus /></el-icon>
            生成模拟数据
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>流程变体说明</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12" v-for="(variant, key) in variants" :key="key">
          <el-card shadow="hover" style="margin-bottom: 15px;">
            <template #header>
              <div class="variant-header">
                <span class="variant-name">{{ variant.name }}</span>
                <el-tag type="info">{{ variant.percentage }}</el-tag>
              </div>
            </template>
            <p class="variant-desc">{{ variant.description }}</p>
            <div class="variant-activities">
              <span class="activity-label">活动流程：</span>
              <el-tag 
                v-for="(activity, index) in variant.activities" 
                :key="index"
                :type="getActivityType(index, variant.activities.length)"
                size="small"
                style="margin-right: 5px;"
              >
                {{ activity }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据字段说明</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="case_id">
          案例ID，用于唯一标识一个财务单据的整个生命周期
        </el-descriptions-item>
        <el-descriptions-item label="activity">
          活动名称，如：制单、部门审核、财务审核、总经理审批、支付、归档
        </el-descriptions-item>
        <el-descriptions-item label="timestamp">
          事件发生的时间戳
        </el-descriptions-item>
        <el-descriptions-item label="resource">
          执行该活动的人员
        </el-descriptions-item>
        <el-descriptions-item label="document_type">
          单据类型，如：报销单、付款单、采购申请单等
        </el-descriptions-item>
        <el-descriptions-item label="department">
          所属部门，如：销售部、技术部、财务部等
        </el-descriptions-item>
        <el-descriptions-item label="amount">
          单据金额（元）
        </el-descriptions-item>
        <el-descriptions-item label="status">
          事件状态，如：提交、通过、驳回、修改后提交等
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { generateSimulation, getVariantsInfo } from '@/api'

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)
const variants = ref({})

const form = reactive({
  numCases: 500,
  logName: '模拟财务单据流程日志'
})

const rules = {
  numCases: [
    { required: true, message: '请输入案例数量', trigger: 'blur' },
    { type: 'number', min: 1, max: 10000, message: '案例数量必须在1到10000之间', trigger: 'blur' }
  ],
  logName: [
    { required: true, message: '请输入日志名称', trigger: 'blur' }
  ]
}

const loadVariantsInfo = async () => {
  try {
    const res = await getVariantsInfo()
    if (res.data.success) {
      variants.value = res.data.variants
    }
  } catch (error) {
    console.error('加载流程变体信息失败:', error)
  }
}

const getActivityType = (index, total) => {
  if (index === 0) return 'success'
  if (index === total - 1) return 'danger'
  return 'primary'
}

const handleGenerate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await ElMessageBox.confirm(
          `确定要生成 ${form.numCases} 个案例的模拟数据吗？`,
          '确认生成',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        loading.value = true
        const res = await generateSimulation({
          num_cases: form.numCases,
          log_name: form.logName
        })
        
        if (res.data.success) {
          ElMessage.success(res.data.message)
          // 跳转到事件日志页面
          router.push('/simulation/logs')
        } else {
          ElMessage.error(res.data.error || '生成失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.error || '生成失败')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const resetForm = () => {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadVariantsInfo()
})
</script>

<style scoped>
.card-header {
  font-weight: bold;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.variant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.variant-name {
  font-weight: bold;
}

.variant-desc {
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.6;
}

.variant-activities {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.activity-label {
  font-size: 12px;
  color: #909399;
  margin-right: 5px;
}
</style>
