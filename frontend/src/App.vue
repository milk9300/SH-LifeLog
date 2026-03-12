<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  LayoutDashboard, 
  Lightbulb, 
  FolderKanban, 
  ListTodo, 
  BookOpen, 
  Shield, 
  Target, 
  Beaker, 
  FileText,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

const isCollapsed = ref(false)
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const router = useRouter()
const route = useRoute()

const navItems = [
  { path: '/', name: 'Dashboard', icon: LayoutDashboard, label: '工作台' },
  { path: '/brainstorm', name: 'Brainstorm', icon: Lightbulb, label: '头脑风暴' },
  { path: '/incubation', name: 'Incubation', icon: Beaker, label: '产品孵化' },
  { path: '/projects', name: 'Projects', icon: FolderKanban, label: '项目大厅' },
  { path: '/plans', name: 'Plans', icon: Target, label: '长期计划' },
  { path: '/tasks', name: 'Tasks', icon: ListTodo, label: '时间管理' },
  { path: '/knowledge', name: 'Knowledge', icon: BookOpen, label: '知识沉淀' },
  { path: '/articles', name: 'Articles', icon: FileText, label: '文章管理' },
  { path: '/vault', name: 'Vault', icon: Shield, label: '密码凭证' }
]

// 检查当前路由
const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

</script>

<template>
  <div class="min-h-screen bg-[#FAFAFA] flex flex-col md:flex-row">
    <!-- Sidebar (Desktop) / Header (Mobile) -->
    <aside 
      v-if="!route.meta.hideSidebar" 
      :class="[
        'bg-white border-r border-gray-100 flex flex-col items-center py-8 gap-10 md:sticky md:top-0 md:h-screen transition-all duration-300 relative group',
        isCollapsed ? 'w-full md:w-20' : 'w-full md:w-20 lg:w-64'
      ]"
    >
      <!-- Toggle Button (Desktop Only) -->
      <button 
        @click="toggleSidebar"
        class="hidden md:flex absolute -right-3 top-20 w-6 h-6 bg-white border border-gray-100 rounded-full items-center justify-center shadow-sm text-gray-400 hover:text-primary hover:border-primary/20 transition-all opacity-0 group-hover:opacity-100 z-50"
      >
        <component :is="isCollapsed ? ChevronRight : ChevronLeft" class="w-4 h-4" />
      </button>

      <div class="flex items-center gap-3 px-4">
        <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 shrink-0">
          <span class="text-white font-bold text-xl">SH</span>
        </div>
        <span 
          v-show="!isCollapsed"
          class="text-xl font-bold md:hidden lg:block text-lifelogText whitespace-nowrap overflow-hidden transition-all"
        >工作站</span>
      </div>

      <nav class="flex-1 w-full px-4 flex flex-row md:flex-col justify-center md:justify-start gap-2 overflow-x-auto md:overflow-x-visible">
        <router-link 
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 p-3 rounded-xl transition-all group/nav relative',
            isActive(item.path) 
              ? 'bg-primary/5 text-primary' 
              : 'text-gray-400 hover:bg-gray-50'
          ]"
          :title="isCollapsed ? item.label : ''"
        >
          <component :is="item.icon" class="w-6 h-6 shrink-0" />
          <span 
            v-show="!isCollapsed"
            class="font-medium md:hidden lg:block whitespace-nowrap overflow-hidden transition-all"
          >{{ item.label }}</span>

          <!-- Tooltip when collapsed -->
          <div 
            v-if="isCollapsed"
            class="hidden md:block absolute left-full ml-4 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 pointer-events-none group-hover/nav:opacity-100 transition-opacity whitespace-nowrap z-50"
          >
            {{ item.label }}
          </div>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main :class="['flex-1 w-full mx-auto', route.meta.hideSidebar ? '' : 'p-4 md:p-8 lg:p-10 max-w-[1600px]']">
      <router-view />
    </main>
  </div>
</template>

<style>
/* 全局动画 */
.animate-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
