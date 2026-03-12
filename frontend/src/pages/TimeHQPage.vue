<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { focusApi } from '../api/focus'
import { projectApi } from '../api/project'
import { usePlanStore } from '../stores/plan'
import { storeToRefs } from 'pinia'
import FocusModal from '../components/business/focus/FocusModal.vue'
import { 
  ListTodo, CheckCircle2, Circle, Clock, Plus, Trash2, Rocket, LayoutGrid, LayoutList, Target, Edit2,
  GripVertical, MoreHorizontal, Calendar, AlertCircle, Eye, X
} from 'lucide-vue-next'
import draggable from 'vuedraggable'

const projects = ref([])
const activeProjects = computed(() => projects.value.filter(p => p.status !== 'graveyard'))
const planStore = usePlanStore()
const { plans } = storeToRefs(planStore)
const isLoading = ref(true)
const isModalOpen = ref(false)
const isDetailOpen = ref(false)
const editingRecord = ref(null)
const viewingRecord = ref(null)
const activeTab = ref('matrix') // 'matrix' | 'completed'
const allRecords = ref([])

// 使用单个 reactive 对象管理四个象限，这在 vuedraggable 中表现最稳定
const quadrantData = reactive({
  0: [], // Do First
  1: [], // Schedule
  2: [], // Delegate
  3: []  // Don't Do
})

const loadRecords = async () => {
  isLoading.value = true
  try {
    const [focusRes, projRes] = await Promise.all([
      focusApi.getRecords(),
      projectApi.getProjects(),
      planStore.fetchPlans()
    ])
    allRecords.value = focusRes
    
    // 初始化四个象限的数组（仅非完成状态）
    const activeRecords = focusRes.filter(r => r.status !== 'done')
    quadrantData[0] = activeRecords.filter(r => r.priority === 0)
    quadrantData[1] = activeRecords.filter(r => r.priority === 1)
    quadrantData[2] = activeRecords.filter(r => r.priority === 2)
    quadrantData[3] = activeRecords.filter(r => r.priority === 3)
    
    projects.value = projRes
  } catch (error) {
    console.error('Load records failed:', error)
  } finally {
    isLoading.value = false
  }
}

const completedRecords = computed(() => {
  return allRecords.value
    .filter(r => r.status === 'done')
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
})

const handleDragChange = async (event, targetPriority) => {
  // 当元素从另一个象限拖入当前象限时
  if (event.added) {
    const record = event.added.element
    try {
      await focusApi.updateRecord(record.id, { priority: targetPriority })
      // vuedraggable 已经完成了数据的内存迁移，我们只需要同步后端
    } catch (error) {
      console.error('Update priority via drag failed:', error)
      loadRecords() // 失败则重载以保持一致
    }
  }
}

const openNewModal = () => {
  editingRecord.value = null
  isModalOpen.value = true
}

const openEditModal = (record) => {
  editingRecord.value = { ...record }
  isModalOpen.value = true
}

const openDetail = (record) => {
  viewingRecord.value = record
  isDetailOpen.value = true
}

const handleSave = async (payload, recordId) => {
  try {
    if (recordId) {
      await focusApi.updateRecord(recordId, payload)
    } else {
      await focusApi.createRecord(payload)
    }
    isModalOpen.value = false
    loadRecords()
  } catch (error) {
    console.error('Save record failed:', error)
  }
}

const updateRecordStatus = async (record, newStatus) => {
  try {
    await focusApi.updateRecord(record.id, { status: newStatus })
    loadRecords() // 刷新以响应过滤逻辑
  } catch (error) {
    console.error('Update status failed:', error)
  }
}

const deleteRecord = async (id) => {
  if (!confirm('确定要删除这条关注记录吗？')) return
  try {
    await focusApi.deleteRecord(id)
    loadRecords()
  } catch (error) {
    console.error('Delete record failed:', error)
  }
}

const matrixQuadrants = computed(() => [
  {
    id: 0,
    name: 'Do First',
    desc: '重且急',
    color: 'border-red-200 bg-red-50/30',
    textColor: 'text-red-700',
    badgeColor: 'bg-red-100 text-red-700 border-red-200'
  },
  {
    id: 1,
    name: 'Schedule',
    desc: '重不急',
    color: 'border-blue-200 bg-blue-50/30',
    textColor: 'text-blue-700',
    badgeColor: 'bg-blue-100 text-blue-700 border-blue-200'
  },
  {
    id: 2,
    name: 'Delegate',
    desc: '急不重',
    color: 'border-amber-200 bg-amber-50/30',
    textColor: 'text-amber-700',
    badgeColor: 'bg-amber-100 text-amber-700 border-amber-200'
  },
  {
    id: 3,
    name: "Don't Do",
    desc: '不急不重',
    color: 'border-gray-200 bg-gray-50/30',
    textColor: 'text-gray-600',
    badgeColor: 'bg-gray-200 text-gray-700 border-gray-300'
  }
])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadRecords()
})
</script>

<template>
  <div class="animate-in max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
    <header class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-gray-800 tracking-tight flex items-center gap-3">
          <ListTodo class="text-indigo-500 w-8 h-8" />
          时间总线 (Time HQ)
        </h1>
        <p class="text-gray-500 mt-2 text-lg">支持长期计划、今日聚焦、项目备忘的通用时间管理枢纽。</p>
      </div>

      <div class="flex items-center gap-4">
        <!-- View Switcher -->
        <div class="bg-gray-100 p-1.5 rounded-2xl flex items-center gap-1 shadow-inner border border-black/5">
          <button 
            @click="activeTab = 'matrix'"
            :class="[
              'px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2',
              activeTab === 'matrix' ? 'bg-white shadow-md text-indigo-600' : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <LayoutGrid class="w-4 h-4" /> 四象限计划
          </button>
          <button 
            @click="activeTab = 'completed'"
            :class="[
              'px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2',
              activeTab === 'completed' ? 'bg-white shadow-md text-emerald-600' : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <CheckCircle2 class="w-4 h-4" /> 已完成记录
          </button>
        </div>

        <button @click="openNewModal" class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 shadow-md hover:shadow-lg inline-flex whitespace-nowrap">
          <Plus class="w-5 h-5 shrink-0" />新建事务
        </button>
      </div>
    </header>

    <div v-if="isLoading" class="flex-1 flex items-center justify-center text-gray-400">正在加载事务...</div>

    <!-- Focus Matrix View -->
    <div v-if="activeTab === 'matrix'" class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-y-auto pb-20 custom-scrollbar pr-2">
      <div v-for="quad in matrixQuadrants" :key="quad.id" 
        :class="['rounded-3xl border p-5 flex flex-col gap-4 transition-all duration-300 h-fit min-h-[300px]', quad.color]">
        
        <div class="flex items-center justify-between">
          <div>
            <h3 :class="['font-black text-xl flex items-center gap-2', quad.textColor]">
               {{ quad.name }}
            </h3>
            <p class="text-[10px] font-bold opacity-60 mt-0.5 uppercase tracking-[0.2em]">{{ quad.desc }}</p>
          </div>
          <span :class="['text-[10px] font-black px-2.5 py-1 rounded-full border shadow-sm', quad.badgeColor]">
            {{ quadrantData[quad.id].length }}
          </span>
        </div>

        <div class="flex-1 relative mt-2 flex flex-col">
          <!-- 空状态占位 (绝对定位以不影响布局且允许拖放容器覆盖此区域) -->
          <div v-if="quadrantData[quad.id].length === 0" class="absolute inset-0 flex flex-col items-center justify-center opacity-30 pointer-events-none">
            <LayoutGrid class="w-8 h-8 mb-2" />
            <span class="text-xs font-bold uppercase tracking-widest">象限空闲 (EMPTY)</span>
          </div>

          <draggable 
            v-model="quadrantData[quad.id]" 
            group="quadrants" 
            item-key="id"
            handle=".drag-handle"
            @change="(ev) => handleDragChange(ev, quad.id)"
            class="flex-1 grid grid-cols-1 xl:grid-cols-2 gap-4 min-h-[150px] content-start"
            ghost-class="opacity-50"
            drag-class="rotate-1"
          >
            <template #item="{ element: task }">
              <div 
                :class="[
                  'relative p-4 rounded-2xl shadow-sm border transition-all duration-300 group flex flex-col gap-2',
                  'bg-white border-black/5 hover:shadow-lg hover:border-indigo-200'
                ]"
              >
                <!-- Drag Handle Side Stripe -->
                <div class="drag-handle absolute left-0 top-0 bottom-0 w-1.5 bg-gray-100/50 group-hover:bg-indigo-400 transition-all cursor-grab active:cursor-grabbing"></div>

                <div class="flex-1 pl-1">
                  <!-- Top Row: Status, ID & Actions -->
                  <div class="flex items-center justify-between mb-1.5">
                    <div class="flex items-center gap-2">
                      <button 
                        @click.stop="updateRecordStatus(task, 'done')" 
                        class="w-4.5 h-4.5 rounded-full border-2 border-gray-200 hover:border-indigo-400 bg-white transition-all flex items-center justify-center"
                      >
                        <Circle class="w-2.5 h-2.5 text-transparent" />
                      </button>
                      <span class="text-[9px] font-black text-gray-400 uppercase tracking-tighter">HQ-{{ task.id }}</span>
                      <span v-if="task.is_today" class="px-1.5 py-0.5 rounded-md bg-red-50 text-[8px] font-black text-red-500 tracking-tighter border border-red-100 uppercase italic">Focus</span>
                    </div>
                    
                    <div class="flex items-center gap-1 relative group/menu">
                      <button 
                        @click.stop="openDetail(task)"
                        class="p-1 hover:bg-gray-100 rounded-lg text-gray-300 hover:text-indigo-500 transition-all flex items-center justify-center tooltip-trigger"
                        title="查看详情"
                      >
                        <Eye class="w-4 h-4" />
                      </button>
                      <button class="p-1 hover:bg-gray-100 rounded-lg text-gray-300 hover:text-gray-500 transition-all flex items-center justify-center">
                        <MoreHorizontal class="w-4 h-4" />
                      </button>
                      
                      <!-- Hover Bridge & Dropdown Menu -->
                      <div class="absolute right-0 top-full pt-1.5 hidden group-hover/menu:block z-20 -mr-2">
                        <div class="bg-white shadow-2xl border border-gray-100 rounded-xl py-1 min-w-[110px] animate-in fade-in slide-in-from-top-1">
                          <button @click.stop="openEditModal(task)" class="w-full px-3 py-2 text-[10px] font-black text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 flex items-center gap-2 text-left">
                            <Edit2 class="w-3 h-3" /> 编辑记录
                          </button>
                          <button @click.stop="deleteRecord(task.id)" class="w-full px-3 py-2 text-[10px] font-black text-red-500 hover:bg-red-50 flex items-center gap-2 text-left">
                            <Trash2 class="w-3 h-3" /> 永久删除
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Middle Row: Title -->
                  <h4 class="text-sm font-bold leading-snug transition-all line-clamp-2 text-gray-800">
                    {{ task.title }}
                  </h4>
                </div>

                <!-- Bottom Row: Type and Deadline -->
                <div class="mt-2 pt-2 border-t border-gray-50/50 flex items-center justify-between">
                  <div class="flex items-center gap-2 flex-wrap">
                    <div v-if="task.project_id" class="flex items-center gap-1.5 px-2 py-0.5 rounded bg-indigo-50/50 text-indigo-600">
                      <span class="text-[8px] font-black tracking-tighter uppercase whitespace-nowrap">📦 关联项目</span>
                    </div>
                    <div v-else-if="task.plan_id" class="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-50/50 text-amber-600">
                      <span class="text-[8px] font-black tracking-tighter uppercase whitespace-nowrap">🎯 关联计划</span>
                    </div>
                    <div v-else class="flex items-center gap-1.5 px-2 py-0.5 rounded bg-gray-50 text-gray-400">
                      <span class="text-[8px] font-black tracking-tighter uppercase whitespace-nowrap">☀️ 通用事务</span>
                    </div>

                    <div v-if="task.deadline" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50/50 text-blue-600">
                      <Calendar class="w-2.5 h-2.5" />
                      <span class="text-[8px] font-bold">
                        {{ formatDate(task.deadline).split(',')[0] }}
                      </span>
                    </div>
                  </div>

                  <AlertCircle v-if="task.priority === 0 && task.status !== 'done'" class="w-3.5 h-3.5 text-red-500 animate-pulse shrink-0" />
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>

    <!-- Completed Records View -->
    <div v-else-if="activeTab === 'completed'" class="flex-1 overflow-y-auto pb-20 custom-scrollbar pr-2">
      <div v-if="completedRecords.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
        <CheckCircle2 class="w-16 h-16 mb-4" />
        <p class="text-lg font-bold">暂无已完成记录</p>
        <p class="text-sm">完成事务后，它们会出现在这里。</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div 
          v-for="task in completedRecords" :key="task.id"
          class="relative p-4 rounded-2xl shadow-sm border bg-emerald-50/20 border-emerald-100 flex flex-col gap-2 opacity-80"
        >
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center gap-2">
                <button 
                  @click.stop="updateRecordStatus(task, 'todo')" 
                  class="w-4.5 h-4.5 rounded-full bg-emerald-500 text-white flex items-center justify-center transition-all hover:scale-110"
                >
                  <CheckCircle2 class="w-2.5 h-2.5" />
                </button>
                <span class="text-[9px] font-black text-gray-400 uppercase tracking-tighter">HQ-{{ task.id }}</span>
              </div>
              
              <div class="flex items-center gap-1 relative group/menu">
                <button 
                  @click.stop="openDetail(task)"
                  class="p-1 hover:bg-gray-100 rounded-lg text-gray-300 hover:text-indigo-500 transition-all flex items-center justify-center tooltip-trigger"
                  title="查看详情"
                >
                  <Eye class="w-4 h-4" />
                </button>
                <button class="p-1 hover:bg-gray-100 rounded-lg text-gray-300 hover:text-gray-500 transition-all">
                  <MoreHorizontal class="w-4 h-4" />
                </button>
                <div class="absolute right-0 top-full pt-1 hidden group-hover/menu:block z-20">
                  <div class="bg-white shadow-xl border border-gray-100 rounded-xl py-1 min-w-[100px]">
                    <button @click.stop="deleteRecord(task.id)" class="w-full px-3 py-1.5 text-[10px] font-black text-red-500 hover:bg-red-50 flex items-center gap-2 text-left">
                      <Trash2 class="w-3 h-3" /> 永久删除
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <h4 class="text-sm font-bold leading-snug text-gray-400 line-through line-clamp-2">
              {{ task.title }}
            </h4>
          </div>

          <div class="mt-2 pt-2 border-t border-emerald-50/50 flex items-center justify-between">
            <span class="text-[9px] font-bold text-emerald-600/60 uppercase italic">
              {{ formatDate(task.updated_at).split(',')[0] }} 完成
            </span>
            <div class="flex items-center gap-1 px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600">
               <span class="text-[8px] font-black uppercase tracking-tighter">{{ matrixQuadrants[task.priority]?.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Focus Modal -->
    <FocusModal 
      :show="isModalOpen" 
      :editingRecord="editingRecord"
      :projects="activeProjects"
      :plans="plans"
      @close="isModalOpen = false" 
      @save="handleSave"
    />

    <!-- Focus Detail Modal (Peek) -->
    <div v-if="isDetailOpen && viewingRecord" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm animate-in fade-in" @click="isDetailOpen = false"></div>
      
      <div class="bg-white rounded-3xl w-full max-w-xl shadow-2xl relative overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4 duration-300 border border-black/5">
        <!-- Decoration Header -->
        <div :class="['h-2 w-full', matrixQuadrants[viewingRecord.priority]?.color.split(' ')[0].replace('border-', 'bg-')]"></div>
        
        <div class="p-8">
          <div class="flex items-start justify-between mb-8">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="px-2 py-0.5 rounded-lg bg-gray-100 text-[10px] font-black text-gray-500 uppercase tracking-widest">HQ-{{ viewingRecord.id }}</span>
                <span v-if="viewingRecord.status === 'done'" class="px-2 py-0.5 rounded-lg bg-emerald-100 text-[10px] font-black text-emerald-600 uppercase">已完成</span>
                <span v-else :class="['px-2 py-0.5 rounded-lg text-[10px] font-black uppercase tracking-widest border', matrixQuadrants[viewingRecord.priority]?.badgeColor]">
                  {{ matrixQuadrants[viewingRecord.priority]?.name }}
                </span>
              </div>
              <h2 class="text-2xl font-black text-gray-800 tracking-tight leading-tight">{{ viewingRecord.title }}</h2>
            </div>
            <button @click="isDetailOpen = false" class="p-2 hover:bg-gray-100 rounded-xl text-gray-400 hover:text-gray-600 transition-all">
              <X class="w-6 h-6" />
            </button>
          </div>

          <div class="space-y-8">
            <!-- Metadata Row -->
            <div class="flex flex-wrap gap-4">
               <div v-if="viewingRecord.project_id" class="flex flex-col gap-1">
                 <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">关联项目</span>
                 <div class="px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-600 font-bold text-sm">📦 长期目标：具体项目</div>
               </div>
               <div v-if="viewingRecord.deadline" class="flex flex-col gap-1">
                 <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">计划节点</span>
                 <div class="px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 font-bold text-sm flex items-center gap-2">
                   <Calendar class="w-4 h-4" /> {{ formatDate(viewingRecord.deadline) }}
                 </div>
               </div>
            </div>

            <!-- Description Section -->
            <div class="bg-gray-50/50 rounded-2xl p-6 border border-black/5">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-4">详情说明 (Description)</span>
              <div v-if="viewingRecord.description" class="text-gray-600 leading-relaxed whitespace-pre-wrap text-sm">
                {{ viewingRecord.description }}
              </div>
              <div v-else class="text-gray-400 italic text-sm py-4 text-center">
                暂无详细描述...
              </div>
            </div>
          </div>

          <!-- Bottom Footer Tools -->
          <div class="mt-8 pt-6 border-t border-gray-100 flex items-center justify-between">
            <span class="text-[10px] font-bold text-gray-400">最后更新：{{ formatDate(viewingRecord.updated_at) }}</span>
            <div class="flex items-center gap-2">
              <button @click="isDetailOpen = false; openEditModal(viewingRecord)" class="px-5 py-2 rounded-xl bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition-all shadow-md">
                前往编辑
              </button>
              <button @click="isDetailOpen = false" class="px-5 py-2 rounded-xl bg-gray-100 text-gray-600 font-bold text-xs hover:bg-gray-200 transition-all">
                关闭查看
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 20px;
}
</style>
