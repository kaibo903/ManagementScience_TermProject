<template>
  <div class="gantt-chart">
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
  const colors = schedules.map(s => s.is_crashed ? '#EF4444' : '#10B981')

  // 計算最大時間
  const maxTime = Math.max(...schedules.map(s => (s.end_time || 0)), 1)

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
        return `
          <div style="padding: 8px;">
            <strong>${schedule.activity_name || '未命名作業'}</strong><br/>
            開始時間：第 ${schedule.start_time || 0} 天<br/>
            結束時間：第 ${schedule.end_time || 0} 天<br/>
            工期：${schedule.duration || 0} 天<br/>
            是否趕工：${schedule.is_crashed ? '是' : '否'}<br/>
            成本：${formatCurrency(schedule.cost || 0)}
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
      name: '時間（天）',
      min: 0,
      max: maxTime,
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
      // 透明佔位條（開始時間偏移）
      {
        name: '開始偏移',
        type: 'bar',
        stack: 'total',
        silent: true,
        itemStyle: {
          color: 'transparent',
          borderColor: 'transparent'
        },
        emphasis: {
          itemStyle: {
            color: 'transparent',
            borderColor: 'transparent'
          }
        },
        data: schedules.map(s => s.start_time || 0),
        barWidth: '60%'
      },
      // 實際作業條
      {
        name: '作業排程',
        type: 'bar',
        stack: 'total',
        data: schedules.map((s, index) => ({
          value: s.duration || 0,
          itemStyle: {
            color: colors[index],
            borderRadius: 0
          }
        })),
        barWidth: '60%',
        label: {
          show: true,
          position: 'inside',
          formatter: (params) => {
            const schedule = schedules[params.dataIndex]
            return `${schedule.duration || 0}天`
          },
          fontSize: 11,
          color: '#FFFFFF',
          fontWeight: 'bold'
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
.gantt-chart {
  width: 100%;
  min-height: 400px;
  position: relative;
}

/* 圖表容器樣式 */
.gantt-chart :deep(.echarts) {
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

