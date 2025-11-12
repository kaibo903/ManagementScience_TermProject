<template>
  <el-container class="app-container">
    <!-- 頂部導航欄 -->
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">營造廠決策分析平台</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          router
          class="header-menu"
        >
          <el-menu-item index="/projects">
            <el-icon><FolderOpened /></el-icon>
            <span>專案管理</span>
          </el-menu-item>
          <el-menu-item index="/optimization">
            <el-icon><TrendCharts /></el-icon>
            <span>投標優化</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <!-- 主要內容區域 -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FolderOpened, TrendCharts } from '@element-plus/icons-vue'

const route = useRoute()

// 計算當前啟用的選單項
const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #409eff;
  color: white;
  padding: 0;
  height: 60px !important;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-menu {
  background-color: transparent;
  border-bottom: none;
}

.header-menu :deep(.el-menu-item) {
  color: white;
  border-bottom: 2px solid transparent;
}

.header-menu :deep(.el-menu-item:hover),
.header-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}
</style>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
