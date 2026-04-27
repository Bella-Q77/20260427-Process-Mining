<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="layout-aside">
      <div class="logo">
        <el-icon size="32"><DataAnalysis /></el-icon>
        <span class="logo-text">财务单据流程挖掘系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        
        <el-sub-menu index="simulation">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>模拟数据</span>
          </template>
          <el-menu-item index="/simulation/generate">生成模拟数据</el-menu-item>
          <el-menu-item index="/simulation/logs">事件日志管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="mining">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>流程挖掘</span>
          </template>
          <el-menu-item index="/mining/discover">流程发现</el-menu-item>
          <el-menu-item index="/mining/variants">流程变体</el-menu-item>
          <el-menu-item index="/mining/performance">性能分析</el-menu-item>
          <el-menu-item index="/mining/resources">资源分析</el-menu-item>
          <el-menu-item index="/mining/departments">部门分析</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/models">
          <el-icon><Share /></el-icon>
          <span>流程模型</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="layout-header">
        <div class="header-title">
          <span>{{ currentRouteTitle }}</span>
        </div>
        <div class="header-actions">
          <el-tooltip content="刷新数据" placement="bottom">
            <el-button type="primary" :icon="Refresh" circle @click="handleRefresh" />
          </el-tooltip>
        </div>
      </el-header>
      
      <el-main class="layout-main">
        <router-view />
      </el-main>
      
      <el-footer class="layout-footer">
        <span>财务单据流程挖掘系统 v1.0.0</span>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh, DataAnalysis, DataLine, Connection, Share } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const currentRouteTitle = computed(() => {
  if (route.meta && route.meta.title) {
    return route.meta.title
  }
  return '首页'
})

const handleRefresh = () => {
  window.location.reload()
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #2b3a4a;
  color: #fff;
}

.logo-text {
  margin-left: 10px;
  font-size: 16px;
  font-weight: bold;
}

.sidebar-menu {
  border-right: none;
}

.layout-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.layout-footer {
  background-color: #fff;
  border-top: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}
</style>
