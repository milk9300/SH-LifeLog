import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart, RadarChart, FunnelChart, HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, CalendarComponent, VisualMapComponent } from 'echarts/components'

use([
    CanvasRenderer,
    PieChart,
    LineChart,
    RadarChart,
    FunnelChart,
    HeatmapChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    CalendarComponent,
    VisualMapComponent
])

import { createPinia } from 'pinia'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.component('v-chart', ECharts)
app.mount('#app')
