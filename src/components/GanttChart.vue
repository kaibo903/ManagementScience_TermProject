<template>
  <div class="gantt-chart">
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
  const startTimes = schedules.map(s => s.start_time)
  const durations = schedules.map(s => s.duration)
  const colors = schedules.map(s => s.is_crashed ? '#f56c6c' : '#67c23a')

  // 計算最大時間
  const maxTime = Math.max(...schedules.map(s => s.end_time))

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const data = params[0]
        const schedule = schedules[data.dataIndex]
        return `
          <div>
            <strong>${schedule.activity_name}</strong><br/>
            開始時間：第 ${schedule.start_time} 天<br/>
            結束時間：第 ${schedule.end_time} 天<br/>
            工期：${schedule.duration} 天<br/>
            是否趕工：${schedule.is_crashed ? '是' : '否'}<br/>
            成本：${formatCurrency(schedule.cost)}
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
      name: '時間（天）',
      min: 0,
      max: maxTime
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true
    },
    series: [
      {
        name: '作業排程',
        type: 'bar',
        data: schedules.map((s, index) => ({
          value: [s.start_time, s.start_time + s.duration],
          itemStyle: {
            color: colors[index]
          }
        })),
        barWidth: '60%',
        label: {
          show: true,
          position: 'inside',
          formatter: (params) => {
            const schedule = schedules[params.dataIndex]
            return `${schedule.duration}天`
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
.gantt-chart {
  width: 100%;
  min-height: 400px;
}

/* 圖表容器樣式 */
.gantt-chart :deep(.echarts) {
  width: 100% !important;
  height: 100% !important;
}
</style>

