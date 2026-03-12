<script setup>
import { computed } from 'vue'

const props = defineProps({
  distributionData: {
    type: Array,
    required: true,
    default: () => []
  }
})

const option = computed(() => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center',
      icon: 'circle',
      textStyle: {
        color: '#6b7280' // gray-500
      }
    },
    series: [
      {
        name: '项目任务数',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#374151' // gray-700
          }
        },
        labelLine: {
          show: false
        },
        data: props.distributionData
      }
    ],
    // Let ECharts use its default beautiful colors, or we can specify a custom palette
    color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#14b8a6', '#f43f5e']
  }
})
</script>

<template>
  <div class="w-full h-full min-h-[300px]">
    <div v-if="distributionData.length === 0" class="h-full flex items-center justify-center text-gray-400">
      暂无活跃项目数据
    </div>
    <v-chart v-else class="chart w-full h-full" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart {
  height: 300px;
}
</style>
