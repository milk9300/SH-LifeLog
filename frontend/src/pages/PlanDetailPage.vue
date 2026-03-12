<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlan, getMilestones, addMilestone, updateMilestone, deleteMilestone } from '../api/plan'
import { articleApi } from '../api/article'
import { ArrowLeft, Target, Calendar, Plus, CheckCircle2, Circle, Edit2, Trash2, BookOpen, Save, AlignLeft } from 'lucide-vue-next'
import { MdEditor, MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import 'md-editor-v3/lib/preview.css'

const route = useRoute()
const router = useRouter()
const planId = parseInt(route.params.id)

const plan = ref(null)
const milestones = ref([])
const reflections = ref([])
const isLoading = ref(true)

// Milestone editing
const newMilestoneTitle = ref('')
const editingMilestoneId = ref(null)
const editingMilestoneTitle = ref('')

// Reflection editing
const isEditingReflection = ref(false)
const activeReflection = ref(null)
const editorTitle = ref('')
const editorContent = ref('')
const editorMilestoneId = ref('')

const loadData = async () => {
    isLoading.value = true
    try {
        const [planRes, milRes, refRes] = await Promise.all([
            getPlan(planId),
            getMilestones(planId),
            articleApi.getArticles({ plan_id: planId })
        ])
        plan.value = planRes
        milestones.value = milRes
        reflections.value = Array.isArray(refRes.data) ? refRes.data : (Array.isArray(refRes) ? refRes : [])
    } catch (err) {
        console.error('Failed to load plan details:', err)
    } finally {
        isLoading.value = false
    }
}

// --- Milestones ---
const handleAddMilestone = async () => {
    if (!newMilestoneTitle.value.trim()) return
    try {
        await addMilestone({
            plan_id: planId,
            title: newMilestoneTitle.value.trim(),
            status: 'todo',
            order_index: milestones.value.length
        })
        newMilestoneTitle.value = ''
        await loadData()
    } catch (err) {
        console.error('Failed to add milestone:', err)
    }
}

const toggleMilestoneStatus = async (milestone) => {
    const cycle = ['todo', 'doing', 'done']
    const idx = cycle.indexOf(milestone.status)
    const nextStatus = cycle[(idx + 1) % cycle.length]
    try {
        await updateMilestone(milestone.id, { status: nextStatus })
        await loadData()
    } catch (err) {
        console.error('Failed to switch milestone status:', err)
    }
}

const startEditMilestone = (milestone) => {
    editingMilestoneId.value = milestone.id
    editingMilestoneTitle.value = milestone.title
}

const saveMilestoneEdit = async () => {
    if (!editingMilestoneTitle.value.trim() || !editingMilestoneId.value) return
    try {
        await updateMilestone(editingMilestoneId.value, { title: editingMilestoneTitle.value.trim() })
        editingMilestoneId.value = null
        editingMilestoneTitle.value = ''
        await loadData()
    } catch (err) {
        console.error('Failed to update milestone:', err)
    }
}

const removeMilestone = async (id) => {
    if (!confirm('确定删除该里程碑吗？')) return
    try {
        await deleteMilestone(id)
        await loadData()
    } catch (err) {
        console.error('Failed to delete milestone:', err)
    }
}

// --- Reflections (Articles) ---
const startNewReflection = () => {
    activeReflection.value = { isNew: true }
    editorTitle.value = ''
    editorContent.value = ''
    editorMilestoneId.value = ''
    isEditingReflection.value = true
}

const openReflection = (reflec) => {
    activeReflection.value = reflec
    editorTitle.value = reflec.title || ''
    editorContent.value = reflec.content || ''
    editorMilestoneId.value = reflec.milestone_id || ''
    isEditingReflection.value = false
}

const editReflection = () => {
    if (!activeReflection.value || activeReflection.value.isNew) return
    isEditingReflection.value = true
}

const saveReflection = async () => {
    if (!editorContent.value) {
        alert('内容不能为空')
        return
    }

    const payload = {
        title: editorTitle.value.trim() || '学习记录',
        content: editorContent.value,
        plan_id: planId,
        milestone_id: editorMilestoneId.value ? parseInt(editorMilestoneId.value) : null,
        category: '长线计划'
    }

    try {
        if (activeReflection.value.isNew) {
            const res = await articleApi.createArticle(payload)
            activeReflection.value = res.data || res
        } else {
            const res = await articleApi.updateArticle(activeReflection.value.id, payload)
            activeReflection.value = res.data || res
        }
        isEditingReflection.value = false
        await loadData()
    } catch (err) {
        console.error('Failed to save reflection:', err)
    }
}

const removeReflection = async (id) => {
    if (!confirm('确定删除该文章记录吗？')) return
    try {
        await articleApi.deleteArticle(id)
        if (activeReflection.value && activeReflection.value.id === id) {
            activeReflection.value = null
        }
        await loadData()
    } catch (err) {
        console.error('Failed to delete reflection:', err)
    }
}

const getMilestoneName = (id) => {
    if (!id) return ''
    const m = milestones.value.find(x => x.id === id)
    return m ? m.title : ''
}

const formatDate = (dateStr) => {
    if(!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
    loadData()
})

const planProgress = computed(() => {
    if (milestones.value.length === 0) return 0
    const done = milestones.value.filter(m => m.status === 'done').length
    return Math.round((done / milestones.value.length) * 100)
})
</script>

<template>
  <div class="h-[calc(100vh-8rem)] flex flex-col pt-2 animate-in">
    <!-- Top Nav -->
    <div class="flex items-center gap-4 mb-6">
      <button 
        @click="router.push('/plans')"
        class="p-2.5 bg-white border border-gray-200 rounded-xl text-gray-500 hover:text-indigo-600 hover:border-indigo-200 transition-all shadow-sm"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>
      <div v-if="plan" class="flex flex-col">
        <h1 class="text-2xl font-black text-gray-800">{{ plan.title }}</h1>
        <div class="flex items-center gap-3 text-xs font-semibold text-gray-400 mt-1">
          <span class="flex items-center gap-1"><Calendar class="w-3.5 h-3.5" /> {{ plan.start_date || '未定' }} - {{ plan.target_date || '未定' }}</span>
          <span class="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded">进度 {{ planProgress }}%</span>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
      
      <!-- Left: Milestones Timeline -->
      <div class="w-full lg:w-[380px] flex flex-col bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden shrink-0 h-full">
        <div class="p-6 border-b border-gray-50 bg-gray-50/50">
          <h2 class="text-lg font-bold text-gray-800 mb-2">里程碑 (Milestones)</h2>
          <p class="text-xs text-gray-500">拆解你的长线目标，逐个击破</p>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <div v-if="milestones.length === 0" class="text-center py-10 text-gray-400 text-sm">
            还没有添加任何里程碑。
          </div>

          <div class="relative pl-6 border-l-2 border-indigo-100 space-y-8">
            <div 
              v-for="(milestone, index) in milestones" 
              :key="milestone.id"
              class="relative"
            >
              <!-- Timeline Dot -->
              <div 
                class="absolute -left-[31px] w-4 h-4 rounded-full border-4 border-white shadow-sm flex items-center justify-center cursor-pointer transition-colors"
                :class="milestone.status === 'done' ? 'bg-indigo-500' : (milestone.status === 'doing' ? 'bg-amber-400' : 'bg-gray-200')"
                @click="toggleMilestoneStatus(milestone)"
                title="点击切换状态"
              ></div>
              
              <div class="group bg-white border border-gray-100 rounded-2xl p-4 shadow-sm hover:border-indigo-200 transition-all">
                <div v-if="editingMilestoneId === milestone.id" class="flex gap-2">
                    <input 
                        v-model="editingMilestoneTitle"
                        type="text" 
                        class="flex-1 bg-gray-50 border border-indigo-200 rounded-lg px-3 py-1.5 text-sm outline-none font-medium"
                        @keyup.enter="saveMilestoneEdit"
                        autoFocus
                    >
                    <button @click="saveMilestoneEdit" class="text-indigo-600 bg-indigo-50 px-3 rounded-lg text-sm font-bold">保存</button>
                    <button @click="editingMilestoneId = null" class="text-gray-400 hover:text-gray-600 text-sm px-1">取消</button>
                </div>
                <div v-else class="flex justify-between items-start">
                  <div>
                    <h4 
                        class="font-bold text-gray-800"
                        :class="milestone.status === 'done' ? 'line-through text-gray-400' : ''"
                    >
                        {{ milestone.title }}
                    </h4>
                    <span 
                        class="text-[10px] font-bold px-2 py-0.5 rounded uppercase mt-1 inline-block"
                        :class="milestone.status === 'done' ? 'bg-indigo-50 text-indigo-600' : (milestone.status === 'doing' ? 'bg-amber-50 text-amber-600' : 'bg-gray-100 text-gray-500')"
                    >
                        {{ milestone.status === 'done' ? '已完成' : (milestone.status === 'doing' ? '进行中' : '未开始') }}
                    </span>
                  </div>
                  <div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                      <button @click="startEditMilestone(milestone)" class="p-1 text-gray-400 hover:text-indigo-600 rounded">
                          <Edit2 class="w-3.5 h-3.5" />
                      </button>
                      <button @click="removeMilestone(milestone.id)" class="p-1 text-gray-400 hover:text-red-500 rounded">
                          <Trash2 class="w-3.5 h-3.5" />
                      </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Add Milestone Input -->
          <div class="mt-8 pt-6 border-t border-gray-100 border-dashed">
             <div class="flex items-center gap-2 bg-gray-50 rounded-xl px-3 py-2 border border-gray-200 focus-within:border-indigo-300 focus-within:bg-white transition-all">
                 <input 
                    v-model="newMilestoneTitle"
                    @keyup.enter="handleAddMilestone"
                    type="text" 
                    placeholder="添加新里程碑 (Enter 确认)"
                    class="bg-transparent border-none outline-none text-sm font-medium w-full"
                 >
                 <button @click="handleAddMilestone" class="p-1 text-gray-400 hover:text-indigo-600"><Plus class="w-4 h-4" /></button>
             </div>
          </div>
        </div>
      </div>

      <!-- Right: Content Links & Editor -->
      <div class="flex-1 flex flex-col bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden h-full relative">
        <template v-if="!activeReflection">
            <!-- Article List View -->
            <div class="p-6 border-b border-gray-50 flex items-center justify-between">
                <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <BookOpen class="w-5 h-5 text-indigo-600" />
                    学习记录
                </h2>
                <button 
                    @click="startNewReflection"
                    class="px-4 py-2 bg-indigo-600 text-white font-bold text-sm rounded-xl hover:bg-indigo-700 transition-all shadow-sm flex items-center gap-2"
                >
                    <Plus class="w-4 h-4" />
                    新增记录
                </button>
            </div>
            
            <div class="flex-1 overflow-y-auto p-6">
                <div v-if="reflections.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
                    <AlignLeft class="w-12 h-12 text-gray-200 mb-4" />
                    <p class="text-sm">暂时没有相关的学习记录，快去沉淀第一篇文章吧！</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div 
                        v-for="reflec in reflections" 
                        :key="reflec.id"
                        @click="openReflection(reflec)"
                        class="group cursor-pointer bg-white border border-gray-100 rounded-2xl p-5 hover:border-indigo-200 hover:shadow-md transition-all"
                    >
                        <h3 class="font-bold text-gray-800 text-lg mb-2 line-clamp-1 group-hover:text-indigo-600 transition-colors">{{ reflec.title || '无标题记录' }}</h3>
                        <p class="text-xs text-gray-500 flex items-center gap-3">
                            <span>{{ formatDate(reflec.created_at) }}</span>
                            <span v-if="reflec.milestone_id" class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded bg-indigo-50/50">
                                关联: {{ getMilestoneName(reflec.milestone_id) }}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </template>
        
        <template v-else>
            <!-- Editor / Reader View -->
            <div class="p-6 border-b border-gray-100 flex items-center justify-between bg-white shrink-0 shadow-sm z-10">
                <div v-if="isEditingReflection" class="flex-1 flex flex-col gap-3 mr-4">
                    <input 
                        v-model="editorTitle"
                        type="text"
                        placeholder="记录标题..."
                        class="text-xl font-black text-gray-800 bg-transparent border-none outline-none w-full p-0"
                    />
                    <select v-model="editorMilestoneId" class="text-sm py-1.5 px-3 border border-gray-200 rounded-lg focus:ring-indigo-300 text-gray-600 w-fit outline-none">
                        <option value="">关联指定里程碑 (可选)</option>
                        <option v-for="m in milestones" :key="m.id" :value="m.id">{{ m.title }}</option>
                    </select>
                </div>
                <div v-else class="flex-1 mr-4">
                    <h1 class="text-2xl font-black text-gray-800">{{ activeReflection.title || '无标题记录' }}</h1>
                    <span v-if="activeReflection.milestone_id" class="inline-block mt-2 px-2.5 py-1 bg-indigo-50 text-indigo-600 rounded-md text-xs font-medium border border-indigo-100">
                        {{ getMilestoneName(activeReflection.milestone_id) }}
                    </span>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                    <button 
                        @click="activeReflection = null" 
                        class="px-4 py-2 text-gray-400 hover:bg-gray-100 rounded-xl transition-all"
                    >
                        返回列表
                    </button>
                    
                    <template v-if="isEditingReflection">
                        <button 
                            @click="saveReflection"
                            class="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors flex items-center gap-2 font-bold shadow-sm"
                        >
                            <Save class="w-4 h-4" /> 保存
                        </button>
                    </template>
                    <template v-else>
                        <button 
                            @click="editReflection"
                            class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-colors"
                            title="编辑"
                        >
                            <Edit2 class="w-5 h-5" />
                        </button>
                        <button 
                            @click="removeReflection(activeReflection.id)"
                            class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                            title="删除"
                        >
                            <Trash2 class="w-5 h-5" />
                        </button>
                    </template>
                </div>
            </div>

            <!-- Markdown Section -->
            <div v-if="isEditingReflection" class="flex-1 min-h-0 bg-gray-50/30 w-full h-full relative p-0 overflow-hidden">
                <MdEditor 
                    v-model="editorContent" 
                    style="height: 100%; border-radius: 0; outline: none;" 
                    :toolbarsExclude="['github', 'pageFullscreen', 'fullscreen', 'htmlPreview', 'catalog']"
                    placeholder="在此记录你的学习历程 (Markdown)..."
                />
            </div>
            <div v-else class="flex-1 overflow-y-auto p-8 bg-gray-50/30">
                <div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100 min-h-full">
                    <MdPreview :editorId="'preview-only'" :modelValue="activeReflection.content" />
                </div>
            </div>
        </template>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
:deep(.md-editor) {
    --md-color: #374151;
    --md-bk-color: transparent;
}
:deep(.md-editor-preview) {
    font-size: 1.05rem;
    line-height: 1.8;
}
</style>
