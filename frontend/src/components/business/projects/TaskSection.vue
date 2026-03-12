<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, CheckCircle2, Circle, Calendar, Trash2, Edit2, Target, Beaker } from 'lucide-vue-next'
import { useProjectStore } from '../../../stores/project'
import { usePlanStore } from '../../../stores/plan'
import { storeToRefs } from 'pinia'
import { taskApi } from '../../../api/task'
import TaskModal from './TaskModal.vue'
import ProblemModal from './ProblemModal.vue'

const router = useRouter()

const projectStore = useProjectStore()
const { activeProject, tasks, projects } = storeToRefs(projectStore)

const newTaskTitle = ref('')
const newTaskType = ref('feature')
const isTaskModalOpen = ref(false)
const editingTask = ref(null)

const planStore = usePlanStore()
const { plans } = storeToRefs(planStore)

// Problem Link Logic
const isProblemModalOpen = ref(false)
const selectedProblemId = ref(null)
const initialProblemData = ref(null)

const openEditModal = (task) => {
  editingTask.value = { ...task }
  isTaskModalOpen.value = true
}

const taskTypeColors = {
  feature: 'bg-blue-50 text-blue-600 border-blue-200/60 shadow-sm shadow-blue-100/50',
  bugfix: 'bg-red-50 text-red-600 border-red-200/60 shadow-sm shadow-red-100/50',
  optimize: 'bg-emerald-50 text-emerald-600 border-emerald-200/60 shadow-sm shadow-emerald-100/50',
  chore: 'bg-slate-50 text-slate-600 border-slate-200/60 shadow-sm shadow-slate-100/50',
  research: 'bg-purple-50 text-purple-600 border-purple-200/60 shadow-sm shadow-purple-100/50',
  design: 'bg-orange-50 text-orange-600 border-orange-200/60 shadow-sm shadow-orange-100/50'
}

const taskTypeLabels = {
  feature: '🚀 新需求',
  bugfix: '🐛 缺陷修复',
  optimize: '🛠️ 优化/重构',
  chore: '⚙️ 杂项/基建',
  research: '🔬 技术预研',
  design: '🎨 设计/原型'
}

const handleAddTask = async () => {
  if (!newTaskTitle.value.trim()) return
  try {
    await taskApi.createTask({
      title: newTaskTitle.value,
      project_id: activeProject.value.id,
      task_type: newTaskType.value,
      category: 'task'
    })
    newTaskTitle.value = ''
    newTaskType.value = 'feature'
    projectStore.fetchTasks(activeProject.value.id)
  } catch (error) {
    console.error('Failed to add task', error)
  }
}

const handleSaveTask = async (payload, taskId) => {
  try {
    if (taskId) {
      await taskApi.updateTask(taskId, payload)
    } else {
      // Must enforce current project if not explicitly set
      if (!payload.project_id) {
        payload.project_id = activeProject.value.id
      }
      await taskApi.createTask(payload)
    }
    isTaskModalOpen.value = false
    projectStore.fetchTasks(activeProject.value.id)
  } catch (error) {
    console.error('Failed to save task', error)
  }
}

const toggleTaskStatus = async (task) => {
  const newStatus = task.status === 'done' ? 'todo' : 'done'
  try {
    await taskApi.updateTask(task.id, { status: newStatus })
    projectStore.fetchTasks(activeProject.value.id)
  } catch (error) {
    console.error('Failed to toggle task status', error)
  }
}


const deleteTask = async (id) => {
  if (!window.confirm('确定要删除这个任务吗？此操作不可撤销。')) return
  try {
    await taskApi.deleteTask(id)
    projectStore.fetchTasks(activeProject.value.id)
  } catch (error) {
    console.error('Failed to delete task', error)
  }
}

// 任务 → 知识沉淀（问题记录）
const convertToProblem = (task) => {
  if (task.problem_id) {
    selectedProblemId.value = task.problem_id
    initialProblemData.value = null
    isProblemModalOpen.value = true
  } else {
    selectedProblemId.value = null
    initialProblemData.value = { 
      title: task.title, 
      description: task.description || '', 
      task_id: task.id,
      category: task.task_type === 'bugfix' ? 'bug' : 'other'
    }
    isProblemModalOpen.value = true
  }
}

const handleProblemModalSuccess = () => {
  projectStore.fetchTasks(activeProject.value.id)
}
</script>

<template>
  <div v-if="activeProject">
      <div class="flex items-center gap-2 mb-2 relative">
        <div class="relative flex-1 flex items-center group">
          <Plus class="w-5 h-5 text-gray-400 absolute left-4 group-focus-within:text-indigo-500 transition-colors z-10" />
          <input 
            v-model="newTaskTitle"
            @keyup.enter="handleAddTask"
            type="text" 
            class="w-full bg-gray-50 bg-opacity-50 hover:bg-white focus:bg-white border border-transparent hover:border-gray-200 focus:border-indigo-300 rounded-2xl pl-11 pr-4 py-3 outline-none transition-all placeholder:text-gray-400 font-bold text-gray-700 shadow-sm"
            placeholder="添加新任务，按回车键保存..."
          >
        </div>
        <select 
          v-model="newTaskType" 
          class="shrink-0 bg-gray-50 bg-opacity-50 hover:bg-white focus:bg-white border border-transparent hover:border-gray-200 focus:border-indigo-300 rounded-2xl px-3 py-3 outline-none transition-all font-bold text-gray-600 shadow-sm text-sm cursor-pointer appearance-none text-center"
        >
          <option v-for="(label, val) in taskTypeLabels" :key="val" :value="val">{{ label }}</option>
        </select>
      </div>

    <div class="space-y-3">
      <div v-if="tasks.length === 0" class="text-center py-8 text-gray-400 italic text-sm border border-dashed border-gray-200 rounded-2xl">
        项目一切就绪，开始添加任务吧！
      </div>

      <div 
        v-for="task in tasks" 
        :key="task.id"
        class="group flex items-start gap-4 p-4 rounded-2xl transition-all border"
        :class="[
          task.status === 'done' 
            ? 'bg-gray-50/80 border-gray-100 opacity-60 grayscale-[0.5]' 
            : 'bg-white shadow-sm border-gray-100 hover:shadow-md hover:border-indigo-100'
        ]"
      >
        <button 
          @click="toggleTaskStatus(task)"
          class="shrink-0 mt-0.5 text-gray-300 hover:text-emerald-500 transition-colors focus:outline-none"
          :class="{'text-emerald-500': task.status === 'done'}"
        >
          <CheckCircle2 v-if="task.status === 'done'" class="w-6 h-6" />
          <Circle v-else class="w-6 h-6" />
        </button>
        
        <div class="flex flex-col flex-1 overflow-hidden">
          <div class="flex items-start justify-between mb-1 gap-2">
              <div class="flex items-center gap-2">
                <span 
                  class="font-bold text-gray-800 leading-snug break-words"
                  :class="task.status === 'done' ? 'text-gray-400 line-through' : ''"
                >
                  {{ task.title }}
                </span>
                <!-- Problem Indicator -->
                <div v-if="task.problem_id" 
                     @click="convertToProblem(task)"
                     class="flex items-center gap-1 px-2 py-0.5 bg-amber-50 border border-amber-100/50 rounded-lg cursor-pointer hover:bg-amber-100 transition-colors shrink-0">
                  <span class="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse"></span>
                  <span class="text-[9px] font-black text-amber-600 uppercase tracking-tighter">已积淀</span>
                </div>
              </div>
             <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all">
               <button 
                 @click="convertToProblem(task)" 
                 class="p-1 transition-all rounded"
                 :class="task.problem_id ? 'text-amber-500 hover:bg-amber-100' : 'text-gray-300 hover:text-amber-500 hover:bg-amber-50'"
                 :title="task.problem_id ? '查看/编辑知识记录' : '转为问题 · 添加到知识沉淀'"
               >
                 <Beaker class="w-4 h-4" />
               </button>
               <button 
                 @click="openEditModal(task)" 
                 class="p-1 text-gray-300 hover:text-indigo-500 transition-all rounded hover:bg-indigo-50"
                 title="编辑任务"
               >
                 <Edit2 class="w-4 h-4" />
               </button>
               <button 
                 @click="deleteTask(task.id)" 
                 class="p-1 text-gray-300 hover:text-red-500 transition-all rounded hover:bg-red-50"
                 title="删除任务"
               >
                 <Trash2 class="w-4 h-4" />
               </button>
             </div>
          </div>
          
          <div class="flex flex-wrap items-center gap-2 mt-2">
            <!-- 核心分类：任务类型 -->
            <span class="text-[10px] font-bold px-2 py-0.5 rounded border uppercase" :class="taskTypeColors[task.task_type] || taskTypeColors.feature">{{ taskTypeLabels[task.task_type] || '🚀 新需求' }}</span>
          </div>

          <div v-if="task.deliverable" class="mt-3 flex items-start gap-1.5 text-xs font-semibold text-gray-500 bg-gray-50 p-2 rounded-lg border border-gray-100 w-fit">
            <Target class="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-px" />
            <span>Output: {{ task.deliverable }}</span>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <TaskModal 
        :show="isTaskModalOpen" 
        :editingTask="editingTask"
        :projects="projects"
        :plans="plans"
        @close="isTaskModalOpen = false" 
        @save="handleSaveTask"
      />
      
      <ProblemModal
        :show="isProblemModalOpen"
        :problemId="selectedProblemId"
        :initialData="initialProblemData"
        @close="isProblemModalOpen = false"
        @success="handleProblemModalSuccess"
      />
    </Teleport>
  </div>
</template>
