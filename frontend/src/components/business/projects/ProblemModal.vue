<script setup>
import { ref, watch } from 'vue'
import { Plus, Edit, Hash, X, Bug, Zap, Layers, Rocket } from 'lucide-vue-next'
import { problemApi } from '../../../api/problem'

const props = defineProps({
  show: Boolean,
  problemId: Number, // If editing existing
  initialData: Object // For pre-filling (e.g. from task)
})

const emit = defineEmits(['close', 'success'])

const isEditMode = ref(false)
const problemForm = ref({ title: '', description: '', category: 'bug', tags: '', status: 'open', task_id: null })
const currentTag = ref('')
const tagList = ref([])
const isSaving = ref(false)

const categories = {
  bug: { label: 'Bug修复', icon: Bug },
  performance: { label: '性能瓶颈', icon: Zap },
  architecture: { label: '架构设计', icon: Layers },
  other: { label: '其他记录', icon: Rocket }
}

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}

const loadProblemData = async (id) => {
  try {
    const p = await problemApi.getProblem(id)
    problemForm.value = { ...p }
    tagList.value = formatTags(p.tags)
    isEditMode.value = true
  } catch (error) {
    console.error('Failed to load problem', error)
  }
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    if (props.problemId) {
      await loadProblemData(props.problemId)
    } else if (props.initialData) {
      problemForm.value = { 
        title: props.initialData.title || '', 
        description: props.initialData.description || '', 
        category: props.initialData.category || 'bug', 
        tags: props.initialData.tags || '',
        status: 'open',
        task_id: props.initialData.task_id || null
      }
      tagList.value = formatTags(props.initialData.tags)
      isEditMode.value = false
    } else {
      // Default reset
      problemForm.value = { title: '', description: '', category: 'bug', tags: '', status: 'open', task_id: null }
      tagList.value = []
      isEditMode.value = false
    }
  }
})

const addTag = () => {
  const tag = currentTag.value.trim()
  if (tag && !tagList.value.includes(tag)) {
    tagList.value.push(tag)
  }
  currentTag.value = ''
}

const removeTag = (index) => {
  tagList.value.splice(index, 1)
}

const handleTagKeydown = (e) => {
  if (e.key === ',' || e.key === '，' || e.key === 'Enter') {
    e.preventDefault()
    addTag()
  }
}

const saveProblem = async () => {
  if (!problemForm.value.title.trim()) return
  isSaving.value = true
  try {
    problemForm.value.tags = tagList.value.join(', ')
    
    if (isEditMode.value) {
      await problemApi.updateProblem(props.problemId, problemForm.value)
    } else {
      await problemApi.createProblem(problemForm.value)
    }
    
    emit('success')
    emit('close')
  } catch (error) {
    console.error('Failed to save problem', error)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm animate-in fade-in" @click="emit('close')"></div>
    <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-xl relative z-10 animate-in zoom-in duration-300 overflow-hidden">
      <!-- Header -->
      <div class="px-8 py-6 border-b border-gray-50 flex items-center justify-between bg-white sticky top-0 z-10">
        <div class="flex items-center gap-3">
          <span class="text-indigo-600 font-mono text-xl font-bold">&gt;_</span>
          <h3 class="text-xl font-black text-gray-800 tracking-tight">{{ isEditMode ? '完善案发现场' : '保护案发现场' }}</h3>
        </div>
        <button @click="emit('close')" class="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400">
           <X class="w-5 h-5" />
        </button>
      </div>

      <div class="p-8 space-y-8 custom-scrollbar max-h-[85vh] overflow-y-auto">
        <!-- Title -->
        <div class="space-y-3">
          <label class="text-sm font-black text-gray-700 flex items-center gap-1">
            一句话描述问题 <span class="text-red-500">*</span>
          </label>
          <input v-model="problemForm.title" autoFocus type="text" placeholder="例如：移除反思日记导航栏导致白屏..." 
                 class="w-full bg-gray-50/50 border border-gray-100 focus:border-indigo-500/20 focus:bg-white focus:ring-4 focus:ring-indigo-500/5 rounded-xl px-5 py-4 outline-none transition-all font-bold text-gray-800 placeholder:text-gray-300">
        </div>

        <!-- Category (Segmented Style) -->
        <div class="space-y-3">
           <label class="text-sm font-black text-gray-700">问题分类</label>
           <div class="grid grid-cols-2 md:grid-cols-4 gap-2 p-1 bg-gray-50/50 rounded-xl border border-gray-100">
              <button v-for="(info, key) in categories" :key="key"
                      @click="problemForm.category = key"
                      class="px-3 py-3 rounded-lg text-[11px] font-black transition-all text-center"
                      :class="problemForm.category === key 
                        ? 'bg-white shadow-sm text-indigo-600 ring-1 ring-indigo-500/10' 
                        : 'text-gray-400 hover:text-gray-600'">
                {{ info.label }}
              </button>
           </div>
        </div>

        <!-- Context -->
        <div class="space-y-3">
          <label class="text-sm font-black text-gray-700">原始上下文 (报错日志 / 现象)</label>
          <textarea v-model="problemForm.description" rows="5" placeholder="粘贴 Error Log，或简述表现。后续 AI 会帮你一起排查..."
                    class="w-full bg-gray-50/50 border border-gray-100 focus:border-indigo-500/20 focus:bg-white focus:ring-4 focus:ring-indigo-500/5 rounded-xl px-5 py-4 outline-none transition-all font-medium text-gray-600 placeholder:text-gray-300 leading-relaxed"></textarea>
        </div>

        <!-- Tags -->
        <div class="space-y-3">
          <label class="text-sm font-bold text-gray-400">标签 (可选)</label>
          <div class="flex flex-wrap gap-2 p-3 bg-gray-50/50 border border-gray-100 rounded-xl focus-within:border-indigo-500/20 focus-within:bg-white focus-within:ring-4 focus-within:ring-indigo-500/5 transition-all min-h-[56px]">
            <span v-for="(tag, index) in tagList" :key="index" 
                  class="flex items-center gap-1.5 px-3 py-1 bg-white border border-indigo-100 text-indigo-600 text-[11px] font-black rounded-lg">
              # {{ tag }}
              <button @click="removeTag(index)" class="hover:text-red-500 p-0.5">
                <X class="w-3 h-3" />
              </button>
            </span>
            <input v-model="currentTag" type="text" placeholder="输入标签按回车..." 
                   @keydown="handleTagKeydown"
                   @blur="addTag"
                   class="flex-1 bg-transparent border-none outline-none py-1 font-bold text-gray-800 placeholder:text-gray-300 text-[13px] min-w-[120px]">
          </div>
          <p class="text-[10px] text-gray-300 ml-2 italic">提示：输入标签后按下回车或逗号即可添加</p>
        </div>
      </div>
      
      <!-- Footer Actions -->
      <div class="p-8 bg-gray-50/30 border-t border-gray-50 flex items-center justify-end gap-6">
        <button @click="emit('close')" class="text-sm font-bold text-gray-400 hover:text-gray-600 transition-colors" :disabled="isSaving">取消</button>
        <button @click="saveProblem" :disabled="!problemForm.title.trim() || isSaving" 
                class="bg-[#1a202c] hover:bg-black text-white px-8 py-4 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-xl disabled:opacity-50 transform active:scale-95 flex items-center gap-2">
          <span v-if="isSaving" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ isEditMode ? '更新记录' : '保存并稍后整理' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }

.animate-in {
  animation: slideTop 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideTop {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
