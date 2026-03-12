<script setup>
import { ref, watch, onMounted } from 'vue'
import { FileText, Plus, ExternalLink, ChevronRight, Trash2 } from 'lucide-vue-next'
import { articleApi } from '../../../api/article'
import { useRouter } from 'vue-router'

const props = defineProps({
  projectId: {
    type: [Number, String],
    default: null
  }
})

const router = useRouter()
const articles = ref([])
const isLoading = ref(false)
const hasError = ref(false)

const fetchRelatedArticles = async (id) => {
  if (!id) {
    articles.value = []
    isLoading.value = false
    return
  }
  
  isLoading.value = true
  hasError.value = false
  try {
    const response = await articleApi.getArticles({ project_id: id })
    articles.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to fetch related articles:', error)
    hasError.value = true
    articles.value = []
  } finally {
    isLoading.value = false
  }
}

watch(() => props.projectId, (newId) => {
  fetchRelatedArticles(newId)
}, { immediate: true })

const navigateToArticle = (id) => {
  router.push(`/articles/${id}`)
}

const createNewArticle = () => {
  router.push({
    path: '/articles/new',
    query: { project_id: props.projectId }
  })
}

const deleteArticle = async (e, id) => {
  e.stopPropagation() // Prevent navigation
  if (!window.confirm('确定要删除这篇文章吗？此操作不可撤销。')) return
  try {
    await articleApi.deleteArticle(id)
    fetchRelatedArticles(props.projectId)
  } catch (error) {
    console.error('Failed to delete article', error)
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-black text-gray-800 flex items-center gap-2">
        <FileText class="w-5 h-5 text-primary" />
        相关文章
        <span class="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{{ articles.length }}</span>
      </h3>
      <button 
        @click="createNewArticle"
        class="flex items-center gap-1.5 text-sm font-bold text-primary hover:underline"
      >
        <Plus class="w-4 h-4" />
        撰写新文章
      </button>
    </div>

    <!-- 错误状态 -->
    <div v-if="hasError" class="p-6 bg-red-50 rounded-2xl border border-red-100 text-center">
      <p class="text-red-500 font-bold text-sm">加载文章失败，请稍后重试</p>
      <button @click="fetchRelatedArticles(props.projectId)" class="mt-2 text-red-600 underline text-xs">重试</button>
    </div>

    <div v-else-if="isLoading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-20 bg-gray-50 rounded-2xl animate-pulse"></div>
    </div>

    <div v-else-if="articles.length === 0" class="flex flex-col items-center justify-center py-12 bg-gray-50/50 rounded-3xl border border-dashed border-gray-100">
      <div class="bg-white p-4 rounded-full mb-4 shadow-sm">
        <FileText class="w-8 h-8 text-gray-200" />
      </div>
      <p class="text-gray-400 font-bold">暂无关联文章</p>
      <button @click="createNewArticle" class="mt-2 text-primary font-bold text-sm hover:underline">去写一篇记录一下？</button>
    </div>

    <div v-else class="grid grid-cols-1 gap-3">
      <div 
        v-for="article in articles" 
        :key="article.id"
        @click="navigateToArticle(article.id)"
        class="group flex items-center justify-between p-4 bg-white border border-gray-100 rounded-2xl hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer"
      >
        <div class="flex items-center gap-4 min-w-0">
          <div class="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center group-hover:bg-primary/5 transition-colors shrink-0">
            <FileText class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors" />
          </div>
          <div class="min-w-0">
            <h4 class="font-bold text-gray-800 group-hover:text-primary transition-colors truncate">{{ article.title || '无标题' }}</h4>
            <div class="flex items-center gap-3 mt-0.5">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">{{ article.category }}</span>
              <span class="text-[10px] text-gray-300">{{ new Date(article.created_at).toLocaleDateString() }}</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
          <button 
            @click="deleteArticle($event, article.id)" 
            class="p-2 text-gray-300 hover:text-red-500 transition-all rounded-xl hover:bg-red-50"
            title="删除文章"
          >
            <Trash2 class="w-4 h-4" />
          </button>
          <ChevronRight class="w-4 h-4 text-gray-300 group-hover:text-primary group-hover:translate-x-1 transition-all" />
        </div>
      </div>
    </div>
  </div>
</template>
