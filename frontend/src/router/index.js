import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页概览', icon: 'DataLine' }
      }
    ]
  },
  {
    path: '/simulation',
    component: Layout,
    redirect: '/simulation/generate',
    meta: { title: '模拟数据', icon: 'DataAnalysis' },
    children: [
      {
        path: 'generate',
        name: 'GenerateSimulation',
        component: () => import('@/views/simulation/Generate.vue'),
        meta: { title: '生成模拟数据', icon: 'Plus' }
      },
      {
        path: 'logs',
        name: 'EventLogs',
        component: () => import('@/views/simulation/EventLogs.vue'),
        meta: { title: '事件日志管理', icon: 'Document' }
      }
    ]
  },
  {
    path: '/mining',
    component: Layout,
    redirect: '/mining/discover',
    meta: { title: '流程挖掘', icon: 'Connection' },
    children: [
      {
        path: 'discover',
        name: 'ProcessDiscover',
        component: () => import('@/views/mining/Discover.vue'),
        meta: { title: '流程发现', icon: 'Search' }
      },
      {
        path: 'variants',
        name: 'ProcessVariants',
        component: () => import('@/views/mining/Variants.vue'),
        meta: { title: '流程变体', icon: 'Share' }
      },
      {
        path: 'performance',
        name: 'PerformanceAnalysis',
        component: () => import('@/views/mining/Performance.vue'),
        meta: { title: '性能分析', icon: 'Timer' }
      },
      {
        path: 'resources',
        name: 'ResourceAnalysis',
        component: () => import('@/views/mining/Resources.vue'),
        meta: { title: '资源分析', icon: 'User' }
      },
      {
        path: 'departments',
        name: 'DepartmentAnalysis',
        component: () => import('@/views/mining/Departments.vue'),
        meta: { title: '部门分析', icon: 'OfficeBuilding' }
      }
    ]
  },
  {
    path: '/models',
    component: Layout,
    children: [
      {
        path: '',
        name: 'ProcessModels',
        component: () => import('@/views/Models.vue'),
        meta: { title: '流程模型', icon: 'Share' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
