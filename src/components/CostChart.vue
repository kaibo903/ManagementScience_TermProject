<template>
  <div class="cost-chart">
    <v-chart :option="chartOption" style="height: 400px;" />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  schedules: {
    type: Array,
    required: true
  }
})

// 計算圖表選項
const chartOption = computed(() => {
  const schedules = props.schedules || []
  
  if (schedules.length === 0) {
    return {
      title: {
        text: '沒有資料',
        left: 'center'
      }
    }
  }

  // 準備資料
  const categories = schedules.map(s => s.activity_name)
  const costs = schedules.map(s => parseFloat(s.cost))
  const totalCost = costs.reduce((sum, cost) => sum + cost, 0)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const data = params[0]
        const schedule = schedules[data.dataIndex]
        const percentage = ((parseFloat(schedule.cost) / totalCost) * 100).toFixed(2)
        return `
          <div>
            <strong>${schedule.activity_name}</strong><br/>
            成本：${formatCurrency(schedule.cost)}<br/>
            佔比：${percentage}%
          </div>
        `
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '10%'
    },
    xAxis: {
      type: 'value',
      name: '成本（元）'
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true
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
            return schedule.is_crashed ? '#f56c6c' : '#67c23a'
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params) => {
            return formatCurrency(params.value)
          }
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
}

/* 圖表容器樣式 */
.cost-chart :deep(.echarts) {
  width: 100% !important;
  height: 100% !important;
}
</style>

