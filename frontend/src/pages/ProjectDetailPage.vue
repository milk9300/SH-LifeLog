<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/project'
import { 
  ArrowLeft, Target, Settings, ExternalLink, Github, Layers, 
  ClipboardList, BookText, ShieldCheck 
} from 'lucide-vue-next'
import { projectApi } from '../api/project'

// Sub-components
import TaskSection from '../components/business/projects/TaskSection.vue'
import VaultSection from '../components/business/projects/VaultSection.vue'
import ProjectModal from '../components/business/projects/ProjectModal.vue'
import GraveyardSection from '../components/business/projects/GraveyardSection.vue'
import GraveyardModal from '../components/business/projects/GraveyardModal.vue'
import RelatedArticlesSection from '../components/business/projects/RelatedArticlesSection.vue'
import { graveyardApi } from '../api/graveyard'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const { activeProject, projectProgress, isLoading } = storeToRefs(projectStore)

const projectId = route.params.id
const activeTab = ref('tasks')

// Status meta (consistent with ProjectsPage)
const projectStatusMeta = {
  preparation: { label: '准备中', dotClass: 'text-amber-500' },
  active: { label: '进行中', dotClass: 'text-green-500' },
  deploying: { label: '部署中', dotClass: 'text-blue-500' },
  done: { label: '已上线', dotClass: 'text-gray-400' },
  graveyard: { label: '安息地', dotClass: 'text-purple-500' }
}
const projectStatusCycle = ['preparation', 'active', 'deploying', 'done']

// Project Modal State
const showProjectModal = ref(false)
const projectForm = ref({ 
  name: '', 
  description: '', 
  reference_url: '', 
  git_url: '',
  tech_stack: '',
  project_type: 'Web',
  status: 'preparation' 
})

const openProjectModal = () => {
  if (activeProject.value) {
    projectForm.value = { 
      name: activeProject.value.name, 
      description: activeProject.value.description || '',
      reference_url: activeProject.value.reference_url || '',
      git_url: activeProject.value.git_url || '',
      tech_stack: activeProject.value.tech_stack || '',
      project_type: activeProject.value.project_type || 'Web',
      status: activeProject.value.status || 'preparation'
    }
  }
  showProjectModal.value = true
}

const handleSaveProject = async () => {
  if (!projectForm.value.name.trim()) return
  try {
    await projectApi.updateProject(activeProject.value.id, projectForm.value)
    showProjectModal.value = false
    await projectStore.fetchProjectById(projectId)
  } catch (error) {
    console.error('Failed to update project', error)
  }
}

// Graveyard Logic
const showGraveyardModal = ref(false)
const graveyardForm = ref({ reason: '', lessons: '' })

const handleBuryAction = () => {
  graveyardForm.value = { reason: '', lessons: '' }
  showGraveyardModal.value = true
}

const handleSaveGraveyard = async () => {
  if (!graveyardForm.value.reason.trim()) return
  try {
    await graveyardApi.createGraveyard({
      project_id: activeProject.value.id,
      reason: graveyardForm.value.reason,
      lessons: graveyardForm.value.lessons
    })
    showGraveyardModal.value = false
    await projectStore.fetchProjectById(projectId)
  } catch (error) {
    console.error('Failed to bury project', error)
  }
}

const handleToggleStatus = async () => {
  const currentIndex = projectStatusCycle.indexOf(activeProject.value.status)
  const nextIndex = currentIndex !== -1 ? (currentIndex + 1) % projectStatusCycle.length : 1
  const newStatus = projectStatusCycle[nextIndex]
  await projectStore.updateProjectStatus(activeProject.value.id, newStatus)
}

const getExternalLink = (url) => {
  if (!url) return '#'
  if (!/^https?:\/\//i.test(url)) {
    return `http://${url}`
  }
  return url
}

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}

onMounted(async () => {
  await projectStore.fetchProjectById(projectId)
})
</script>

<template>
  <div class="h-full flex flex-col gap-6 animate-in">
    <!-- 顶部导航与操作 -->
    <div class="flex items-center justify-between shrink-0">
      <button 
        @click="router.push('/projects')" 
        class="flex items-center gap-2 text-gray-500 hover:text-gray-800 transition-colors font-bold group"
      >
        <div class="w-8 h-8 rounded-xl bg-white border border-gray-100 flex items-center justify-center group-hover:bg-gray-50 shadow-sm transition-all">
          <ArrowLeft class="w-5 h-5" />
        </div>
        返回项目大厅
      </button>
      
      <div class="flex items-center gap-3">
        <button 
          v-if="activeProject && activeProject.status !== 'graveyard'"
          @click="openProjectModal" 
          class="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-100 rounded-2xl text-gray-600 hover:bg-gray-50 shadow-sm transition-all font-bold"
        >
          <Settings class="w-4 h-4" />
          项目设置
        </button>
        <button 
          v-if="activeProject && activeProject.status !== 'graveyard'"
          @click="handleBuryAction" 
          class="px-4 py-2.5 bg-purple-50 text-purple-600 rounded-2xl font-bold flex items-center gap-2 hover:bg-purple-100 transition-all border border-purple-100 shadow-sm"
        >
          埋入墓地
        </button>
      </div>
    </div>

    <!-- 主要栅格布局 -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6 overflow-hidden min-h-0">
      
      <!-- 加载/空状态处理 -->
      <div v-if="isLoading" class="lg:col-span-2 flex flex-col items-center justify-center text-gray-400 bg-white rounded-3xl border border-gray-100 shadow-sm">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent mb-4"></div>
        <p class="font-bold">加载中...</p>
      </div>

      <div v-else-if="!activeProject" class="lg:col-span-2 flex flex-col items-center justify-center text-gray-400 bg-white rounded-3xl border border-gray-100 shadow-sm">
        <Target class="w-16 h-16 text-gray-100 mb-4" />
        <p class="font-bold text-lg">未找到该项目</p>
      </div>

      <template v-else>
        <!-- 左侧边栏 -->
        <aside class="flex flex-col gap-6 overflow-y-auto pr-1 custom-scrollbar">
          <!-- 区域 1: 项目详情 -->
          <section class="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm relative overflow-hidden flex flex-col">
            <!-- 装饰 -->
            <div class="absolute -right-6 -top-6 w-32 h-32 bg-primary/5 rounded-full blur-3xl"></div>

            <!-- 标题与进度圆圈 -->
            <div class="flex items-center gap-5 mb-8 relative z-10">
              <div class="relative w-20 h-20 shrink-0">
                <svg class="w-full h-full transform -rotate-90">
                  <circle 
                    cx="40" cy="40" r="34" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="6" 
                    class="text-gray-100" 
                  />
                  <circle 
                    cx="40" cy="40" r="34" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="7" 
                    stroke-linecap="round"
                    class="text-primary transition-all duration-1000" 
                    :stroke-dasharray="2 * Math.PI * 34"
                    :stroke-dashoffset="2 * Math.PI * 34 * (1 - projectProgress / 100)"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-lg font-black text-gray-800 leading-none">{{ projectProgress }}%</span>
                  <span class="text-[8px] font-black text-gray-400 uppercase tracking-tighter mt-0.5">Progress</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <h1 class="text-2xl font-black text-gray-800 line-clamp-2 leading-tight mb-2">{{ activeProject.name }}</h1>
                <div 
                  @click="handleToggleStatus"
                  class="inline-flex items-center gap-1.5 cursor-pointer px-2.5 py-1 rounded-xl transition-all border shadow-sm text-[11px] font-black"
                  :class="[
                    projectStatusMeta[activeProject.status]?.dotClass || 'text-gray-400',
                    'bg-white border-gray-100 hover:border-primary/20 hover:scale-105 active:scale-95'
                  ]"
                >
                  <span class="text-[8px]">●</span>
                  {{ projectStatusMeta[activeProject.status]?.label || '未知状态' }}
                </div>
              </div>
            </div>

            <!-- 元数据标签 -->
            <div class="flex flex-wrap gap-2 mb-8 relative z-10">
              <div v-if="activeProject.project_type" class="px-2.5 py-1.5 rounded-xl bg-gray-50 border border-gray-100 text-[11px] font-black text-gray-500 flex items-center gap-1.5 shadow-sm">
                <Layers class="w-3.5 h-3.5 text-gray-400" />
                {{ activeProject.project_type }}
              </div>
              <template v-if="activeProject.tech_stack">
                <div v-for="tech in formatTags(activeProject.tech_stack)" :key="tech" class="px-2.5 py-1.5 rounded-xl bg-white border border-primary/20 text-[11px] font-black text-primary shadow-sm">
                  # {{ tech }}
                </div>
              </template>
            </div>

            <!-- 快捷链接 -->
            <div class="grid grid-cols-2 gap-3 mb-8 relative z-10">
              <a 
                v-if="activeProject.reference_url"
                :href="getExternalLink(activeProject.reference_url)"
                target="_blank"
                class="flex items-center justify-center gap-2 bg-blue-50 text-blue-600 px-3 py-2.5 rounded-2xl text-xs font-bold hover:bg-blue-100 transition-all border border-blue-200/40 shadow-sm"
              >
                <ExternalLink class="w-3.5 h-3.5" />
                访问环境
              </a>
              <a 
                v-if="activeProject.git_url"
                :href="getExternalLink(activeProject.git_url)"
                target="_blank"
                class="flex items-center justify-center gap-2 bg-gray-800 text-white px-3 py-2.5 rounded-2xl text-xs font-bold hover:bg-gray-900 transition-all shadow-sm"
              >
                <Github class="w-3.5 h-3.5" />
                Git 仓库
              </a>
            </div>

            <!-- 描述信息 -->
            <div class="relative z-10 pt-4 border-t border-gray-50 flex-1">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3 block">项目描述 / Project Overview</label>
              <p class="text-gray-600 text-[13px] leading-relaxed whitespace-pre-wrap font-medium">
                {{ activeProject.description || '暂无项目描述，点击设置可添加。' }}
              </p>
            </div>
          </section>

          <!-- 区域 2: 项目凭证 (Vault) -->
          <section class="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm">
            <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2">
               <ShieldCheck class="w-4 h-4 text-primary" />
               项目凭证 (Vault)
            </h3>
            <VaultSection hideHeader />
          </section>
        </aside>

        <!-- 右侧主内容 -->
        <main class="bg-white rounded-[2rem] border border-gray-100 shadow-sm flex flex-col overflow-hidden">
          <!-- 标签页头部 -->
          <div class="px-8 pt-6 border-b border-gray-50 bg-gray-50/10">
            <div class="flex gap-10">
              <button 
                @click="activeTab = 'tasks'"
                class="pb-4 text-sm font-black transition-all relative"
                :class="activeTab === 'tasks' ? 'text-gray-800' : 'text-gray-400 hover:text-gray-600'"
              >
                <div class="flex items-center gap-2.5">
                  <ClipboardList class="w-4 h-4" />
                  任务清单
                </div>
                <div v-if="activeTab === 'tasks'" class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full animate-in zoom-in-50"></div>
              </button>
              <button 
                @click="activeTab = 'articles'"
                class="pb-4 text-sm font-black transition-all relative"
                :class="activeTab === 'articles' ? 'text-gray-800' : 'text-gray-400 hover:text-gray-600'"
              >
                <div class="flex items-center gap-2.5">
                  <BookText class="w-4 h-4" />
                  相关文章
                </div>
                <div v-if="activeTab === 'articles'" class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full animate-in zoom-in-50"></div>
              </button>
            </div>
          </div>

          <!-- 内容滚动区 -->
          <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <template v-if="activeProject.status !== 'graveyard'">
              <div v-if="activeTab === 'tasks'" class="animate-in slide-in-from-bottom-2">
                <TaskSection hideHeader />
              </div>
              <div v-else-if="activeTab === 'articles'" class="animate-in slide-in-from-bottom-2">
                <RelatedArticlesSection :projectId="activeProject.id" />
              </div>
            </template>
            <template v-else>
              <GraveyardSection />
            </template>
          </div>
        </main>
      </template>
    </div>

    <!-- Modals -->
    <Teleport to="body">
      <ProjectModal 
        :show="showProjectModal"
        :editingProject="activeProject"
        :projectForm="projectForm"
        @close="showProjectModal = false"
        @save="handleSaveProject"
      />

      <GraveyardModal 
        :show="showGraveyardModal"
        :buryingProject="activeProject"
        :graveyardForm="graveyardForm"
        @close="showGraveyardModal = false"
        @save="handleSaveGraveyard"
      />
    </Teleport>
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
  background: #f1f1f1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #e5e5e5;
}
</style>
