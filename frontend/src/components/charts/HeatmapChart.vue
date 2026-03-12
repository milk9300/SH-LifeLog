<script setup>
import { computed } from 'vue'

const props = defineProps({
  heatmapData: {
    type: Array, // Array of [dateString (yyyy-MM-dd), count]
    required: true,
    default: () => []
  }
})

const option = computed(() => {
  // Try to set dynamic range for the current year or last 6 months
  const now = new Date()
  const currentYear = now.getFullYear()
  const halfYearAgo = new Date(now.getFullYear(), now.getMonth() - 5, 1)

  const startDateStr = `${halfYearAgo.getFullYear()}-${String(halfYearAgo.getMonth() + 1).padStart(2, '0')}-01`
  const endDateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  return {
    tooltip: {
      position: 'top',
      formatter: function (p) {
        const format = window.echarts ? window.echarts.format : { formatTime: (t, d) => d }
        // p.data is [date, value]
        return p.data[0] + ' : ' + p.data[1] + ' 项活动'
      }
    },
    visualMap: {
      min: 0,
      max: props.heatmapData.length > 0 ? Math.max(...props.heatmapData.map(i => i[1]), 5) : 5,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      top: 0,
      inRange: {
        // GitHub style green gradient
        color: ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
      }
    },
    calendar: [
      {
        range: [startDateStr, endDateStr],
        cellSize: ['auto', 20],
        right: 20,
        left: 40,
        top: 60,
        yearLabel: { show: false },
        dayLabel: {
          firstDay: 1,
          nameMap: ['周日', '一', '二', '三', '四', '五', '六'],
          color: '#6b7280'
        },
        monthLabel: {
          nameMap: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
          color: '#6b7280'
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 4,
          borderRadius: 4
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: props.heatmapData
      }
    ]
  }
})
</script>

<template>
  <div class="w-full h-full min-h-[250px]">
    <v-chart class="chart w-full h-full" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart {
  height: 250px;
}
</style>
