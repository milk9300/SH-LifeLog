<script setup>
import { ref, watch } from 'vue'
import { CheckCircle2, X } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  editingTask: Object,
  projects: Array,
  plans: Array
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  title: '',
  description: '',
  project_id: null,
  is_today: false,
  due_date: '',
  priority: 0,
  task_type: 'feature',
  category: 'daily', // project | long_term | daily | memo | task
  deliverable: '',
  status: 'todo'
})

const taskTypeLabels = {
  feature: '🚀 新需求',
  bugfix: '🐛 缺陷修复',
  optimize: '🛠️ 优化/重构',
  chore: '⚙️ 杂项/基建',
  research: '🔬 技术预研',
  design: '🎨 设计/原型'
}

const taskTypeColors = {
  feature: 'bg-blue-50 text-blue-600 border-blue-200/60',
  bugfix: 'bg-red-50 text-red-600 border-red-200/60',
  optimize: 'bg-emerald-50 text-emerald-600 border-emerald-200/60',
  chore: 'bg-slate-50 text-slate-600 border-slate-200/60',
  research: 'bg-purple-50 text-purple-600 border-purple-200/60',
  design: 'bg-orange-50 text-orange-600 border-orange-200/60'
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    selectedSourceId.value = null // Reset auto-fill selection
    if (props.editingTask) {
      form.value = { 
        ...props.editingTask,
        due_date: props.editingTask.due_date ? new Date(props.editingTask.due_date).toISOString().slice(0, 16) : ''
      }
    } else {
      form.value = {
        title: '',
        description: '',
        project_id: null,
        is_today: false,
        due_date: '',
        priority: 0, // 0: Do First, 1: Schedule, 2: Delegate, 3: Don't Do
        task_type: 'feature',
        category: 'daily',
        deliverable: '',
        status: 'todo'
      }
    }
  }
})

const selectedSourceId = ref(null)

watch(selectedSourceId, (newId) => {
  if (!newId) return
  
  if (form.value.category === 'project') {
    const proj = props.projects.find(p => p.id === newId)
    if (proj) {
      form.value.title = proj.name
      form.value.description = proj.description || ''
      form.value.project_id = proj.id
    }
  } else if (form.value.category === 'long_term') {
    const plan = props.plans.find(p => p.id === newId)
    if (plan) {
      form.value.title = plan.title
      form.value.description = plan.description || ''
    }
  }
})

watch(() => form.value.category, () => {
  selectedSourceId.value = null // Clear when switching tabs
})

const handleSave = () => {
  if (!form.value.title.trim()) return
  
  const payload = { ...form.value }
  // Optional date handling
  if (!payload.due_date) {
    payload.due_date = null
  } else {
    // Ensure ISO format if necessary for backend
    payload.due_date = new Date(payload.due_date).toISOString()
  }

  // Handle constraints based on category
  if (payload.category === 'project') {
    payload.task_type = 'feature' // Reset unused field
  }
  if (payload.category === 'long_term') {
     payload.task_type = 'feature'
  }
  if (payload.category === 'daily') {
    payload.is_today = true
    payload.task_type = 'feature'
  }
  if (payload.category === 'memo') {
     payload.task_type = 'feature'
  }
  if (payload.category === 'task') {
    // Keep specified task_type
  }

  emit('save', payload, props.editingTask ? props.editingTask.id : null)
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-3xl relative z-10 animate-in flex flex-col max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
        <h3 class="text-xl font-black text-gray-800 flex items-center gap-2">
          <CheckCircle2 class="w-6 h-6 text-indigo-500" />
          {{ editingTask ? '编辑任务 (Task Planning)' : '新建任务 (Task Planning)' }}
        </h3>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scrollable Content Layout -->
      <div class="flex-1 overflow-y-auto p-6 md:p-8 custom-scrollbar">

        <div class="space-y-8">
          
          <!-- Column 1: Core Fields (Goal & Type) -->
          <div class="space-y-6">
            <!-- 目标维度 -->
            <div>
              <div class="space-y-4">
                <!-- Source Selector for Projects/Plans -->
                <div v-if="['project', 'long_term'].includes(form.category)" class="animate-in slide-in-from-top-1">
                  <label class="block text-xs font-bold text-indigo-500 uppercase mb-1">
                    {{ form.category === 'project' ? '关联已有项目 (Linked Project)' : '关联已有长期计划 (Linked Plan)' }}
                  </label>
                  <select v-model="selectedSourceId" class="w-full bg-indigo-50 border border-indigo-100 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-gray-700 font-bold">
                    <option :value="null">-- 选择以快速填充标题与描述 --</option>
                    <template v-if="form.category === 'project'">
                      <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                    </template>
                    <template v-else>
                      <option v-for="pl in plans" :key="pl.id" :value="pl.id">{{ pl.title }}</option>
                    </template>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">标题 Title *</label>
                  <input v-model="form.title" type="text" placeholder="一句话描述要实现的功能或修复..." class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-bold text-gray-800" autofocus>
                </div>
                <!-- 详述与项目仅在复杂分类（项目/长期）下展示 -->
                <template v-if="['project', 'long_term'].includes(form.category)">
                  <div class="animate-in slide-in-from-top-2">
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">详述 Description</label>
                    <textarea v-model="form.description" rows="3" placeholder="任务详细背景、步骤或技术难点..." class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-gray-600 resize-none text-sm"></textarea>
                  </div>
                  <div class="animate-in slide-in-from-top-2">
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">所属宏观项目 Project (可选)</label>
                    <select v-model="form.project_id" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all text-gray-700 font-medium">
                      <option :value="null">-- Inbox (不挂载具体宏观项目) --</option>
                      <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                    </select>
                  </div>
                </template>

                <!-- 任务类型 (仅在项目任务或相关分类下展示) -->
                <div v-if="['task', 'daily'].includes(form.category)" class="animate-in slide-in-from-top-2">
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-2">任务类型 Type</label>
                  <div class="grid grid-cols-2 gap-2">
                    <button 
                      v-for="(label, type) in taskTypeLabels" 
                      :key="type"
                      type="button"
                      @click="form.task_type = type"
                      :class="[
                        'px-3 py-2 rounded-xl border text-xs font-bold transition-all text-left flex items-center justify-between group',
                        form.task_type === type ? (taskTypeColors[type] + ' ring-1 ring-indigo-500 shadow-sm') : 'bg-white border-gray-200 text-gray-500 hover:border-indigo-300'
                      ]"
                    >
                      {{ label }}
                      <CheckCircle2 v-if="form.task_type === type" class="w-3 h-3 text-indigo-600" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 类型维度: 已在全局 Time HQ 中移除，此组件不再需要渲染任务类型表单 -->
          </div>

            <!-- 输出维度 -->
            <div class="animate-in slide-in-from-top-2">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-1.5 h-4 bg-emerald-500 rounded-full"></div>
                <h4 class="font-bold text-gray-700">3. 输出 (Output / Deliverable)</h4>
              </div>
              <div>
                <input v-model="form.deliverable" type="text" placeholder="例如：代码提交/PR、架构文档、产出分析文章..." class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-medium text-sm text-gray-700">
                <p class="text-[11px] text-gray-400 mt-1">明确的交付物能指引任务向更有价值的资产（Knowledge）沉淀。</p>
              </div>
            </div>
          </div>
        </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 shrink-0">
        <button @click="emit('close')" class="px-6 py-2.5 rounded-xl font-bold text-gray-600 bg-white border border-gray-200 hover:bg-gray-100 transition-colors">
          取消
        </button>
        <button @click="handleSave" :disabled="!form.title.trim()" class="px-8 py-2.5 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:hover:shadow-none">
          {{ editingTask ? '保存更新' : '创建任务' }}
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 20px; }
</style>
