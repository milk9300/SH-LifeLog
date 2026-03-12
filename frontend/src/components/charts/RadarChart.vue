<script setup>
import { computed } from 'vue'

const props = defineProps({
  radarData: {
    type: Array, // Array of { name: 'Goal Name', progress: 50 }
    required: true,
    default: () => []
  }
})

const option = computed(() => {
  const indicator = props.radarData.map(item => ({
    name: item.name,
    max: 100 // Progress is up to 100%
  }))

  const dataValues = props.radarData.map(item => item.progress)

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b} : {c}%'
    },
    radar: {
      indicator: indicator.length > 0 ? indicator : [{ name: '无目标', max: 100 }],
      shape: 'circle',
      radius: '60%',
      center: ['50%', '50%'],
      splitNumber: 5,
      axisName: {
        color: '#4b5563', // gray-600
        formatter: (value) => {
          if (!value) return ''
          let result = ''
          for (let i = 0; i < value.length; i += 6) {
            if (i > 6) {
              result += '...'
              break
            }
            result += value.slice(i, i + 6) + '\n'
          }
          return result.trim()
        }
      },
      splitLine: {
        lineStyle: {
          color: [
            'rgba(59, 130, 246, 0.1)',
            'rgba(59, 130, 246, 0.2)',
            'rgba(59, 130, 246, 0.4)',
            'rgba(59, 130, 246, 0.6)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(59, 130, 246, 1)'
          ].reverse()
        }
      },
      splitArea: {
        show: false
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(59, 130, 246, 0.5)' // blue-500
        }
      }
    },
    series: [
      {
        name: '长期目标进度',
        type: 'radar',
        data: [
          {
            value: dataValues.length > 0 ? dataValues : [0],
            name: '当前进度',
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#3b82f6' // blue-500
            },
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.4)'
            },
            lineStyle: {
              width: 2,
              color: '#3b82f6'
            }
          }
        ]
      }
    ]
  }
})
</script>

<template>
  <div class="w-full h-full min-h-[300px]">
    <div v-if="radarData.length === 0" class="h-full flex items-center justify-center text-gray-400">
      暂未设定长期目标
    </div>
    <v-chart v-else class="chart w-full h-full" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart {
  height: 300px;
}
</style>
