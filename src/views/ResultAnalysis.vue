<template>
  <div class="result-analysis">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>優化結果分析</span>
          <div>
            <el-button @click="exportPDF" :loading="exportingPDF">
              <el-icon><Document /></el-icon>
              匯出 PDF
            </el-button>
            <el-button @click="exportExcel" :loading="exportingExcel">
              <el-icon><Document /></el-icon>
              匯出 Excel
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="result">
        <!-- 結果摘要 -->
        <el-descriptions :column="2" border style="margin-bottom: 20px;">
          <el-descriptions-item label="最優工期">
            {{ result.optimal_duration }} 天
          </el-descriptions-item>
          <el-descriptions-item label="最優成本">
            {{ formatCurrency(result.optimal_cost) }}
          </el-descriptions-item>
          <el-descriptions-item label="違約金">
            {{ formatCurrency(result.penalty_amount) }}
          </el-descriptions-item>
          <el-descriptions-item label="獎金">
            {{ formatCurrency(result.bonus_amount) }}
          </el-descriptions-item>
          <el-descriptions-item label="總成本（含獎懲）" :span="2">
            <strong style="font-size: 18px; color: #409eff;">
              {{ formatCurrency(result.total_cost) }}
            </strong>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 甘特圖 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>作業排程甘特圖</span>
          </template>
          <GanttChart :schedules="result.schedules" />
        </el-card>

        <!-- 成本分析圖表 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>成本分析</span>
          </template>
          <CostChart :schedules="result.schedules" />
        </el-card>

        <!-- 作業排程表 -->
        <el-card>
          <template #header>
            <span>作業排程明細</span>
          </template>
          <el-table :data="result.schedules" stripe border>
            <el-table-column prop="activity_name" label="作業名稱" width="200" />
            <el-table-column prop="start_time" label="開始時間（天）" width="120" align="center" />
            <el-table-column prop="end_time" label="結束時間（天）" width="120" align="center" />
            <el-table-column prop="duration" label="工期（天）" width="100" align="center" />
            <el-table-column prop="is_crashed" label="是否趕工" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_crashed ? 'warning' : 'success'">
                  {{ row.is_crashed ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cost" label="成本" align="right">
              <template #default="{ row }">
                {{ formatCurrency(row.cost) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <el-empty v-else description="沒有找到優化結果" />
    </el-card>
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
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

