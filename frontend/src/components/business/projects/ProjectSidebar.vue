<script setup>
import { useProjectStore } from '../../../stores/project'
import { Plus, FolderKanban, MoreVertical, Edit2, Trash2, Skull } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'

const projectStore = useProjectStore()
const { projects, activeProject, isLoading, projectCounts } = storeToRefs(projectStore)

const props = defineProps({
  currentStatusTab: String,
  projectStatusMeta: Object
})

const emit = defineEmits(['open-modal', 'delete-project', 'toggle-status', 'update-tab', 'bury-project'])

const filteredProjects = computed(() => {
  return projects.value.filter(p => p.status === props.currentStatusTab)
})

const getExternalLink = (url) => {
  if (!url) return '#'
  if (!/^https?:\/\//i.test(url)) {
    return `http://${url}`
  }
  return url
}
</script>

<template>
  <div class="w-full md:w-[400px] flex flex-col bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden shrink-0">
    <div class="p-6 border-b border-gray-50 flex items-center justify-between">
      <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
        <FolderKanban class="w-6 h-6 text-primary" />
        项目大厅
      </h2>
      <button 
        @click="emit('open-modal')" 
        class="p-2 bg-primary/10 text-primary rounded-xl hover:bg-primary/20 transition-colors"
        title="新建项目"
      >
        <Plus class="w-5 h-5" />
      </button>
    </div>

    <!-- 项目状态 Tabs -->
    <div class="px-4 py-2 border-b border-gray-50 flex gap-1 overflow-x-auto shrink-0">
      <button 
        v-for="(meta, key) in projectStatusMeta"
        :key="key"
        @click="emit('update-tab', key)"
        class="px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-colors flex items-center gap-1.5"
        :class="currentStatusTab === key ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-100'"
      >
        <span>{{ meta.label }}</span>
        <span 
          class="px-1.5 py-0.5 rounded-md text-[10px] leading-none transition-colors"
          :class="currentStatusTab === key ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'"
        >{{ projectCounts[key] || 0 }}</span>
      </button>
    </div>
    
    <div class="flex-1 overflow-y-auto p-4 space-y-3">
      <div v-if="isLoading" class="text-center py-10 text-gray-400 text-sm">加载中...</div>
      
      <div v-else-if="projects.length === 0" class="text-center py-10 text-gray-400 text-sm">
        还没有任何项目，点击右上角新建。
      </div>

      <div 
        v-for="project in filteredProjects" 
        :key="project.id"
        @click="projectStore.selectProject(project)"
        :class="[
          'p-4 rounded-2xl cursor-pointer transition-all border',
          activeProject?.id === project.id 
            ? 'bg-primary/5 border-primary/20 shadow-sm relative' 
            : 'bg-white border-transparent hover:border-gray-100 hover:bg-gray-50'
        ]"
      >
        <!-- 活动指示器 -->
        <div v-if="activeProject?.id === project.id" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-md"></div>
        
        <div class="flex items-start justify-between">
          <h3 class="font-bold text-gray-800 truncate pr-2">{{ project.name }}</h3>
          <div class="relative group" @click.stop>
            <button class="text-gray-400 hover:text-gray-600 p-1"><MoreVertical class="w-4 h-4" /></button>
            <div class="absolute right-0 top-full mt-1 w-28 bg-white border border-gray-100 shadow-lg rounded-xl overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button @click="emit('open-modal', project)" class="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-2">
                <Edit2 class="w-3 h-3" /> 编辑
              </button>
              <button v-if="project.status !== 'graveyard'" @click="emit('bury-project', project)" class="w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-purple-50 flex items-center gap-2 border-t border-gray-50">
                <Skull class="w-3 h-3" /> 埋入墓地
              </button>
              <button @click="emit('delete-project', project.id)" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 border-t border-gray-50">
                <Trash2 class="w-3 h-3" /> 删除
              </button>
            </div>
          </div>
        </div>
        <p class="text-xs mt-1 flex items-center justify-between gap-1 w-full">
          <button 
            @click.stop="emit('toggle-status', project)"
            class="flex items-center gap-1 hover:bg-gray-100 px-1 py-0.5 rounded transition-colors"
            :class="projectStatusMeta[project.status]?.dotClass || 'text-gray-400'"
            title="点击切换项目状态"
          >
            <span class="text-[10px]">●</span>
            {{ projectStatusMeta[project.status]?.label || '未知状态' }}
          </button>
          <a 
            v-if="project.reference_url" 
            :href="getExternalLink(project.reference_url)" 
            target="_blank" 
            class="text-blue-500 hover:text-blue-700 hover:underline flex items-center gap-1 shrink-0"
            @click.stop
          >
            <span class="truncate max-w-[80px]">跳转链接</span>
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
// For filteredProjects computed which was defined but needs import/correct setup in script setup
import { computed } from 'vue'
</script>
