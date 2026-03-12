<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { debounce } from 'lodash-es'
import { useRoute, useRouter } from 'vue-router'
import { articleApi } from '../api/article'
import { projectApi } from '../api/project'
import { 
  ArrowLeft, 
  Save, 
  Tag, 
  Hash, 
  BookOpen, 
  FileText, 
  Settings2, 
  X, 
  Check,
  ChevronDown,
  Eye,
  Expand,
  Minimize2
} from 'lucide-vue-next'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const route = useRoute()
const router = useRouter()
const isEdit = ref(!!route.params.id)
const isLoading = ref(false)
const isSaving = ref(false)
const showSettings = ref(false)
const isFullscreen = ref(false)
const isFocusMode = ref(false)
const lastSavedTime = ref(null)
const saveStatus = ref('synced') // 'synced', 'modified', 'saving', 'error'

const title = ref('')
const content = ref('')
const status = ref('draft')
const category = ref('technical')
const tags = ref('')
const projectId = ref('')
const projects = ref([])

const currentTag = ref('')
const tagList = ref([])

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}


const categories = [
  { id: 'technical', name: '技术文章', icon: Hash, desc: '深度技术沉淀与经验分享' },
  { id: 'reflection', name: '反思日记', icon: FileText, desc: '每日成长心路与自我复盘' },
  { id: 'other', name: '其他文章', icon: BookOpen, desc: '随笔、计划或其他杂项' }
]

const statuses = [
  { id: 'draft', name: '草稿', icon: FileText, desc: '仅自己可见，适合记录灵感' },
  { id: 'published', name: '已发布', icon: Check, desc: '正式定稿，进入知识库' }
]

const activeCategory = computed(() => categories.find(c => c.id === category.value))

const loadProjects = async () => {
    try {
        const res = await projectApi.getProjects()
        projects.value = res.data || res
    } catch (err) {
        console.error('Failed to load projects:', err)
    }
}

const loadArticle = async () => {
  if (!isEdit.value) return
  isLoading.value = true
  try {
    const res = await articleApi.getArticle(route.params.id)
    const data = res.data || res
    title.value = data.title || ''
    content.value = data.content || ''
    category.value = data.category || 'technical'
    status.value = data.status || 'draft'
    tags.value = data.tags || ''
    tagList.value = formatTags(data.tags)
    projectId.value = data.project_id || ''
  } catch (err) {
    console.error('Failed to load article:', err)
  } finally {
    isLoading.value = false
  }
}

const handleSave = async (isSilent = false) => {
  if (!content.value) return
  isSaving.value = true
  saveStatus.value = 'saving'
  
  const payload = {
    title: title.value.trim() || (category.value === 'reflection' ? '未命名感悟' : '无标题文章'),
    content: content.value,
    category: category.value,
    status: status.value,
    tags: tags.value.trim(),
    project_id: projectId.value ? parseInt(projectId.value) : null
  }

  try {
    if (isEdit.value) {
      await articleApi.updateArticle(route.params.id, payload)
    } else {
      const res = await articleApi.createArticle(payload)
      const newId = res.id || (res.data && res.data.id)
      if (newId) {
        isEdit.value = true
        router.replace(`/articles/${newId}/edit`)
      }
    }
    
    lastSavedTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    saveStatus.value = 'synced'

    if (!isSilent) {
      router.back()
    }
  } catch (err) {
    console.error('Failed to save article:', err)
    saveStatus.value = 'error'
    if (!isSilent) {
      alert('保存失败，请检查网络')
    }
  } finally {
    isSaving.value = false
  }
}

const addTag = () => {
  const tag = currentTag.value.trim()
  if (tag && !tagList.value.includes(tag)) {
    tagList.value.push(tag)
    updateTags()
  }
  currentTag.value = ''
}

const removeTag = (index) => {
  tagList.value.splice(index, 1)
  updateTags()
}

const handleTagKeydown = (e) => {
  if (e.key === ',' || e.key === '，' || e.key === 'Enter') {
    e.preventDefault()
    addTag()
  }
}

const updateTags = () => {
  tags.value = tagList.value.join(', ')
}


// 自动保存逻辑
const debouncedSave = debounce(() => {
  handleSave(true)
}, 30000) // 30秒无操作自动同步

watch([content, title, tags, category, projectId, status], () => {
  if (content.value) {
    saveStatus.value = 'modified'
    debouncedSave()
  }
})

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

const toggleFocusMode = () => {
  isFocusMode.value = !isFocusMode.value
}

onMounted(() => {
    loadProjects()
    loadArticle()
})

onUnmounted(() => {
    debouncedSave.cancel()
})
</script>

<template>
  <div class="zenith-writer-container h-screen overflow-hidden bg-white selection:bg-indigo-100 selection:text-indigo-900 relative">
    <!-- Immersive Header (Glassmorphism) -->
    <header v-if="!isFocusMode" class="sticky top-0 left-0 right-0 z-50 backdrop-blur-xl bg-white/70 border-b border-gray-100/50 transition-all duration-300">
      <div class="max-w-6xl mx-auto flex items-center justify-between px-4 lg:px-0 py-4">
        <div class="flex-1 flex items-center gap-4 mr-8 min-w-0">
            <button 
                @click="router.back()" 
                class="flex-shrink-0 text-gray-400 hover:text-gray-900 transition-colors"
                title="返回列表"
            >
                <ArrowLeft class="w-5 h-5" />
            </button>
            <div class="h-4 w-px bg-gray-100 flex-shrink-0"></div>
            <input 
                v-model="title"
                type="text"
                placeholder="文章标题..." 
                class="bg-transparent border-none outline-none focus:ring-0 text-gray-900 font-black text-lg placeholder:text-gray-200 w-full"
            />
        </div>

        <div class="flex items-center gap-4">
            <div class="hidden md:flex items-center gap-3 text-gray-300">
                <!-- Save Status Indicator -->
                <div class="flex items-center gap-1.5 px-3 py-1 bg-gray-50 rounded-lg border border-gray-100 mr-2 transition-all">
                    <div :class="[
                      'w-1.5 h-1.5 rounded-full transition-all duration-500', 
                      saveStatus === 'saving' ? 'bg-amber-400 animate-pulse' : 
                      saveStatus === 'synced' ? 'bg-emerald-500' : 
                      saveStatus === 'modified' ? 'bg-indigo-400' : 'bg-red-500'
                    ]"></div>
                    <span class="text-[9px] font-black uppercase tracking-wider text-gray-400">
                        {{ 
                          saveStatus === 'saving' ? '同步中...' : 
                          saveStatus === 'synced' ? (lastSavedTime ? `已于 ${lastSavedTime} 同步` : '已同步至云端') : 
                          saveStatus === 'modified' ? '等待同步...' : '同步失败' 
                        }}
                    </span>
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest whitespace-nowrap">字数: {{ content.length }}</span>
                <span class="text-[10px] font-black uppercase tracking-widest whitespace-nowrap">预计: {{ Math.ceil(content.length / 500) }} 分</span>
            </div>
            
            <div class="flex items-center gap-2">
                <button 
                    @click="showSettings = !showSettings"
                    :class="['p-2 rounded-xl transition-all', showSettings ? 'bg-indigo-50 text-indigo-600' : 'text-gray-400 hover:text-gray-900 hover:bg-gray-50']"
                    title="撰写配置"
                >
                    <Settings2 class="w-4.5 h-4.5" />
                </button>
                <div class="w-px h-4 bg-gray-100 mx-1"></div>
                <button 
                    @click="handleSave()"
                    :disabled="isSaving"
                    class="bg-gray-900 text-white px-5 py-2 rounded-xl text-xs font-black shadow-lg shadow-gray-200 hover:bg-black active:scale-95 transition-all disabled:opacity-50"
                >
                    {{ isEdit ? '保存' : (status === 'published' ? '发布' : '存为草稿') }}
                </button>
            </div>
        </div>
      </div>
    </header>

    <!-- Settings Dialog (Teleport to Body to fix z-index issues) -->
    <Teleport to="body">
      <Transition name="fade-scale">
        <div v-if="showSettings" class="fixed inset-0 z-[2147483647] flex items-center justify-center p-4 md:p-10 pointer-events-auto settings-modal-container">
          <!-- Backdrop -->
          <div @click="showSettings = false" class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity"></div>
          
          <!-- Modal Content -->
          <div class="relative bg-white w-full max-w-5xl rounded-[3rem] shadow-2xl border border-gray-100 overflow-hidden flex flex-col max-h-[90vh]">
              <div class="flex items-center justify-between p-8 pb-4 border-b border-gray-50 text-left">
                  <div class="flex items-center gap-3">
                      <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
                          <Settings2 class="w-5 h-5" />
                      </div>
                      <h3 class="text-xl font-black text-gray-900">撰写配置</h3>
                  </div>
                  <button @click="showSettings = false" class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-50 text-gray-400 hover:text-gray-900 transition-colors">
                      <X class="w-6 h-6" />
                  </button>
              </div>
              
              <div class="flex-1 overflow-y-auto p-8 lg:p-12 custom-scrollbar text-left font-sans">
                  <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
                      <!-- Left: Categories -->
                      <div class="lg:col-span-4 space-y-6">
                          <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] px-2">内容分类</label>
                          <div class="space-y-3">
                              <div 
                                  v-for="cat in categories" 
                                  :key="cat.id"
                                  @click="category = cat.id"
                                  :class="[
                                      'p-5 rounded-3xl border-2 transition-all cursor-pointer group',
                                      category === cat.id ? 'border-indigo-600 bg-indigo-50/50 shadow-inner' : 'border-gray-50 bg-white hover:border-indigo-100'
                                  ]"
                              >
                                  <div class="flex items-center gap-4">
                                      <div :class="['w-10 h-10 rounded-xl flex items-center justify-center transition-colors', category === cat.id ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-400 group-hover:bg-indigo-50 group-hover:text-indigo-600']">
                                          <component :is="cat.icon" class="w-5 h-5" />
                                      </div>
                                      <div>
                                          <p class="text-sm font-black text-gray-800">{{ cat.name }}</p>
                                          <p class="text-[10px] text-gray-400 font-medium mt-0.5">{{ cat.desc }}</p>
                                      </div>
                                  </div>
                              </div>
                          </div>

                          <div class="pt-4 space-y-6">
                              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] px-2">发布状态</label>
                              <div class="grid grid-cols-2 gap-3">
                                  <div 
                                      v-for="s in statuses" 
                                      :key="s.id"
                                      @click="status = s.id"
                                      :class="[
                                          'p-4 rounded-2xl border-2 transition-all cursor-pointer text-center',
                                          status === s.id ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600' : 'border-gray-50 bg-white text-gray-400 hover:border-indigo-100'
                                      ]"
                                  >
                                      <p class="text-xs font-black">{{ s.name }}</p>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- Middle: Project & Tags -->
                      <div class="lg:col-span-4 space-y-8">
                          <div class="space-y-4">
                              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] px-2">关联项目</label>
                              <div class="relative">
                                  <select 
                                      v-model="projectId" 
                                      class="w-full bg-gray-50/50 border-2 border-transparent rounded-3xl px-6 py-5 text-sm font-bold text-gray-800 outline-none focus:border-indigo-500 focus:bg-white transition-all appearance-none cursor-pointer"
                                  >
                                      <option value="">独立文章 (不关联项目)</option>
                                      <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                                  </select>
                                  <ChevronDown class="absolute right-6 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                              </div>
                          </div>

                          <div class="space-y-4">
                              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] px-2 block">标签属性</label>
                              <div class="flex flex-wrap gap-2 p-4 bg-gray-50/50 border-2 border-transparent rounded-3xl focus-within:border-indigo-500 focus-within:bg-white transition-all min-h-[60px]">
                                  <span v-for="(tag, index) in tagList" :key="index" 
                                        class="flex items-center gap-1.5 px-3 py-1 bg-white border border-indigo-100 text-indigo-600 text-[11px] font-black rounded-lg shadow-sm">
                                    # {{ tag }}
                                    <button @click="removeTag(index)" class="hover:text-red-500 p-0.5">
                                      <X class="w-3 h-3" />
                                    </button>
                                  </span>
                                  <input 
                                      v-model="currentTag"
                                      type="text" 
                                      placeholder="输入标签按回车..."
                                      @keydown="handleTagKeydown"
                                      @blur="addTag"
                                      class="flex-1 bg-transparent border-none outline-none py-1 text-sm font-bold text-gray-800 outline-none placeholder:text-gray-300 font-sans min-w-[120px]"
                                  />
                              </div>
                          </div>
                      </div>

                      <!-- Right: Guidance Card -->
                      <div class="lg:col-span-4 flex flex-col">
                           <div class="flex-1 bg-indigo-900 rounded-[2.5rem] p-10 text-white relative overflow-hidden flex flex-col justify-end min-h-[300px]">
                              <div class="absolute top-0 right-0 w-48 h-48 bg-white/10 rounded-full blur-3xl -mr-16 -mt-16"></div>
                              <div class="relative z-10 text-left">
                                  <h4 class="text-xl font-black mb-4 flex items-center gap-3"><Eye class="w-6 h-6 text-indigo-300" /> 写作建议</h4>
                                  <p class="text-[13px] text-indigo-100/80 leading-relaxed font-medium">好的文章是思想的容器。尝试在标题中通过简单的陈述概括核心观点，并利用 Markdown 的多级标题构建清晰的叙事逻辑。</p>
                                  <div class="mt-10 flex flex-wrap gap-2">
                                       <div class="px-4 py-2 bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-wider">支持 Markdown</div>
                                       <div class="px-4 py-2 bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-wider">自动同步</div>
                                  </div>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>

              <div class="p-8 border-t border-gray-50 flex justify-end">
                  <button @click="showSettings = false" class="bg-gray-900 text-white px-10 py-4 rounded-2xl font-black text-sm hover:bg-black transition-all shadow-xl shadow-gray-200 active:scale-95">
                      完成配置
                  </button>
              </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Main Workspace -->
    <main :class="['overflow-hidden transition-all duration-500', isFocusMode ? 'h-screen pt-10' : 'h-[calc(100vh-4.5rem)]', showSettings ? 'opacity-0 pointer-events-none' : 'opacity-100']">
        <div class="max-w-6xl mx-auto h-full flex flex-col px-4 lg:px-0">
            <!-- Content Editor Section -->
            <div class="zenith-editor-wrapper flex-1 h-full overflow-hidden border-x border-gray-50">
                <MdEditor 
                    v-model="content" 
                    placeholder="沉淀此时此刻的思考，让灵感自然流淌..." 
                    style="height: 100%; border: none;"
                    :toolbarsExclude="['github', 'save', 'htmlPreview', 'catalog', 'header', 'italic', 'strikeThrough', 'sub', 'sup']"
                    :preview="!isFocusMode"
                    class="zenith-mde"
                />
            </div>
        </div>
    </main>

    <!-- Floating Actions (Bottom) -->
    <div class="absolute bottom-10 left-1/2 -translate-x-1/2 z-50 w-fit mx-auto">
        <div class="flex items-center gap-2 p-2 bg-gray-900/90 backdrop-blur-xl rounded-[2rem] shadow-2xl border border-white/10 scale-90 md:scale-100 origin-bottom">
             <button 
                @click="toggleFullscreen" 
                :class="['w-12 h-12 flex items-center justify-center rounded-xl transition-colors', isFullscreen ? 'bg-white text-gray-900' : 'text-gray-400 hover:text-white']" 
                title="全屏模式"
             >
                <Expand class="w-5 h-5" />
             </button>
             <button 
                @click="toggleFocusMode" 
                :class="['w-12 h-12 flex items-center justify-center rounded-xl transition-colors', isFocusMode ? 'bg-white text-gray-900' : 'text-gray-400 hover:text-white']" 
                title="聚焦模式"
             >
                <Eye class="w-5 h-5" />
             </button>
             <div class="w-px h-6 bg-white/10 mx-1"></div>
             <button @click="handleSave(true)" :disabled="isSaving" class="px-6 py-2.5 bg-indigo-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20 active:scale-95 disabled:opacity-50">
                {{ isSaving ? '同步中...' : '同步保存内容' }}
             </button>
        </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');

.zenith-writer-container {
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

.title-font {
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.04em;
}

/* MdEditor Reset & Style */
:deep(.md-editor) {
  --md-color: #1a1a1a;
  --md-bk-color: transparent;
}

:deep(.md-editor-content) {
  padding: 0;
}

:deep(.md-editor-textarea) {
    font-size: 1.25rem !important;
    line-height: 1.8 !important;
    color: #374151 !important;
    font-family: 'Inter', sans-serif !important;
}

:deep(.md-editor-toolbar-wrapper) {
    border-bottom: 1px solid #f3f4f6 !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(8px);
    position: sticky !important;
    top: 0;
    z-index: 45;
}

:deep(.md-editor-toolbar) {
    justify-content: center !important;
    flex-wrap: nowrap !important;
    gap: 0.5rem !important;
}

:deep(.md-editor-toolbar-item) {
    color: #94a3b8 !important;
    transition: all 0.2s !important;
    border-radius: 0.5rem !important;
}

:deep(.md-editor-toolbar-item:hover) {
    color: #4f46e5 !important;
    background: #f5f3ff !important;
}

/* Animations */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.fade-scale-enter-active .transition-opacity,
.fade-scale-leave-active .transition-opacity {
    transition: opacity 0.4s ease;
}

.fade-scale-enter-from .transition-opacity,
.fade-scale-leave-to .transition-opacity {
    opacity: 0;
}

/* Settings Modal Overrides */
.settings-modal-container {
    z-index: 2147483647 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #e5e7eb;
}
</style>
