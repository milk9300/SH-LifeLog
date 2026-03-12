<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDashboardStore } from '../stores/dashboard'
import { useProjectStore } from '../stores/project'
import { useBrainstormStore } from '../stores/brainstorm'
import { brainstormApi } from '../api/brainstorm'
import { taskApi } from '../api/task'
import { projectApi } from '../api/project'
import { planApi } from '../api/plan'
import { focusApi } from '../api/focus'
import { ref, computed } from 'vue'

import { 
  FolderKanban, Lightbulb, ListTodo, Activity, Target, 
  BookOpen, Shield, Calendar, Plus, Sparkles, Clock, 
  Zap, ArrowRight, CheckCircle2, MessageSquare, Briefcase
} from 'lucide-vue-next'
import TrendChart from '../components/charts/TrendChart.vue'
import DistributionChart from '../components/charts/DistributionChart.vue'
import RadarChart from '../components/charts/RadarChart.vue'
import FunnelChart from '../components/charts/FunnelChart.vue'
import HeatmapChart from '../components/charts/HeatmapChart.vue'

const dashboardStore = useDashboardStore()
const projectStore = useProjectStore()
const brainstormStore = useBrainstormStore()

const { stats, isLoading } = storeToRefs(dashboardStore)

const trendData = ref({ dates: [], brainstorms: [], tasks: [] })
const distributionData = ref([])
const radarData = ref([])
const funnelData = ref([])
const heatmapData = ref([])
const activePlansList = ref([])
const recentBrainstorms = ref([])
const dailyFocusTasks = ref([])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好，追梦人'
  if (hour < 12) return '早安，指挥官'
  if (hour < 14) return '午安，核心时刻'
  if (hour < 18) return '下午好，持续输出中'
  if (hour < 22) return '晚安，总结与沉淀'
  return '夜深了，注意休息'
})

const currentDate = computed(() => {
  return new Intl.DateTimeFormat('zh-CN', { 
    month: 'long', day: 'numeric', weekday: 'long' 
  }).format(new Date())
})

const formatDateStr = (d) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const extractDate = (dateStr) => {
  if (!dateStr) return ''
  return dateStr.split('T')[0].split(' ')[0]
}

const fetchDashboardData = async () => {
    try {
        await dashboardStore.fetchStats()
        
        const [tasksRes, projectsRes, brainstormsRes, plansRes, focusRes] = await Promise.all([
            taskApi.getTasks({ limit: 1000 }),
            projectApi.getProjects({ limit: 100 }),
            brainstormApi.getBrainstorms({ limit: 1000 }),
            planApi.getPlans({ limit: 100 }),
            focusApi.getRecords({ is_today: true, status: 'todo' })
        ])

        const dates = []
        const brainstormCounts = []
        const taskCounts = []
        for (let i = 6; i >= 0; i--) {
            const d = new Date()
            d.setDate(d.getDate() - i)
            const currentDayStr = formatDateStr(d)
            dates.push(currentDayStr)
            brainstormCounts.push(brainstormsRes.filter(b => extractDate(b.created_at) === currentDayStr).length)
            taskCounts.push(tasksRes.filter(t => t.status === 'done' && extractDate(t.updated_at || t.created_at) === currentDayStr).length)
        }
        trendData.value = { dates: dates.map(d => d.slice(5)), brainstorms: brainstormCounts, tasks: taskCounts }
        
        const activeProjects = projectsRes.filter(p => p.status === 'active')
        distributionData.value = activeProjects.map(proj => ({ name: proj.name, value: tasksRes.filter(t => t.project_id === proj.id).length })).filter(i => i.value > 0)
        
        const activePlans = plansRes.filter(p => p.status === 'active')
        activePlansList.value = await Promise.all(activePlans.map(async (plan) => {
            const milestones = await planApi.getMilestones(plan.id)
            const progress = milestones.length === 0 ? 0 : Math.round((milestones.filter(m => m.status === 'done').length / milestones.length) * 100)
            return { ...plan, progress }
        }))
        
        radarData.value = activePlansList.value.slice(0, 6).map(p => ({ name: p.title, progress: p.progress }))
        
        funnelData.value = [
            { value: brainstormsRes.length + tasksRes.filter(t => !t.brainstorm_id).length, name: '产生想法与待办' },
            { value: tasksRes.length, name: '建立实际任务' },
            { value: tasksRes.filter(t => t.status === "done").length, name: '最终完成任务' }
        ]

        const activityMap = {}
        const addActivity = (d) => { if(d) activityMap[d] = (activityMap[d] || 0) + 1 }
        brainstormsRes.forEach(b => addActivity(extractDate(b.created_at)))
        tasksRes.forEach(t => { addActivity(extractDate(t.created_at)); if(t.status === 'done') addActivity(extractDate(t.updated_at || t.created_at)) })
        heatmapData.value = Object.keys(activityMap).map(d => [d, activityMap[d]])

        recentBrainstorms.value = brainstormsRes.slice(0, 3)
        
        // 优先显示标记为“今日聚焦”的任务，若无则显示其他未完成任务
        let focusItems = focusRes.sort((a, b) => a.priority - b.priority)
        if (focusItems.length === 0) {
          // 如果没有标记为今日的任务，则获取所有未完成的任务作为候补
          const allFocusRes = await focusApi.getRecords({ status: 'todo' })
          focusItems = allFocusRes.sort((a, b) => a.priority - b.priority)
        }
        dailyFocusTasks.value = focusItems.slice(0, 3)

    } catch (e) { console.error(e) }
}

onMounted(() => {
    fetchDashboardData()
})
</script>

<template>
  <div class="animate-in space-y-8 max-w-[1600px] mx-auto pb-12">
    <!-- Header Section: Greeting & Quick Actions -->
    <header class="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-8">
      <div>
        <div class="flex items-center gap-2 text-primary font-bold mb-1">
          <Sparkles class="w-5 h-5" />
          <span class="text-sm uppercase tracking-widest">{{ currentDate }}</span>
        </div>
        <h1 class="text-4xl font-black text-gray-900 tracking-tight">{{ greeting }}</h1>
        <p class="text-gray-500 mt-2 text-lg font-medium">这是您的生命记录总线与数字指挥中心。</p>
      </div>
      
      <!-- Quick Action Panel -->
      <div class="flex items-center gap-3">
        <button @click="$router.push('/brainstorm')" class="flex items-center gap-2 px-6 py-3 bg-white border border-gray-100 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all text-gray-700 font-bold group">
          <div class="w-8 h-8 bg-yellow-50 text-yellow-600 rounded-xl flex items-center justify-center group-hover:bg-yellow-100 transition-colors"><Lightbulb class="w-4 h-4" /></div>
          捕捉灵感
        </button>
        <button @click="$router.push('/tasks')" class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-2xl shadow-lg shadow-primary/20 hover:shadow-xl hover:-translate-y-0.5 transition-all font-bold">
          <div class="w-8 h-8 bg-white/20 rounded-xl flex items-center justify-center"><Plus class="w-4 h-4" /></div>
          新增任务
        </button>
      </div>
    </header>

    <!-- Stats Grid: Horizontal Overview -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-if="isLoading" v-for="i in 4" :key="i" class="h-32 bg-gray-100 rounded-3xl animate-pulse"></div>
      <template v-else>
        <div @click="$router.push('/projects')" class="bg-white/70 backdrop-blur-xl border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer group relative overflow-hidden">
          <div class="absolute -right-4 -top-4 w-16 h-16 bg-blue-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div class="relative flex flex-col gap-3">
            <div class="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center"><FolderKanban class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">活跃项目</p>
              <h4 class="text-2xl font-black text-gray-800">{{ stats.active_projects }}</h4>
            </div>
          </div>
        </div>

        <div @click="$router.push('/brainstorm')" class="bg-white/70 backdrop-blur-xl border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer group relative overflow-hidden">
          <div class="absolute -right-4 -top-4 w-16 h-16 bg-orange-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div class="relative flex flex-col gap-3">
            <div class="w-10 h-10 bg-orange-50 text-orange-600 rounded-xl flex items-center justify-center"><Zap class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">待处理灵感</p>
              <h4 class="text-2xl font-black text-gray-800">{{ stats.pending_brainstorms }}</h4>
            </div>
          </div>
        </div>
        <div @click="$router.push('/articles')" class="bg-white/70 backdrop-blur-xl border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer group relative overflow-hidden">
          <div class="absolute -right-4 -top-4 w-16 h-16 bg-purple-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div class="relative flex flex-col gap-3">
            <div class="w-10 h-10 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center"><BookOpen class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">累计文章</p>
              <h4 class="text-2xl font-black text-gray-800">{{ stats.total_reflections }}</h4>
            </div>
          </div>
        </div>
        <div @click="$router.push('/vault')" class="bg-white/70 backdrop-blur-xl border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer group relative overflow-hidden">
          <div class="absolute -right-4 -top-4 w-16 h-16 bg-slate-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div class="relative flex flex-col gap-3">
            <div class="w-10 h-10 bg-slate-100 text-slate-700 rounded-xl flex items-center justify-center"><Shield class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">密钥保管</p>
              <h4 class="text-2xl font-black text-gray-800">{{ stats.total_credentials }}</h4>
            </div>
          </div>
        </div>
      </template>
    </section>

    <!-- Main Content: Focus Area & Side Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Left Column (8/12): Focus and Charts -->
      <div class="lg:col-span-8 space-y-8">
        <!-- Daily Focus Tasks -->
        <section class="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-primary/10 text-primary rounded-xl flex items-center justify-center"><Target class="w-5 h-5" /></div>
              <h3 class="text-xl font-black text-gray-800">今日专注焦点</h3>
            </div>
            <button @click="$router.push('/tasks')" class="text-sm font-bold text-gray-400 hover:text-primary transition-colors flex items-center gap-1">查看全部 <ArrowRight class="w-3 h-3" /></button>
          </div>
          
          <div v-if="isLoading" class="space-y-4">
            <div v-for="i in 3" :key="i" class="h-20 bg-gray-50 rounded-2xl animate-pulse"></div>
          </div>
          <div v-else-if="dailyFocusTasks.length === 0" class="py-12 text-center flex flex-col items-center">
            <div class="w-16 h-16 bg-emerald-50 text-emerald-500 rounded-full flex items-center justify-center mb-4"><CheckCircle2 class="w-8 h-8" /></div>
            <h4 class="text-gray-800 font-bold">太棒了！今日任务已全部清空</h4>
            <p class="text-gray-400 text-sm mt-1">稍微休息一下，或者捕获一些新的灵感吧。</p>
          </div>
          <div v-else class="grid gap-4">
            <div v-for="task in dailyFocusTasks" :key="task.id" @click="$router.push('/tasks')" class="flex items-center gap-4 p-4 rounded-2xl hover:bg-gray-50 transition-all cursor-pointer border border-transparent hover:border-gray-100">
              <div :class="[
                'w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center',
                task.priority === 0 ? 'border-red-400 bg-red-50' : 
                task.priority === 1 ? 'border-blue-400 bg-blue-50' :
                task.priority === 2 ? 'border-amber-400 bg-amber-50' : 'border-gray-300'
              ]">
                <div v-if="task.priority === 0" class="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h4 class="font-bold text-gray-800 truncate">{{ task.title }}</h4>
                  <span v-if="task.priority === 0" class="px-1.5 py-0.5 rounded bg-red-100 text-[8px] font-black text-red-600 uppercase italic">Urgent</span>
                </div>
                <div class="flex items-center gap-3 mt-1 text-[11px] text-gray-400 font-semibold">
                  <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {{ extractDate(task.created_at) }}</span>
                  <span v-if="task.deadline" class="flex items-center gap-1 text-blue-500/70 uppercase tracking-tighter"><Calendar class="w-3 h-3" /> {{ extractDate(task.deadline) }}</span>
                </div>
              </div>
              <ArrowRight class="w-4 h-4 text-gray-200" />
            </div>
          </div>
        </section>

        <!-- Efficiency Trends -->
        <div class="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100">
          <div class="flex items-center gap-3 mb-8">
            <div class="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center"><Activity class="w-5 h-5" /></div>
            <h3 class="text-xl font-black text-gray-800">效能趋势分析</h3>
          </div>
          <TrendChart :trendData="trendData" />
        </div>
      </div>

      <!-- Right Column (4/12): Sidebar Activities -->
      <aside class="lg:col-span-4 space-y-8">
        <!-- Recent Sparks -->
        <section class="bg-indigo-600 rounded-[2rem] p-8 shadow-xl text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div class="relative z-10">
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center"><Sparkles class="w-5 h-5" /></div>
                <h3 class="text-xl font-black">近期灵感火花</h3>
              </div>
              <button @click="$router.push('/brainstorm')" class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"><Plus class="w-4 h-4" /></button>
            </div>

            <div v-if="isLoading" class="space-y-4">
              <div v-for="i in 3" :key="i" class="h-16 bg-white/10 rounded-2xl animate-pulse"></div>
            </div>
            <div v-else-if="recentBrainstorms.length === 0" class="py-8 text-center text-white/60">
              <MessageSquare class="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p class="font-bold">暂无新火花</p>
            </div>
            <div v-else class="space-y-4">
              <div v-for="b in recentBrainstorms" :key="b.id" @click="$router.push('/brainstorm')" class="p-4 bg-white/10 rounded-2xl hover:bg-white/20 transition-all cursor-pointer border border-white/5">
                <p class="font-bold text-sm leading-relaxed mb-2 line-clamp-2">{{ b.content }}</p>
                <div class="flex items-center justify-between text-[10px] font-black uppercase text-white/50 tracking-widest">
                  <span>{{ extractDate(b.created_at) }}</span>
                  <span class="px-2 py-0.5 bg-white/20 rounded-md">IDEA</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Long-term Plans -->
        <section class="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
          <div class="flex items-center justify-between mb-8">
            <h3 class="font-black text-gray-800">活跃计划 ({{ stats.active_plans }})</h3>
            <button @click="$router.push('/plans')" class="text-sm font-bold text-primary">管理</button>
          </div>

          <div v-if="isLoading" class="space-y-6">
            <div v-for="i in 2" :key="i" class="h-32 bg-gray-50 rounded-2xl animate-pulse"></div>
          </div>
          <div v-else-if="activePlansList.length === 0" class="py-12 text-center text-gray-400">
            <p>暂无活跃计划</p>
          </div>
          <div v-else class="space-y-6">
            <div v-for="plan in activePlansList.slice(0, 3)" :key="plan.id" @click="$router.push(`/plans/${plan.id}`)" class="group cursor-pointer">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-bold text-gray-700 group-hover:text-primary transition-colors truncate pr-2">{{ plan.title }}</h4>
                <span class="text-xs font-black text-primary">{{ plan.progress }}%</span>
              </div>
              <div class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-primary transition-all duration-1000" :style="{ width: `${plan.progress}%` }"></div>
              </div>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <!-- Bottom Grids: Charts & Heatmap -->
    <div v-if="!isLoading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 pt-8 border-t border-gray-100">
      <div class="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100">
        <h3 class="font-black text-gray-800 mb-6 flex items-center gap-2">核心目标推进</h3>
        <RadarChart :radarData="radarData" />
      </div>
      <div class="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100">
        <h3 class="font-black text-gray-800 mb-6 flex items-center gap-2">灵感转化漏斗</h3>
        <FunnelChart :funnelData="funnelData" />
      </div>
      <div class="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100">
        <h3 class="font-black text-gray-800 mb-6 flex items-center gap-2">核心精力分布</h3>
        <DistributionChart :distributionData="distributionData" />
      </div>
    </div>

    <div v-if="!isLoading" class="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100">
      <h3 class="font-black text-gray-800 mb-8 flex items-center gap-2">持续行动力网格 <Activity class="w-4 h-4" /></h3>
      <HeatmapChart :heatmapData="heatmapData" />
    </div>
  </div>
</template>
