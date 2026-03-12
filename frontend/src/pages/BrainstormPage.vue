<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useBrainstormStore } from '../stores/brainstorm'
import { useProjectStore } from '../stores/project'
import { brainstormApi } from '../api/brainstorm'
import { projectApi } from '../api/project'
import { incubationApi } from '../api/incubation'
import { Lightbulb, Tag, Archive, CornerDownRight, Check, X, Send, Inbox, RefreshCcw, FolderKanban, Calendar, Beaker } from 'lucide-vue-next'

const brainstormStore = useBrainstormStore()
const projectStore = useProjectStore()

const { brainstorms, stats, isLoading, currentTab } = storeToRefs(brainstormStore)
const { projects } = storeToRefs(projectStore)

const newIdea = ref('')
const newTags = ref('')

const submitIdea = async () => {
    if (!newIdea.value.trim()) return
    await brainstormStore.createIdea(newIdea.value.trim(), newTags.value.trim() || null)
    newIdea.value = ''
    newTags.value = ''
}

const archiveIdea = (id) => brainstormStore.updateStatus(id, 'archived')
const unarchiveIdea = (id) => brainstormStore.updateStatus(id, 'inbox')

// Conversion Logic
const showTaskModal = ref(false)
const taskTitle = ref('')
const convertingId = ref(null)
const selectedProjectId = ref(null)
const addToToday = ref(true)
const conversionType = ref('project') // 'project' or 'incubation'

const openConversionModal = (brainstorm, type = 'project') => {
    const firstLine = brainstorm.content.split('\n')[0]
    taskTitle.value = firstLine.substring(0, 50)
    convertingId.value = brainstorm.id
    conversionType.value = type
    selectedProjectId.value = null
    showTaskModal.value = true
}

const handleConversion = async () => {
    if (!taskTitle.value.trim() || !convertingId.value) return
    
    try {
        if (conversionType.value === 'project') {
            // Convert to Project
            await projectApi.createProject({
                name: taskTitle.value.trim(),
                description: brainstorms.value.find(b => b.id === convertingId.value)?.content || '',
                status: 'preparation',
                source: 'direct'
            })
            await projectStore.fetchProjects()
        } else if (conversionType.value === 'incubation') {
            // Convert to Incubation
            await incubationApi.createIncubation({
                title: taskTitle.value.trim(),
                brainstorm_id: convertingId.value,
                one_page_doc: brainstorms.value.find(b => b.id === convertingId.value)?.content || '',
                mvp_status: 'planning',
                result: 'experiment'
            })
        }
        
        await brainstormStore.updateStatus(convertingId.value, 'converted')
        showTaskModal.value = false
        taskTitle.value = ''
        convertingId.value = null
    } catch (error) {
        console.error('Failed to convert', error)
    }
}

// Tag Editing
const updatingTagId = ref(null)
const tempTagValue = ref('')

const startEditTag = (b) => {
    updatingTagId.value = b.id
    tempTagValue.value = b.tags || ''
}

const saveTag = async (id) => {
    await brainstormStore.updateTags(id, tempTagValue.value)
    updatingTagId.value = null
}

onMounted(() => {
    brainstormStore.fetchBrainstorms()
    projectStore.fetchProjects()
})
</script>

<template>
  <div class="animate-in max-w-4xl mx-auto">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 tracking-tight flex items-center gap-3">
        <Lightbulb class="text-yellow-500 w-8 h-8" />
        灵感收件箱
      </h1>
      <p class="text-gray-500 mt-2 text-lg">清空大脑，随时记录你的神来之笔。</p>
    </header>

    <div class="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 mb-10 transition-shadow focus-within:shadow-md focus-within:border-primary/30">
      <textarea 
        v-model="newIdea"
        @keydown.ctrl.enter="submitIdea"
        class="w-full bg-transparent border-0 focus:ring-0 p-0 text-gray-800 text-lg placeholder-gray-300 resize-none outline-none"
        rows="4"
        placeholder="想到了什么？使用 Markdown 记录下来... (Ctrl+Enter 快捷提交)"
      ></textarea>
      
      <div class="mt-4 pt-4 border-t border-gray-50 flex items-center justify-between">
        <div class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 flex-1 max-w-xs">
          <Tag class="w-4 h-4 text-gray-400" />
          <input 
            v-model="newTags"
            type="text" 
            placeholder="标签 (以逗号分隔)" 
            class="bg-transparent border-0 focus:ring-0 p-0 text-sm outline-none text-gray-600 w-full"
            @keydown.enter="submitIdea"
          >
        </div>
        
        <button 
          @click="submitIdea"
          :disabled="!newIdea.trim()"
          class="flex items-center gap-2 px-6 py-2.5 bg-primary text-white font-semibold rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-primary/20"
        >
          <Send class="w-4 h-4" />记录想法
        </button>
      </div>
    </div>

    <div class="flex items-center gap-4 mb-6 border-b border-gray-100 pb-4">
      <button @click="brainstormStore.switchTab('inbox')" class="flex items-center gap-2 px-4 py-2 rounded-xl font-bold transition-colors" :class="currentTab === 'inbox' ? 'bg-primary/10 text-primary' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'">
        <Inbox class="w-5 h-5" />收件箱未处理
        <span class="text-xs px-2 py-0.5 rounded-full ml-1 transition-colors" :class="currentTab === 'inbox' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500'">{{ stats.inbox }}</span>
      </button>
      <button @click="brainstormStore.switchTab('archived')" class="flex items-center gap-2 px-4 py-2 rounded-xl font-bold transition-colors" :class="currentTab === 'archived' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'">
        <Archive class="w-5 h-5" />已归档冷冻
        <span class="text-xs px-2 py-0.5 rounded-full ml-1 transition-colors" :class="currentTab === 'archived' ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'">{{ stats.archived }}</span>
      </button>
      <button @click="brainstormStore.switchTab('converted')" class="flex items-center gap-2 px-4 py-2 rounded-xl font-bold transition-colors" :class="currentTab === 'converted' ? 'bg-green-50 text-green-600' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'">
        <Check class="w-5 h-5" />已转化为项目/孵化
        <span class="text-xs px-2 py-0.5 rounded-full ml-1 transition-colors" :class="currentTab === 'converted' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-500'">{{ stats.converted }}</span>
      </button>
    </div>

    <div class="space-y-4 pb-12">
      <div v-if="isLoading" class="text-center py-10 text-gray-400">正在加载灵感...</div>
      <div v-else-if="brainstorms.length === 0" class="text-center py-16 bg-white rounded-3xl border border-dashed border-gray-200">
          <Lightbulb v-if="currentTab === 'inbox'" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p class="text-gray-500 font-medium">还没有内容...</p>
      </div>

      <div v-for="item in brainstorms" :key="item.id" class="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden">
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-yellow-300 to-primary/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="whitespace-pre-wrap text-gray-700 font-medium leading-relaxed mb-6">{{ item.content }}</div>
        
        <div class="flex flex-wrap items-center justify-between gap-4 mt-auto pt-4 border-t border-gray-50">
          <div class="flex items-center">
            <div v-if="updatingTagId === item.id" class="flex items-center gap-2">
              <input v-model="tempTagValue" @keyup.enter="saveTag(item.id)" class="bg-gray-50 border border-gray-200 rounded-md px-2 py-1 text-xs outline-none focus:border-primary" placeholder="输入标签" autoFocus>
              <button @click="saveTag(item.id)" class="text-green-500 hover:bg-green-50 p-1 rounded"><Check class="w-4 h-4" /></button>
            </div>
            <div v-else @click="startEditTag(item)" class="cursor-pointer group/tag flex items-center">
              <span v-if="item.tags" class="inline-flex items-center gap-1.5 px-3 py-1 bg-yellow-50 text-yellow-700 text-xs font-semibold rounded-full border border-yellow-100 transition-colors group-hover/tag:bg-yellow-100">
                <Tag class="w-3 h-3" />{{ item.tags }}
              </span>
              <span v-else class="inline-flex items-center gap-1 text-gray-400 text-xs hover:text-gray-600 transition-colors"><Tag class="w-3 h-3" /> 添加标签</span>
            </div>
          </div>

          <div class="flex gap-2" v-if="currentTab === 'inbox'">
            <button @click="openConversionModal(item, 'incubation')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-amber-600 bg-amber-50 rounded-lg hover:bg-amber-100 transition-colors">
              <Beaker class="w-4 h-4" />推入孵化
            </button>
            <button @click="openConversionModal(item, 'project')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <FolderKanban class="w-4 h-4" />转为项目
            </button>
            <button @click="archiveIdea(item.id)" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-500 bg-gray-50 rounded-lg hover:text-gray-700 hover:bg-gray-100 transition-colors"><Archive class="w-4 h-4" />归档</button>
          </div>
          <div class="flex gap-2" v-else>
            <button @click="unarchiveIdea(item.id)" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-yellow-600 bg-yellow-50 rounded-lg hover:text-yellow-700 hover:bg-yellow-100 transition-colors border border-yellow-200/50"><RefreshCcw class="w-4 h-4" />恢复</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Conversion Modal -->
    <div v-if="showTaskModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-gray-900/30 backdrop-blur-sm" @click="showTaskModal = false"></div>
      <div class="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-md relative z-10 animate-in">
        <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <FolderKanban v-if="conversionType === 'project'" class="w-5 h-5 text-blue-500" />
            <Beaker v-else class="w-5 h-5 text-amber-500" />
            {{ conversionType === 'project' ? '灵感直接转为新项目' : '灵感推入孵化实验室' }}
        </h3>
        
        <div class="space-y-4 mb-8">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">{{ conversionType === 'project' ? '项目名称' : '实验名称' }}</label>
            <input v-model="taskTitle" type="text" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800" autoFocus>
          </div>
        </div>
        
        <div class="flex gap-4">
          <button @click="showTaskModal = false" class="flex-1 py-3 text-gray-600 font-semibold bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors">取消</button>
          <button @click="handleConversion" :disabled="!taskTitle.trim()" class="flex-1 py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50">确认转化</button>
        </div>
      </div>
    </div>
  </div>
</template>
