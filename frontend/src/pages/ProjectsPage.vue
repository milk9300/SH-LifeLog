<script setup>
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/project'
import { useRouter } from 'vue-router'
import { Plus, FolderKanban, Target, ChevronRight, LayoutGrid, List } from 'lucide-vue-next'
import { projectApi } from '../api/project'

// Sub-components
import ProjectModal from '../components/business/projects/ProjectModal.vue'

const router = useRouter()
const projectStore = useProjectStore()
const { projects, isLoading, projectCounts } = storeToRefs(projectStore)

const currentStatusTab = ref('active')
const viewMode = ref('grid') // grid or list (grid by default for "Hall" feel)

const projectStatusMeta = {
  active: { label: '进行中', dotClass: 'text-green-500', bgClass: 'bg-green-50', borderClass: 'border-green-100' },
  preparation: { label: '准备中', dotClass: 'text-amber-500', bgClass: 'bg-amber-50', borderClass: 'border-amber-100' },
  deploying: { label: '部署中', dotClass: 'text-blue-500', bgClass: 'bg-blue-50', borderClass: 'border-blue-100' },
  done: { label: '已上线', dotClass: 'text-gray-400', bgClass: 'bg-gray-50', borderClass: 'border-gray-100' },
  graveyard: { label: '安息地', dotClass: 'text-purple-500', bgClass: 'bg-purple-50', borderClass: 'border-purple-100' }
}

const filteredProjects = computed(() => {
  return projects.value.filter(p => p.status === currentStatusTab.value)
})

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
  projectForm.value = { 
    name: '', 
    description: '', 
    reference_url: '', 
    git_url: '',
    tech_stack: '',
    project_type: 'Web',
    status: currentStatusTab.value === 'graveyard' ? 'preparation' : currentStatusTab.value 
  }
  showProjectModal.value = true
}

const handleSaveProject = async () => {
  if (!projectForm.value.name.trim()) return
  try {
    await projectApi.createProject(projectForm.value)
    showProjectModal.value = false
    await projectStore.fetchProjects()
  } catch (error) {
    console.error('Failed to create project', error)
  }
}

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}

const navigateToProject = (id) => {
  router.push(`/projects/${id}`)
}

onMounted(async () => {
  await projectStore.fetchProjects()
})
</script>

<template>
  <div class="space-y-8 animate-in pb-12">
    <!-- 头部：标题与主操作 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-gray-800 flex items-center gap-3">
          <FolderKanban class="w-8 h-8 text-primary" />
          项目大厅
        </h1>
        <p class="text-gray-500 mt-2 font-medium">聚合所有项目，聚焦目标与进度</p>
      </div>
      <button 
        @click="openProjectModal" 
        class="flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white rounded-2xl font-bold shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all"
      >
        <Plus class="w-5 h-5" />
        启动新项目
      </button>
    </div>

    <!-- 过滤器与视图切换 -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white/50 p-2 rounded-2xl border border-gray-100/50 backdrop-blur-sm">
      <div class="flex gap-1 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
        <button 
          v-for="(meta, key) in projectStatusMeta"
          :key="key"
          @click="currentStatusTab = key"
          class="px-4 py-2 rounded-xl text-sm font-bold whitespace-nowrap transition-all flex items-center gap-2"
          :class="currentStatusTab === key ? 'bg-gray-800 text-white shadow-md' : 'text-gray-500 hover:bg-white hover:shadow-sm'"
        >
          <span :class="meta.dotClass">●</span>
          {{ meta.label }}
          <span 
            class="px-1.5 py-0.5 rounded-md text-[10px] leading-none transition-colors"
            :class="currentStatusTab === key ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-400'"
          >{{ projectCounts[key] || 0 }}</span>
        </button>
      </div>

      <div class="flex items-center gap-1 bg-gray-100/50 p-1 rounded-xl shrink-0">
        <button 
          @click="viewMode = 'grid'"
          class="p-2 rounded-lg transition-all"
          :class="viewMode === 'grid' ? 'bg-white text-primary shadow-sm' : 'text-gray-400 hover:text-gray-600'"
        >
          <LayoutGrid class="w-4 h-4" />
        </button>
        <button 
          @click="viewMode = 'list'"
          class="p-2 rounded-lg transition-all"
          :class="viewMode === 'list' ? 'bg-white text-primary shadow-sm' : 'text-gray-400 hover:text-gray-600'"
        >
          <List class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="h-64 bg-gray-100 rounded-3xl animate-pulse"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredProjects.length === 0" class="flex flex-col items-center justify-center py-24 text-gray-400 bg-white rounded-3xl border border-dashed border-gray-200">
      <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-6">
        <Target class="w-10 h-10 text-gray-200" />
      </div>
      <p class="text-lg font-bold text-gray-400">在该分类下暂无项目</p>
      <button @click="openProjectModal" class="mt-4 text-primary font-bold hover:underline">创建一个试试？</button>
    </div>

    <!-- 项目列表/网格 -->
    <div 
      v-else 
      :class="[
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'flex flex-col gap-4'
      ]"
    >
      <div 
        v-for="project in filteredProjects" 
        :key="project.id"
        @click="navigateToProject(project.id)"
        class="group bg-white rounded-3xl border border-gray-100 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5 transition-all p-6 cursor-pointer flex flex-col relative overflow-hidden"
      >
        <!-- 装饰背景 -->
        <div class="absolute -right-4 -top-4 w-24 h-24 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors"></div>
        
        <div class="flex justify-between items-start mb-4 relative z-10">
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-black text-gray-800 leading-tight group-hover:text-primary transition-colors truncate pr-2">
              {{ project.name }}
            </h3>
          </div>
          <div 
            class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider shrink-0"
            :class="[projectStatusMeta[project.status].bgClass, projectStatusMeta[project.status].dotClass, 'border', projectStatusMeta[project.status].borderClass]"
          >
            {{ projectStatusMeta[project.status].label }}
          </div>
        </div>

        <p class="text-gray-500 text-sm line-clamp-2 mb-4 flex-1 min-h-[3rem]">
          {{ project.description || '暂无项目描述，点击进入详情添加更多信息...' }}
        </p>

        <!-- 补充内容 (类型与技术栈) -->
        <div class="flex flex-wrap gap-2 mb-6 relative z-10">
           <span v-if="project.project_type" class="px-2 py-1 rounded-lg bg-gray-50 border border-gray-100 text-[10px] font-black text-gray-400 uppercase tracking-wider">{{ project.project_type }}</span>
           <template v-if="project.tech_stack">
              <span v-for="tech in formatTags(project.tech_stack)" :key="tech" class="px-2 py-1 rounded-lg bg-white border border-indigo-100 text-indigo-600 text-[10px] font-black shadow-sm">
                # {{ tech }}
              </span>
           </template>
        </div>

        <div class="space-y-3 mt-auto relative z-10">
          <div class="flex items-center justify-between text-xs font-bold mb-1">
            <span class="text-gray-400">开发进度</span>
            <span class="text-primary">{{ project.progress || 0 }}%</span>
          </div>
          <div class="h-2 w-full bg-gray-50 rounded-full overflow-hidden border border-gray-100/50">
            <div 
              class="h-full bg-primary transition-all duration-700 rounded-full shadow-[0_0_8px_rgba(var(--primary-rgb),0.3)]"
              :style="{ width: `${project.progress || 0}%` }"
            ></div>
          </div>
          
          <div class="pt-4 flex items-center justify-between text-primary font-black text-sm opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
            <span>进入工作区</span>
            <ChevronRight class="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>

    <!-- 项目编辑 Modal -->
    <Teleport to="body">
      <ProjectModal 
        :show="showProjectModal"
        :editingProject="null"
        :projectForm="projectForm"
        @close="showProjectModal = false"
        @save="handleSaveProject"
      />
    </Teleport>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-clamp: 3;
  overflow: hidden;
}
</style>
