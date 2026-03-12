<script setup>
import { computed } from 'vue'

const props = defineProps({
  trendData: {
    type: Object,
    required: true,
    default: () => ({
      dates: [],
      brainstorms: [],
      tasks: []
    })
  }
})

const option = computed(() => {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['新增灵感', '完成任务'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: props.trendData.dates,
        axisLine: {
          lineStyle: {
            color: '#9ca3af'
          }
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#9ca3af'
          }
        },
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#f3f4f6'
          }
        }
      }
    ],
    series: [
      {
        name: '新增灵感',
        type: 'line',
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#fbbf24' // yellow-400
        },
        itemStyle: {
          color: '#fbbf24'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(251, 191, 36, 0.5)' // yellow-400
            }, {
              offset: 1, color: 'rgba(251, 191, 36, 0.05)'
            }]
          }
        },
        data: props.trendData.brainstorms
      },
      {
        name: '完成任务',
        type: 'line',
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#34d399' // emerald-400
        },
        itemStyle: {
          color: '#34d399'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(52, 211, 153, 0.5)' // emerald-400
            }, {
              offset: 1, color: 'rgba(52, 211, 153, 0.05)'
            }]
          }
        },
        data: props.trendData.tasks
      }
    ]
  }
})
</script>

<template>
  <div class="w-full h-full min-h-[300px]">
    <v-chart class="chart w-full h-full" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart {
  height: 300px;
}
</style>
