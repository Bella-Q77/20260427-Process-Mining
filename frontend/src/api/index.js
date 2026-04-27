import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 健康检查
export const checkHealth = () => api.get('/health')

// 事件日志相关
export const getEventLogs = () => api.get('/event-logs')
export const getEventLogDetail = (logId) => api.get(`/event-logs/${logId}`)
export const getEvents = (logId, params) => api.get(`/event-logs/${logId}/events`, { params })
export const getCases = (logId) => api.get(`/event-logs/${logId}/cases`)
export const getCaseDetail = (logId, caseId) => api.get(`/event-logs/${logId}/cases/${caseId}`)
export const deleteEventLog = (logId) => api.delete(`/event-logs/${logId}`)

// 模拟数据相关
export const generateSimulation = (data) => api.post('/simulation/generate', data)
export const getSimulationStatistics = (logId) => api.get(`/simulation/statistics/${logId}`)
export const getVariantsInfo = () => api.get('/simulation/variants')
export const getSampleStructure = () => api.get('/simulation/sample-data')

// 流程挖掘相关
export const discoverProcess = (data) => api.post('/mining/discover', data)
export const getProcessVariants = (logId) => api.get(`/mining/variants/${logId}`)
export const getPerformanceAnalysis = (logId) => api.get(`/mining/performance/${logId}`)
export const getResourceAnalysis = (logId) => api.get(`/mining/resources/${logId}`)
export const getDepartmentAnalysis = (logId) => api.get(`/mining/departments/${logId}`)
export const getAlgorithmsInfo = () => api.get('/mining/algorithms')

// 流程模型相关
export const getProcessModels = () => api.get('/process-models')
export const getProcessModelDetail = (modelId) => api.get(`/process-models/${modelId}`)
export const deleteProcessModel = (modelId) => api.delete(`/process-models/${modelId}`)

export default api
