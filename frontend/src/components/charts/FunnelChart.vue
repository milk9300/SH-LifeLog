<script setup>
import { computed } from 'vue'

const props = defineProps({
  funnelData: {
    type: Array, // Expected: [{value: 100, name: '待处理灵感'}, {value: 60, name: '已转化任务'}, {value: 30, name: '已完成'}]
    required: true,
    default: () => []
  }
})

const option = computed(() => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c}'
    },
    color: ['#fbbf24', '#3b82f6', '#10b981'], // yellow, blue, emerald
    series: [
      {
        name: '灵感转化漏斗',
        type: 'funnel',
        left: '10%',
        top: 20,
        bottom: 20,
        width: '80%',
        min: 0,
        max: props.funnelData.length > 0 ? props.funnelData[0].value : 100,
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside',
          formatter: '{b}: {c}'
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 16
          }
        },
        data: props.funnelData
      }
    ]
  }
})
</script>

<template>
  <div class="w-full h-full min-h-[300px]">
     <div v-if="funnelData.length === 0 || funnelData[0].value === 0" class="h-full flex items-center justify-center text-gray-400">
      尚未收集灵感
    </div>
    <v-chart v-else class="chart w-full h-full" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart {
  height: 300px;
}
</style>
