<template>
  <div class="result-analysis">
    <!-- 麵包屑導航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>首頁</el-breadcrumb-item>
      <el-breadcrumb-item>結果分析</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 頁面標題和匯出按鈕 -->
    <div class="page-header-bar">
      <h1 class="page-title">優化結果分析</h1>
      <div class="export-buttons">
        <el-button 
          type="primary" 
          @click="exportPDF" 
          :loading="exportingPDF"
          class="export-btn"
        >
          <el-icon><Document /></el-icon>
          匯出 PDF
        </el-button>
        <el-button 
          type="success" 
          @click="exportExcel" 
          :loading="exportingExcel"
          class="export-btn"
        >
          <el-icon><Document /></el-icon>
          匯出 Excel
        </el-button>
      </div>
    </div>

    <div v-loading="loading" class="content-container">
      <div v-if="result">
        <!-- 結果摘要卡片 -->
        <div class="summary-card">
          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-label">最優工期</div>
              <div class="summary-value">{{ result.optimal_duration }} 天</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">最優成本</div>
              <div class="summary-value">{{ formatCurrency(result.optimal_cost) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">違約金</div>
              <div class="summary-value">{{ formatCurrency(result.penalty_amount) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">獎金</div>
              <div class="summary-value">{{ formatCurrency(result.bonus_amount) }}</div>
            </div>
            <div class="summary-item total-item">
              <div class="summary-label">總成本（含獎懲）</div>
              <div class="summary-value total-value">{{ formatCurrency(result.total_cost) }}</div>
            </div>
          </div>
        </div>

        <!-- 甘特圖卡片 -->
        <div class="chart-card">
          <div class="chart-header">
            <h2 class="chart-title">作業排程甘特圖</h2>
          </div>
          <div class="chart-content">
            <GanttChart :schedules="result.schedules" />
          </div>
        </div>

        <!-- 成本分析圖表卡片 -->
        <div class="chart-card">
          <div class="chart-header">
            <h2 class="chart-title">成本分析</h2>
          </div>
          <div class="chart-content">
            <CostChart :schedules="result.schedules" />
          </div>
        </div>

        <!-- 作業排程明細表格 -->
        <div class="table-card">
          <div class="table-header">
            <h2 class="table-title">作業排程明細</h2>
          </div>
          <div class="table-content">
            <el-table :data="result.schedules" stripe border class="schedule-table">
              <el-table-column prop="activity_name" label="作業名稱" width="200" />
              <el-table-column prop="start_time" label="開始時間（天）" width="120" align="center" />
              <el-table-column prop="end_time" label="結束時間（天）" width="120" align="center" />
              <el-table-column prop="duration" label="工期（天）" width="100" align="center" />
              <el-table-column prop="is_crashed" label="是否趕工" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_crashed ? 'warning' : 'success'" class="status-tag">
                    {{ row.is_crashed ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="cost" label="成本" align="right">
                <template #default="{ row }">
                  <span class="cost-text">{{ formatCurrency(row.cost) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <el-empty v-else description="沒有找到優化結果" class="empty-state" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { optimizationAPI } from '../services/api'
import GanttChart from '../components/GanttChart.vue'
import CostChart from '../components/CostChart.vue'
import { exportToPDF } from '../utils/pdfGenerator'
import { exportToExcel } from '../utils/excelGenerator'

const route = useRoute()

const result = ref(null)
const loading = ref(false)
const exportingPDF = ref(false)
const exportingExcel = ref(false)

// 載入優化結果
const loadResult = async () => {
  const scenarioId = route.params.resultId
  if (!scenarioId) {
    ElMessage.warning('請提供優化結果 ID')
    return
  }

  loading.value = true
  try {
    result.value = await optimizationAPI.getResult(scenarioId)
  } catch (error) {
    ElMessage.error('載入優化結果失敗：' + error.message)
  } finally {
    loading.value = false
  }
}

// 匯出 PDF
const exportPDF = async () => {
  if (!result.value) {
    ElMessage.warning('沒有可匯出的結果')
    return
  }

  exportingPDF.value = true
  try {
    await exportToPDF(result.value)
    ElMessage.success('PDF 匯出成功')
  } catch (error) {
    ElMessage.error('PDF 匯出失敗：' + error.message)
  } finally {
    exportingPDF.value = false
  }
}

// 匯出 Excel
const exportExcel = async () => {
  if (!result.value) {
    ElMessage.warning('沒有可匯出的結果')
    return
  }

  exportingExcel.value = true
  try {
    await exportToExcel(result.value)
    ElMessage.success('Excel 匯出成功')
  } catch (error) {
    ElMessage.error('Excel 匯出失敗：' + error.message)
  } finally {
    exportingExcel.value = false
  }
}

// 格式化貨幣
const formatCurrency = (value) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(value)
}

onMounted(() => {
  loadResult()
})
</script>

<style scoped>
.result-analysis {
  width: 100%;
  padding: var(--spacing-3xl);
  background-color: var(--content-bg);
  min-height: calc(100vh - 64px);
}

.breadcrumb {
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-md);
  color: var(--text-secondary);
}

/* 頁面標題欄 */
.page-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0;
}

.export-buttons {
  display: flex;
  gap: 12px;
}

.export-btn {
  border-radius: 6px;
  font-weight: 500;
  padding: 10px 20px;
  transition: all 0.2s ease;
}

.export-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 結果摘要卡片 */
.summary-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xl);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item.total-item {
  grid-column: 1 / -1;
  padding-top: var(--spacing-xl);
  border-top: 2px solid var(--border-color);
}

.summary-label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  letter-spacing: 0;
}

.summary-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: 0;
}

.summary-value.total-value {
  font-size: var(--font-size-3xl);
  color: var(--danger);
}

/* 圖表卡片 */
.chart-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.chart-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  background-color: #F9FAFB;
  border-bottom: 1px solid var(--border-color);
}

.chart-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0;
}

.chart-content {
  padding: var(--spacing-2xl);
  min-height: 400px;
}

/* 表格卡片 */
.table-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.table-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  background-color: #F9FAFB;
  border-bottom: 1px solid var(--border-color);
}

.table-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0;
}

.table-content {
  padding: 0;
}

/* 表格樣式 */
.result-analysis :deep(.schedule-table) {
  border: none;
  border-radius: 0;
}

.result-analysis :deep(.schedule-table th) {
  background-color: #F9FAFB;
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
  border-bottom: 2px solid var(--border-color);
  padding: var(--spacing-md) var(--spacing-md);
  letter-spacing: 0;
}

.result-analysis :deep(.schedule-table td) {
  color: var(--text-primary);
  font-size: var(--font-size-base);
  border-bottom: 1px solid var(--border-light);
  padding: var(--spacing-lg) var(--spacing-md);
  background-color: var(--card-bg);
}

.result-analysis :deep(.schedule-table .el-table__row:hover) {
  background-color: #F9FAFB !important;
  transition: background-color 0.15s ease;
}

.status-tag {
  border-radius: 4px;
  font-weight: 500;
  padding: 4px 12px;
}

.cost-text {
  font-weight: 500;
  color: #1F2937;
}

/* 空狀態 */
.empty-state {
  background-color: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 60px 20px;
}
</style>

