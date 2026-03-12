<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { usePlanStore } from '../stores/plan'
import { Target, Plus, Calendar, Trash2 } from 'lucide-vue-next'

const router = useRouter()
const planStore = usePlanStore()
const { plans, isLoading } = storeToRefs(planStore)

const showAddModal = ref(false)
const newPlan = ref({ title: '', description: '', start_date: '', target_date: '' })

const handleAddPlan = async () => {
    if (!newPlan.value.title.trim()) return
    await planStore.createPlan(newPlan.value)
    showAddModal.value = false
    newPlan.value = { title: '', description: '', start_date: '', target_date: '' }
}

const statusConfig = {
    active: { label: '进行中', color: 'text-blue-600 bg-blue-50', border: 'border-blue-200' },
    paused: { label: '已搁置', color: 'text-amber-600 bg-amber-50', border: 'border-amber-200' },
    completed: { label: '已达成', color: 'text-emerald-600 bg-emerald-50', border: 'border-emerald-200' }
}

onMounted(() => {
    planStore.fetchPlans()
})
</script>

<template>
  <div class="h-full flex flex-col gap-6 animate-in">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center shadow-sm"><Target class="w-6 h-6" /></div>
        <div>
          <h1 class="text-2xl font-black text-gray-800 tracking-tight">长线计划</h1>
          <p class="text-gray-500 font-medium text-sm mt-0.5">目标驱动的知识沉淀与技能树点亮</p>
        </div>
      </div>
      <button @click="showAddModal = true" class="flex items-center gap-2 px-5 py-2.5 bg-gray-900 text-white font-bold rounded-xl hover:bg-gray-800 transition-all">
        <Plus class="w-5 h-5" />种下一棵树
      </button>
    </div>

    <div v-if="isLoading" class="text-center py-20 text-gray-400">加载中...</div>
    <div v-else-if="plans.length === 0" class="flex flex-col items-center justify-center py-20 border-2 border-dashed border-gray-200 rounded-3xl bg-gray-50/50">
        <Target class="w-16 h-16 text-gray-300 mb-4" />
        <h3 class="text-xl font-bold text-gray-700 mb-2">种一棵树最好的时间是十年前</h3>
        <button @click="showAddModal = true" class="px-6 py-2.5 bg-white text-gray-800 font-bold border border-gray-200 rounded-xl mt-6">立即创建计划</button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="plan in plans" :key="plan.id" @click="router.push(`/plans/${plan.id}`)" class="group bg-white border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-xl transition-all cursor-pointer overflow-hidden flex flex-col min-h-[220px]">
        <div class="flex justify-between items-start mb-4">
          <div @click.stop="planStore.toggleStatus(plan)" class="px-2.5 py-1 rounded-lg text-xs font-bold border" :class="[statusConfig[plan.status]?.color, statusConfig[plan.status]?.border]">{{ statusConfig[plan.status]?.label }}</div>
          <button @click.stop="planStore.removePlan(plan.id)" class="p-2 text-gray-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"><Trash2 class="w-4 h-4" /></button>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2 line-clamp-2">{{ plan.title }}</h3>
        <p class="text-sm text-gray-500 line-clamp-2 flex-1">{{ plan.description || '暂无描述' }}</p>

        <div class="mt-6 pt-4 border-t border-gray-50 flex items-end justify-between">
            <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-400"><Calendar class="w-3.5 h-3.5" />{{ plan.start_date || '未定' }} - {{ plan.target_date || '未定' }}</div>
            <div class="relative w-14 h-14 flex items-center justify-center shrink-0">
                <svg class="w-full h-full transform -rotate-90">
                    <circle cx="28" cy="28" r="24" fill="transparent" stroke="#F3F4F6" stroke-width="6" />
                    <circle cx="28" cy="28" r="24" fill="transparent" stroke="currentColor" stroke-width="6" stroke-dasharray="150" :stroke-dashoffset="150 - (150 * plan.progress) / 100" class="text-indigo-600 transition-all duration-1000" stroke-linecap="round" />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center flex-col"><span class="text-sm font-black text-gray-700 leading-none">{{ plan.progress }}</span><span class="text-[9px] font-bold text-gray-400 -mt-0.5">%</span></div>
            </div>
        </div>
      </div>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-gray-900/30 backdrop-blur-sm" @click="showAddModal = false"></div>
      <div class="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-lg relative z-10 animate-in">
        <h3 class="text-2xl font-black text-gray-800 mb-6 flex items-center gap-2"><Target class="w-6 h-6 text-indigo-600" />规划长线目标</h3>
        <div class="space-y-5 mb-8">
          <div><label class="block text-sm font-bold text-gray-600 mb-2">计划名称 (目标)</label><input v-model="newPlan.title" type="text" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 font-bold" placeholder="例如: 3个月完成Java系统学习"></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-sm font-bold text-gray-600 mb-2">开始时间</label><input v-model="newPlan.start_date" type="month" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 font-bold"></div>
            <div><label class="block text-sm font-bold text-gray-600 mb-2">预期达成</label><input v-model="newPlan.target_date" type="month" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 font-bold"></div>
          </div>
          <div><label class="block text-sm font-bold text-gray-600 mb-2">目标描述</label><textarea v-model="newPlan.description" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 resize-none" rows="3"></textarea></div>
        </div>
        <div class="flex gap-4">
          <button @click="showAddModal = false" class="flex-1 py-3.5 text-gray-600 font-bold bg-gray-50 rounded-xl transition-colors">取消</button>
          <button @click="handleAddPlan" :disabled="!newPlan.title.trim()" class="flex-1 py-3.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50">立下 Flag</button>
        </div>
      </div>
    </div>
  </div>
</template>
