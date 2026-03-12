<script setup>
import { ref, watch } from 'vue'
import { CheckCircle2, X, Info } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  editingRecord: Object,
  projects: Array,
  plans: Array
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  title: '',
  description: '',
  priority: 1,
  status: 'todo',
  is_today: false,
  project_id: null,
  plan_id: null,
  deadline: null,
  category: 'daily' // internal UI state: project, plan, daily
})

const selectedSourceId = ref(null)

watch(() => props.show, (newVal) => {
  if (newVal) {
    selectedSourceId.value = null
    if (props.editingRecord) {
      form.value = { 
        ...props.editingRecord,
        category: props.editingRecord.project_id ? 'project' : (props.editingRecord.plan_id ? 'plan' : 'daily')
      }
    } else {
      form.value = {
        title: '',
        description: '',
        priority: 1,
        status: 'todo',
        is_today: false,
        project_id: null,
        plan_id: null,
        deadline: null,
        category: 'daily'
      }
    }
  }
})

watch(selectedSourceId, (newId) => {
  if (!newId) return
  
  if (form.value.category === 'project') {
    const proj = props.projects.find(p => p.id === newId)
    if (proj) {
      form.value.title = proj.name
      form.value.description = proj.description || ''
      form.value.project_id = proj.id
      form.value.plan_id = null
    }
  } else if (form.value.category === 'plan') {
    const plan = props.plans.find(p => p.id === newId)
    if (plan) {
      form.value.title = plan.title
      form.value.description = plan.description || ''
      form.value.plan_id = plan.id
      form.value.project_id = null
    }
  }
})

watch(() => form.value.category, (newCat) => {
  selectedSourceId.value = null
  if (newCat === 'daily') {
    form.value.project_id = null
    form.value.plan_id = null
  }
})

const handleSave = () => {
  if (!form.value.title.trim()) return
  const { category, ...payload } = form.value
  emit('save', payload, props.editingRecord ? props.editingRecord.id : null)
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg relative z-10 animate-in flex flex-col max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
        <h3 class="text-xl font-black text-gray-800 flex items-center gap-2">
          <CheckCircle2 class="w-6 h-6 text-emerald-500" />
          {{ editingRecord ? '编辑记录 (Focus Edit)' : '新建记录 (Quick Focus)' }}
        </h3>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        <!-- 分类选择器 -->
        <div>
           <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">事务分类 Category</label>
           <div class="grid grid-cols-3 gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100">
             <label v-for="cat in [
               { id: 'project', icon: '📦', name: '项目' },
               { id: 'plan', icon: '🎯', name: '计划' },
               { id: 'daily', icon: '☀️', name: '日常' }
             ]" :key="cat.id"
               :class="['cursor-pointer py-2 rounded-lg text-center transition-all font-bold flex flex-col items-center justify-center gap-0.5', 
                 form.category === cat.id ? 'bg-white shadow-sm ring-1 ring-black/5 text-emerald-600' : 'text-gray-400 hover:bg-gray-200/50'
               ]"
             >
               <span class="text-lg leading-none">{{ cat.icon }}</span>
               <span class="text-[9px] uppercase tracking-tighter">{{ cat.name }}</span>
               <input type="radio" :value="cat.id" v-model="form.category" class="hidden">
             </label>
           </div>
        </div>

        <!-- 快速选择器 (仅项目/计划) -->
        <div v-if="form.category !== 'daily'" class="animate-in slide-in-from-top-2 duration-300">
          <label class="block text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-1">
            {{ form.category === 'project' ? '选择已有项目 (Quick Fill)' : '选择已有计划 (Quick Fill)' }}
          </label>
          <select v-model="selectedSourceId" class="w-full bg-emerald-50/50 border border-emerald-100 rounded-xl px-4 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 transition-all text-gray-700 font-bold text-sm">
            <option :value="null">-- 请选择以快速补全 --</option>
            <template v-if="form.category === 'project'">
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </template>
            <template v-else>
              <option v-for="pl in plans" :key="pl.id" :value="pl.id">{{ pl.title }}</option>
            </template>
          </select>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">内容 Record Title *</label>
          <input v-model="form.title" type="text" placeholder="想要专注完成的琐事或活动..." class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-bold text-gray-800" autofocus @keyup.enter="handleSave">
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">详述备注 Description (可选)</label>
          <textarea v-model="form.description" rows="2" placeholder="添加一些背景说明..." class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-gray-600 resize-none text-sm"></textarea>
        </div>

        <div>
           <label class="block text-xs font-bold text-gray-500 uppercase mb-2">优先级 Priority</label>
           <div class="grid grid-cols-2 gap-2">
              <label :class="['border rounded-lg p-2 cursor-pointer transition-all flex flex-col items-center justify-center text-center h-16', form.priority === 0 ? 'bg-red-50 border-red-200 text-red-700 shadow-sm ring-1 ring-red-500' : 'bg-white border-gray-200 hover:border-red-200 text-gray-400']">
                <input type="radio" :value="0" v-model="form.priority" class="hidden">
                <span class="font-bold text-sm">🔥 Do First</span>
                <span class="text-[10px] opacity-80">重要且紧急</span>
              </label>
              <label :class="['border rounded-lg p-2 cursor-pointer transition-all flex flex-col items-center justify-center text-center h-16', form.priority === 1 ? 'bg-blue-50 border-blue-200 text-blue-700 shadow-sm ring-1 ring-blue-500' : 'bg-white border-gray-200 hover:border-blue-200 text-gray-400']">
                <input type="radio" :value="1" v-model="form.priority" class="hidden">
                <span class="font-bold text-sm">📅 Schedule</span>
                <span class="text-[10px] opacity-80">重要不紧急</span>
              </label>
              <label :class="['border rounded-lg p-2 cursor-pointer transition-all flex flex-col items-center justify-center text-center h-16', form.priority === 2 ? 'bg-amber-50 border-amber-200 text-amber-700 shadow-sm ring-1 ring-amber-500' : 'bg-white border-gray-200 hover:border-amber-200 text-gray-400']">
                <input type="radio" :value="2" v-model="form.priority" class="hidden">
                <span class="font-bold text-sm">🤝 Delegate</span>
                <span class="text-[10px] opacity-80">紧急不重要</span>
              </label>
              <label :class="['border rounded-lg p-2 cursor-pointer transition-all flex flex-col items-center justify-center text-center h-16', form.priority === 3 ? 'bg-gray-100 border-gray-300 text-gray-600 shadow-sm ring-1 ring-gray-400' : 'bg-white border-gray-200 hover:border-gray-300 text-gray-400']">
                <input type="radio" :value="3" v-model="form.priority" class="hidden">
                <span class="font-bold text-sm">🗑️ Don't Do</span>
               </label>
            </div>
         </div>
 
         <div>
           <label class="block text-xs font-bold text-gray-500 uppercase mb-1">截至日期 Deadline (可选)</label>
           <input v-model="form.deadline" type="datetime-local" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-bold text-gray-800">
         </div>
 
         <div class="flex items-center justify-between p-4 bg-emerald-50 rounded-2xl border border-emerald-100">
          <div class="flex items-center gap-2">
            <Info class="w-4 h-4 text-emerald-600" />
            <span class="text-sm font-bold text-emerald-800">设为今日重点 (Today Focus)</span>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="form.is_today" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
          </label>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 shrink-0">
        <button @click="emit('close')" class="px-4 py-2 rounded-xl font-bold text-gray-600 bg-white border border-gray-200 hover:bg-gray-100 transition-colors">
          取消
        </button>
        <button @click="handleSave" :disabled="!form.title.trim()" class="px-6 py-2.5 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:hover:shadow-none">
          {{ editingRecord ? '保存更新' : '立即创建' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 20px; }
</style>
