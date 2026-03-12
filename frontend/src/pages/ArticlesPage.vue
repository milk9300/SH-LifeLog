<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { 
  BookOpen, FileText, Plus, Search, Filter, 
  ChevronRight, Hash, Clock, LayoutGrid, List, ChevronLeft,
  Calendar, ArrowUpDown, MoreHorizontal, Square, Trash2, Edit
} from 'lucide-vue-next'
import { articleApi } from '../api/article'
import { projectApi } from '../api/project'
import { planApi } from '../api/plan'
import { useRouter, useRoute } from 'vue-router'
/* #endregion */

const router = useRouter()
const route = useRoute()

// 从 URL 初始化状态
const articles = ref([])
const projects = ref([])
const plans = ref([])
const isLoading = ref(true)
const currentCategory = ref(route.query.category || 'all') 
const searchQuery = ref(route.query.q || '')
const sortBy = ref(route.query.sort || 'latest') // 'latest', 'oldest', 'title'
const statusFilter = ref(route.query.status || 'all') // 'all', 'published', 'draft'
const projectFilter = ref(route.query.project || 'all')
const planFilter = ref(route.query.plan || 'all')
const showSortMenu = ref(false)
const showFilterMenu = ref(false)
const filterMenuRef = ref(null)
const sortMenuRef = ref(null)
const activeMenuId = ref(null)
const projectSearch = ref('')
const planSearch = ref('')

// Pagination logic
const currentPage = ref(parseInt(route.query.page) || 1)
const pageSize = ref(parseInt(route.query.size) || 8)
const pageSizeOptions = [8, 16, 24, 32]

const categories = [
  { id: 'all', name: 'All', icon: LayoutGrid },
  { id: 'technical', name: '技术文章', icon: Hash },
  { id: 'reflection', name: '反思日记', icon: FileText },
  { id: 'other', name: '其他文章', icon: BookOpen }
]

const loadData = async () => {
  isLoading.value = true
  try {
    const [articlesRes, projectsRes, plansRes] = await Promise.all([
      articleApi.getArticles(),
      projectApi.getProjects(),
      planApi.getPlans()
    ])
    // Robust data extraction
    articles.value = articlesRes?.data || articlesRes || []
    projects.value = projectsRes?.data || projectsRes || []
    plans.value = plansRes?.data || plansRes || []
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    isLoading.value = false
  }
}

const filteredArticles = computed(() => {
  let result = [...articles.value]
  
  // Category Filter
  if (currentCategory.value !== 'all') {
    result = result.filter(a => a.category === currentCategory.value)
  }

  // Status Filter
  if (statusFilter.value !== 'all') {
    result = result.filter(a => a.status === statusFilter.value)
  }

  // Project Filter
  if (projectFilter.value !== 'all') {
    result = result.filter(a => a.project_id === parseInt(projectFilter.value))
  }

  // Plan Filter
  if (planFilter.value !== 'all') {
    result = result.filter(a => a.plan_id === parseInt(planFilter.value))
  }

  // Search Filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(a => 
      a.title?.toLowerCase().includes(q) || 
      a.content?.toLowerCase().includes(q)
    )
  }

  // Sorting
  if (sortBy.value === 'latest') {
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortBy.value === 'oldest') {
    result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  } else if (sortBy.value === 'title') {
    result.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
  }
  
  return result
})

const filteredProjectsList = computed(() => {
  if (!projectSearch.value) return projects.value
  const q = projectSearch.value.toLowerCase()
  return projects.value.filter(p => p.name?.toLowerCase().includes(q))
})

const filteredPlansList = computed(() => {
  if (!planSearch.value) return plans.value
  const q = planSearch.value.toLowerCase()
  return plans.value.filter(p => p.title?.toLowerCase().includes(q))
})

const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredArticles.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredArticles.value.length / pageSize.value) || 1
})

// Reset to page 1 on filter changes (except when page itself changes)
watch([currentCategory, searchQuery, statusFilter, projectFilter, planFilter, sortBy, pageSize], () => {
  if (currentPage.value !== 1) {
    currentPage.value = 1
  }
})

// 互斥逻辑：项目和计划不能同时筛选
watch(projectFilter, (newVal) => {
  if (newVal !== 'all' && planFilter.value !== 'all') {
    planFilter.value = 'all'
  }
})

watch(planFilter, (newVal) => {
  if (newVal !== 'all' && projectFilter.value !== 'all') {
    projectFilter.value = 'all'
  }
})

// 监听所有筛选和分页状态，同步到 URL
watch(
  [currentCategory, searchQuery, statusFilter, projectFilter, planFilter, sortBy, currentPage, pageSize],
  () => {
    const query = {}
    if (currentCategory.value !== 'all') query.category = currentCategory.value
    if (searchQuery.value) query.q = searchQuery.value
    if (statusFilter.value !== 'all') query.status = statusFilter.value
    if (projectFilter.value !== 'all') query.project = projectFilter.value
    if (planFilter.value !== 'all') query.plan = planFilter.value
    if (sortBy.value !== 'latest') query.sort = sortBy.value
    if (currentPage.value !== 1) query.page = currentPage.value
    if (pageSize.value !== 8) query.size = pageSize.value

    router.replace({ query })
  },
  { deep: true }
)

const categoryCounts = computed(() => {
  const counts = { all: articles.value.length, technical: 0, reflection: 0, other: 0 }
  articles.value.forEach(a => {
    const cat = a.category || 'other'
    counts[cat] = (counts[cat] || 0) + 1
  })
  return counts
})

const getSortLabel = () => {
  const labels = { latest: '最新发布', oldest: '最早发布', title: '标题排序' }
  return labels[sortBy.value] || '默认排序'
}

const getProjectName = (id) => {
  const p = projects.value.find(p => p.id === id)
  return p ? p.name : `项目 #${id}`
}

const getPlanName = (id) => {
  const p = plans.value.find(p => p.id === id)
  return p ? p.title : `计划 #${id}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toISOString().split('T')[0]
}

const extractSummary = (content) => {
  if (!content) return '暂无内容'
  return content.replace(/[#*`>\[\]\(\)-]/g, '').slice(0, 100) + (content.length > 100 ? '...' : '')
}

const calculateReadTime = (content) => {
  const words = content?.length || 0
  return Math.ceil(words / 400) || 1
}

const getCategoryLabel = (cat) => {
  const category = categories.find(c => c.id === cat)
  return category ? category.name : '其他文章'
}

const getCategoryIcon = (cat) => {
  const category = categories.find(c => c.id === cat)
  return category ? category.icon : BookOpen
}

const getStatusLabel = (status) => {
  const labels = { published: '已发布', draft: '草稿' }
  return labels[status] || '草稿'
}

const viewArticle = (id) => {
  router.push(`/articles/${id}`)
}

const createNewArticle = () => {
  router.push('/articles/new')
}

const editArticle = (id) => {
  router.push(`/articles/${id}/edit`)
}

const toggleMenu = (id) => {
  activeMenuId.value = activeMenuId.value === id ? null : id
}

const deleteArticle = async (id) => {
  const article = articles.value.find(a => a.id === id)
  if (!confirm(`确定要删除文章《${article?.title}》吗？`)) return
  
  try {
    await articleApi.deleteArticle(id)
    await loadData() // 刷新列表
  } catch (err) {
    console.error('Failed to delete article:', err)
  } finally {
    activeMenuId.value = null
  }
}

const handleClickOutside = (event) => {
  if (filterMenuRef.value && !filterMenuRef.value.contains(event.target)) {
    showFilterMenu.value = false
    projectSearch.value = ''
    planSearch.value = ''
  }
  if (sortMenuRef.value && !sortMenuRef.value.contains(event.target)) {
    showSortMenu.value = false
  }
  // 关闭卡片菜单
  if (!event.target.closest('.action-menu-container')) {
    activeMenuId.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadData()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="animate-in max-w-[1440px] mx-auto px-6 pb-20">
    <!-- Header -->
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 pt-10">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-600/20 text-white">
          <BookOpen class="w-8 h-8" />
        </div>
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight flex items-center gap-3">
            文章管理
          </h1>
          <p class="text-gray-400 mt-1 font-medium">沉淀思考，记录成长，构建你的个人知识库。</p>
        </div>
      </div>
      
      <button @click="createNewArticle" class="flex items-center gap-2 bg-[#0f172a] text-white px-8 py-4 rounded-2xl font-black text-sm hover:bg-black transition-all shadow-xl shadow-gray-200 active:scale-95">
        <Plus class="w-5 h-5" />
        撰写新文章
      </button>
    </header>

    <!-- Toolbar: Search & Filters -->
    <div class="bg-white rounded-[2rem] border border-gray-100 shadow-sm p-4 mb-10 flex flex-col lg:flex-row items-center justify-between gap-4">
      <!-- Tabs -->
      <div class="flex items-center gap-2 overflow-x-auto pb-2 lg:pb-0 w-full lg:w-auto">
        <button 
          v-for="cat in categories" 
          :key="cat.id"
          @click="currentCategory = cat.id"
          :class="[
            'px-5 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap text-sm',
            currentCategory === cat.id 
              ? 'bg-indigo-50 text-indigo-600' 
              : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
          ]"
        >
          {{ cat.name }}
          <span class="px-2 py-0.5 rounded-full text-[10px] bg-gray-100/50 text-gray-400 font-black">
            {{ categoryCounts[cat.id] || 0 }}
          </span>
        </button>
      </div>

      <!-- Search & Sort -->
      <div class="flex items-center gap-3 w-full lg:w-auto relative">
        <div class="relative flex-1 lg:w-80">
          <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索标题或内容..."
            class="w-full bg-gray-50 border-none rounded-2xl py-3 pl-11 pr-4 text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder:text-gray-400"
          />
        </div>
        
        <!-- Filter Dropdown -->
        <div class="relative" ref="filterMenuRef">
          <button 
            @click="showFilterMenu = !showFilterMenu"
            :class="[
              'flex items-center gap-2 px-5 py-3 border rounded-2xl text-sm font-bold transition-all whitespace-nowrap',
              (statusFilter !== 'all' || projectFilter !== 'all' || planFilter !== 'all') ? 'border-indigo-600 bg-indigo-50 text-indigo-600' : 'border-gray-100 text-gray-500 hover:bg-gray-50'
            ]"
          >
            <Filter class="w-4 h-4" />
            筛选
          </button>
          
          <div v-if="showFilterMenu" class="absolute right-0 mt-2 w-72 bg-white rounded-3xl border border-gray-100 shadow-2xl z-50 p-4 animate-in space-y-4">
            <div class="flex items-center justify-between mb-2">
               <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">高级筛选</p>
               <button 
                v-if="statusFilter !== 'all' || projectFilter !== 'all' || planFilter !== 'all'"
                @click="statusFilter = 'all'; projectFilter = 'all'; planFilter = 'all'; projectSearch = ''; planSearch = ''; showFilterMenu = false"
                class="text-[10px] font-black text-indigo-600 hover:text-indigo-700"
               >
                 清除全部
               </button>
            </div>
            
            <!-- Status Section -->
            <div class="space-y-1">
              <p class="px-2 text-[9px] font-black text-gray-300 uppercase tracking-tighter">文章状态</p>
              <div class="flex flex-wrap gap-1">
                <button 
                  v-for="status in [{id: 'all', name: '全部'}, {id: 'published', name: '已发布'}, {id: 'draft', name: '草稿'}]" 
                  :key="status.id"
                  @click="statusFilter = status.id"
                  :class="['px-3 py-1.5 rounded-lg text-[11px] font-bold transition-colors', statusFilter === status.id ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100']"
                >
                  {{ status.name }}
                </button>
              </div>
            </div>

            <!-- Project Section -->
            <div class="space-y-1">
              <p class="px-2 text-[9px] font-black text-gray-300 uppercase tracking-tighter">所属项目</p>
              <div class="px-2 pb-1 relative">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-300" />
                <input 
                  v-model="projectSearch"
                  type="text"
                  placeholder="搜索项目..."
                  class="w-full bg-gray-50/80 border-none rounded-lg py-1.5 pl-7 pr-2 text-[10px] font-bold focus:ring-1 focus:ring-indigo-500/20 transition-all placeholder:text-gray-300"
                />
              </div>
              <div class="max-h-32 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                <button 
                  @click="projectFilter = 'all'"
                  :class="['w-full text-left px-3 py-2 rounded-xl text-xs font-bold transition-colors', projectFilter === 'all' ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:bg-gray-50']"
                >
                  所有项目
                </button>
                <button 
                  v-for="proj in filteredProjectsList" 
                  :key="proj.id"
                  @click="projectFilter = proj.id"
                  :class="['w-full text-left px-3 py-2 rounded-xl text-xs font-bold flex items-center justify-between transition-colors', projectFilter === proj.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-500 hover:bg-gray-50']"
                >
                  {{ proj.name }}
                </button>
              </div>
            </div>

            <!-- Plan Section -->
            <div class="space-y-1">
              <p class="px-2 text-[9px] font-black text-gray-300 uppercase tracking-tighter">所属计划</p>
              <div class="px-2 pb-1 relative">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-300" />
                <input 
                  v-model="planSearch"
                  type="text"
                  placeholder="搜索计划..."
                  class="w-full bg-gray-50/80 border-none rounded-lg py-1.5 pl-7 pr-2 text-[10px] font-bold focus:ring-1 focus:ring-indigo-500/20 transition-all placeholder:text-gray-300"
                />
              </div>
              <div class="max-h-32 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                <button 
                  @click="planFilter = 'all'"
                  :class="['w-full text-left px-3 py-2 rounded-xl text-xs font-bold transition-colors', planFilter === 'all' ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:bg-gray-50']"
                >
                  所有计划
                </button>
                <button 
                  v-for="plan in filteredPlansList" 
                  :key="plan.id"
                  @click="planFilter = plan.id"
                  :class="['w-full text-left px-3 py-2 rounded-xl text-xs font-bold flex items-center justify-between transition-colors', planFilter === plan.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-500 hover:bg-gray-50']"
                >
                  {{ plan.title }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sort Dropdown -->
        <div class="relative" ref="sortMenuRef">
          <button 
            @click="showSortMenu = !showSortMenu"
            class="flex items-center gap-2 px-5 py-3 border border-gray-100 rounded-2xl text-sm font-bold text-gray-500 hover:bg-gray-50 transition-all whitespace-nowrap"
          >
            {{ getSortLabel() }}
            <ArrowUpDown class="w-4 h-4" />
          </button>

          <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-2xl border border-gray-100 shadow-xl z-50 p-2 animate-in">
            <button 
              v-for="sort in [{id: 'latest', name: '最新发布'}, {id: 'oldest', name: '最早发布'}, {id: 'title', name: '标题排序'}]" 
              :key="sort.id"
              @click="sortBy = sort.id; showSortMenu = false"
              :class="['w-full text-left px-3 py-2 rounded-xl text-sm font-bold flex items-center justify-between transition-colors', sortBy === sort.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50']"
            >
              {{ sort.name }}
              <Square v-if="sortBy === sort.id" class="w-3 h-3 fill-indigo-600" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Articles List -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-24 gap-4">
      <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
      <p class="text-gray-400 font-medium tracking-tight">内容检索中...</p>
    </div>

    <div v-else-if="filteredArticles.length === 0" class="bg-white rounded-[3rem] p-24 text-center border border-dashed border-gray-200">
      <div class="bg-gray-50 w-24 h-24 rounded-[2rem] flex items-center justify-center mx-auto mb-6">
        <FileText class="w-10 h-10 text-gray-300" />
      </div>
      <h3 class="text-2xl font-black text-gray-800 mb-2">未发现相关记录</h3>
      <p class="text-gray-400 max-w-sm mx-auto mb-10 font-medium">调整搜索条件或开始书写您的第一篇{{ getCategoryLabel(currentCategory) }}。</p>
      <button @click="createNewArticle" class="bg-indigo-600 text-white px-10 py-4 rounded-2xl font-black hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-100">
        立即起笔
      </button>
    </div>

    <div v-else>
      <!-- Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div 
          v-for="article in paginatedArticles" 
          :key="article.id"
          @click="viewArticle(article.id)"
          class="group bg-white p-6 rounded-[2.5rem] border border-transparent shadow-sm hover:shadow-2xl hover:shadow-gray-200/50 hover:border-indigo-100 transition-all duration-500 cursor-pointer flex flex-col justify-between"
        >
        <div>
          <!-- Card Header Tags -->
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <component :is="getCategoryIcon(article.category)" class="w-5 h-5" stroke-width="2.5" />
              </div>
              <span class="text-sm font-black text-indigo-600">{{ getCategoryLabel(article.category) }}</span>
            </div>
            
            <div :class="['flex items-center gap-2 px-3 py-1.5 rounded-full', article.status === 'published' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600']">
              <div :class="['w-1.5 h-1.5 rounded-full', article.status === 'published' ? 'bg-emerald-500' : 'bg-amber-500']"></div>
              <span class="text-[10px] font-black tracking-widest">{{ getStatusLabel(article.status) }}</span>
            </div>
          </div>
          
          <h2 class="text-2xl font-black text-gray-900 group-hover:text-indigo-600 transition-colors mb-4 leading-snug">
            {{ article.title }}
          </h2>
          
          <p class="text-gray-400 font-medium leading-relaxed mb-8 line-clamp-3">
            {{ extractSummary(article.content) }}
          </p>

          <!-- Association info -->
          <div class="flex flex-wrap gap-2 mb-10">
             <div v-if="article.project_id" class="flex items-center gap-1.5 text-[11px] font-black text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100 uppercase tracking-tighter">
                <Hash class="w-3.5 h-3.5" />
                {{ getProjectName(article.project_id) }}
             </div>
             <div v-if="article.plan_id" class="flex items-center gap-1.5 text-[11px] font-black text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100 uppercase tracking-tighter">
                <Calendar class="w-3.5 h-3.5" />
                {{ getPlanName(article.plan_id) }}
             </div>
             <!-- Tags from actual content -->
             <div v-if="article.tags" class="flex flex-wrap gap-2">
               <span v-for="tag in article.tags.split(',')" :key="tag" class="flex items-center gap-1.5 px-3 py-1 bg-white border border-indigo-100 text-indigo-600 text-[11px] font-black rounded-lg shadow-sm">
                # {{ tag.trim() }}
               </span>
             </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="flex items-center justify-between pt-6 border-t border-gray-50 mt-auto">
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-2 text-gray-400 text-sm font-bold">
              <Calendar class="w-4 h-4" />
              {{ formatDate(article.created_at) }}
            </div>
            <div class="flex items-center gap-2 text-gray-400 text-sm font-bold">
              <Clock class="w-4 h-4" />
              {{ calculateReadTime(article.content) }} min
            </div>
          </div>
          
          <div class="relative action-menu-container">
            <button 
              @click.stop="toggleMenu(article.id)" 
              :class="['p-2 rounded-xl transition-all', activeMenuId === article.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-300 hover:text-gray-600']"
            >
              <MoreHorizontal class="w-6 h-6" />
            </button>

            <!-- Dropdown Menu -->
            <transition name="fade">
              <div 
                v-if="activeMenuId === article.id" 
                class="absolute right-0 bottom-full mb-2 w-32 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50 p-2 overflow-hidden"
              >
                <button 
                  @click.stop="editArticle(article.id)" 
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 transition-all"
                >
                  <Edit class="w-4 h-4" />
                  编辑文章
                </button>
                <button 
                  @click.stop="deleteArticle(article.id)" 
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold text-red-500 hover:bg-red-50 transition-all"
                >
                  <Trash2 class="w-4 h-4" />
                  删除文章
                </button>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination UI -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-6 bg-white/50 backdrop-blur-sm p-6 rounded-[2rem] border border-gray-100">
        <div class="flex items-center gap-4">
          <span class="text-xs font-black text-gray-400 uppercase tracking-widest">每页展示</span>
          <div class="flex gap-1 bg-gray-100 p-1 rounded-xl">
            <button 
              v-for="size in pageSizeOptions" 
              :key="size"
              @click="pageSize = size"
              :class="['px-3 py-1.5 rounded-lg text-[10px] font-black transition-all', pageSize === size ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-400 hover:text-gray-600']"
            >
              {{ size }}
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button 
            @click="currentPage > 1 && currentPage--"
            :disabled="currentPage === 1"
            class="w-10 h-10 flex items-center justify-center rounded-xl border border-gray-100 bg-white text-gray-400 hover:text-indigo-600 hover:border-indigo-100 transition-all disabled:opacity-30 disabled:pointer-events-none"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          
          <div class="flex items-center gap-1">
            <button 
              v-for="p in totalPages" 
              :key="p"
              v-show="Math.abs(p - currentPage) < 3 || p === 1 || p === totalPages"
              @click="currentPage = p"
              :class="['w-10 h-10 flex items-center justify-center rounded-xl font-bold transition-all', currentPage === p ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'text-gray-400 hover:bg-gray-50']"
            >
              {{ p }}
            </button>
          </div>

          <button 
            @click="currentPage < totalPages && currentPage++"
            :disabled="currentPage === totalPages"
            class="w-10 h-10 flex items-center justify-center rounded-xl border border-gray-100 bg-white text-gray-400 hover:text-indigo-600 hover:border-indigo-100 transition-all disabled:opacity-30 disabled:pointer-events-none"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>

        <div class="text-xs font-black text-gray-400 uppercase tracking-widest">
          共 {{ filteredArticles.length }} 篇文章, 第 {{ currentPage }} / {{ totalPages }} 页
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-in {
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar {
  height: 0px;
}
</style>
