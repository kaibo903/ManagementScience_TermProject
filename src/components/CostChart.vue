<template>
  <div class="cost-chart">
    <v-chart 
      v-if="chartOption && hasData" 
      :option="chartOption" 
      :autoresize="true"
      style="height: 400px; width: 100%;" 
    />
    <div v-else class="empty-chart">
      <p>沒有資料可顯示</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent
} from 'echarts/components'

// 註冊必要的 ECharts 組件
use([
  CanvasRenderer,
  BarChart,
  TooltipComponent,
  GridComponent
])

const props = defineProps({
  schedules: {
    type: Array,
    required: true,
    default: () => []
  }
})

// 檢查是否有資料
const hasData = computed(() => {
  return props.schedules && props.schedules.length > 0
})

// 計算圖表選項
const chartOption = computed(() => {
  const schedules = props.schedules || []
  
  if (!schedules || schedules.length === 0) {
    return null
  }

  // 準備資料
  const categories = schedules.map(s => s.activity_name || '未命名作業')
  const costs = schedules.map(s => parseFloat(s.cost || 0))
  const totalCost = costs.reduce((sum, cost) => sum + cost, 0) || 1

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        if (!params || !params[0]) return ''
        const data = params[0]
        const schedule = schedules[data.dataIndex]
        if (!schedule) return ''
        const percentage = ((parseFloat(schedule.cost || 0) / totalCost) * 100).toFixed(2)
        return `
          <div style="padding: 8px;">
            <strong>${schedule.activity_name || '未命名作業'}</strong><br/>
            成本：${formatCurrency(schedule.cost || 0)}<br/>
            佔比：${percentage}%
          </div>
        `
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '成本（元）',
      nameTextStyle: {
        fontSize: 12,
        color: '#6B7280'
      }
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true,
      axisLabel: {
        fontSize: 12,
        color: '#1F2937'
      }
    },
    series: [
      {
        name: '成本',
        type: 'bar',
        data: costs,
        itemStyle: {
          color: (params) => {
            // 根據是否趕工顯示不同顏色
            const schedule = schedules[params.dataIndex]
            return schedule.is_crashed ? '#EF4444' : '#10B981'
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params) => {
            return formatCurrency(params.value)
          },
          fontSize: 11,
          color: '#1F2937'
        }
      }
    ]
  }
})

// 格式化貨幣
const formatCurrency = (value) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(value)
}
</script>

<style scoped>
.cost-chart {
  width: 100%;
  min-height: 400px;
  position: relative;
}

/* 圖表容器樣式 */
.cost-chart :deep(.echarts) {
  width: 100% !important;
  height: 400px !important;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #9CA3AF;
  font-size: 14px;
}
</style>

