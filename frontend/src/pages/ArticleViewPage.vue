<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articleApi } from '../api/article'
import { ArrowLeft, Clock, Tag, Calendar, Share2, Edit3, Trash2, ExternalLink, Bookmark, Download } from 'lucide-vue-next'
import { MdPreview, MdCatalog } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const isLoading = ref(true)

const categoryMap = {
  'technical': '技术文章',
  'reflection': '反思日记',
  'other': '其他文章'
}

const loadArticle = async () => {
  isLoading.value = true
  try {
    const res = await articleApi.getArticle(route.params.id)
    article.value = res.data || res
  } catch (error) {
    console.error('Failed to load article:', error)
    if (error.response?.status === 404) {
      alert('文章不存在')
      router.back()
    }
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const deleteArticle = async () => {
  if (!confirm('确定要永久删除这篇文章吗？此操作无法撤销。')) return
  try {
    await articleApi.deleteArticle(article.value.id)
    router.back()
  } catch (error) {
    console.error('Failed to delete article:', error)
    alert('删除失败，请稍后重试。')
  }
}

const editArticle = () => {
  router.push(`/articles/${article.value.id}/edit`)
}

const goBack = () => {
  router.back()
}

const scrollElement = document.documentElement

const copyLink = () => {
  navigator.clipboard.writeText(window.location.href)
  alert('链接已复制到剪贴板')
}

const exportMarkdown = () => {
  if (!article.value) return
  
  const content = `# ${article.value.title}\n\n${article.value.content || ''}`
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${article.value.title || 'article'}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const isScrolled = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 100
}

onMounted(() => {
  loadArticle()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="animate-in pb-20">
    <!-- Floating Action Bar (Island Design) -->
    <nav 
      :class="[
        'sticky top-6 z-50 transition-all duration-500 ease-in-out',
        isScrolled ? 'max-w-2xl' : 'max-w-4xl'
      ]" 
      class="mx-auto mb-12"
    >
      <div 
        :class="[
          'flex items-center justify-between px-6 py-3 rounded-2xl border transition-all duration-500',
          isScrolled 
            ? 'bg-white/70 backdrop-blur-xl border-gray-100 shadow-xl shadow-gray-200/40' 
            : 'bg-white border-transparent shadow-sm'
        ]"
      >
        <div class="flex items-center gap-4 overflow-hidden">
          <button @click="goBack" class="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all">
            <ArrowLeft class="w-5 h-5" />
          </button>
          
          <div class="h-4 w-px bg-gray-100 flex-shrink-0"></div>
          
          <!-- Article Title Preview (Visible when scrolled) -->
          <div 
            :class="[
              'transition-all duration-500 overflow-hidden whitespace-nowrap text-ellipsis',
              isScrolled ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0'
            ]"
          >
            <span class="text-sm font-black text-gray-800">{{ article?.title }}</span>
          </div>

          <!-- Go Back Label (Visible when NOT scrolled) -->
          <div 
            :class="[
              'transition-all duration-500',
              !isScrolled ? 'opacity-100' : 'opacity-0 translate-x-4 w-0 absolute'
            ]"
          >
            <span class="text-xs font-black text-gray-400 uppercase tracking-widest">返回列表</span>
          </div>
        </div>

        <div class="flex items-center gap-3" v-if="article">
          <button @click="editArticle" class="w-10 h-10 flex items-center justify-center text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all" title="编辑文章">
            <Edit3 class="w-5 h-5" />
          </button>
          <button @click="deleteArticle" class="w-10 h-10 flex items-center justify-center text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all" title="删除文章">
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-16 items-start px-4 sm:px-6 lg:px-8">
      <!-- Left Content Column (Main) -->
      <main class="lg:col-span-8 xl:col-span-9 space-y-8 max-w-4xl mx-auto w-full">
        <!-- Article Container -->
        <article v-if="article" class="bg-white rounded-[2.5rem] border border-gray-100/50 shadow-xl shadow-gray-200/30 overflow-hidden">
          <!-- Article Header -->
          <header class="p-8 md:p-12 border-b border-gray-50 bg-gradient-to-b from-gray-50/30 to-white">
            <div class="flex items-center gap-3 mb-6">
              <span class="px-3 py-1 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-lg shadow-lg shadow-indigo-600/20">
                {{ categoryMap[article.category] || '其他文章' }}
              </span>
              <div class="h-1 w-1 bg-gray-300 rounded-full"></div>
              <div class="flex items-center gap-1.5 text-gray-400 text-sm font-bold">
                <Calendar class="w-4 h-4" />
                {{ formatDate(article.created_at) }}
              </div>
              <div class="h-1 w-1 bg-gray-300 rounded-full"></div>
              <div class="flex items-center gap-1.5 text-gray-400 text-sm font-bold">
                <Clock class="w-4 h-4" />
                约 {{ Math.ceil((article.content?.length || 0) / 400) }} 分钟阅读
              </div>
            </div>

            <h1 class="text-3xl md:text-5xl font-black text-gray-900 leading-tight">
              {{ article.title }}
            </h1>
          </header>

          <!-- Markdown Body -->
          <div class="p-8 md:p-12 prose-container">
            <MdPreview :editorId="'preview-page'" :modelValue="article.content || '> 暂无正文内容'" />
          </div>

          <!-- Footer/Share (Mobile perspective) -->
          <footer class="p-8 bg-gray-50/50 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-6 lg:hidden">
            <div class="flex items-center gap-2">
              <Share2 class="w-5 h-5 text-gray-400" />
              <span class="text-sm font-bold text-gray-400">分享这篇文章</span>
            </div>
            <div class="flex gap-2">
                <button @click="copyLink" class="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-600 hover:border-indigo-600 hover:text-indigo-600 transition-all">拷贝链接</button>
                <button @click="exportMarkdown" class="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-600 hover:border-indigo-600 hover:text-indigo-600 transition-all">导出 MD</button>
            </div>
          </footer>
        </article>

        <!-- Loading State -->
        <div v-else-if="isLoading" class="bg-white rounded-[2.5rem] p-20 flex flex-col items-center justify-center border border-gray-100 shadow-sm overflow-hidden min-h-[60vh]">
          <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
          <p class="text-gray-400 font-medium">深度解析内容中...</p>
        </div>
      </main>

      <!-- Right Sidebar Column -->
      <aside class="lg:col-span-4 xl:col-span-3 space-y-6 lg:sticky lg:top-32">
        <!-- Quick Actions Card -->
        <section class="bg-white/80 backdrop-blur-xl rounded-[2rem] border border-white/20 shadow-xl shadow-gray-200/20 p-6 space-y-4">
          <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 pb-2">快捷操作</h3>
          <div class="grid grid-cols-2 gap-3">
            <button @click="copyLink" class="group flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-50 hover:bg-indigo-600 transition-all">
              <Share2 class="w-5 h-5 text-gray-400 group-hover:text-white" />
              <span class="text-[10px] font-black text-gray-500 group-hover:text-white">分享</span>
            </button>
            <button @click="exportMarkdown" class="group flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-50 hover:bg-indigo-600 transition-all">
              <Download class="w-5 h-5 text-gray-400 group-hover:text-white" />
              <span class="text-[10px] font-black text-gray-500 group-hover:text-white">导出 MD</span>
            </button>
          </div>
        </section>

        <!-- TOC Card -->
        <section v-if="article?.content" class="bg-white/80 backdrop-blur-xl rounded-[2rem] border border-white/20 shadow-xl shadow-gray-200/20 p-6">
          <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest border-b border-gray-100 pb-4 mb-4 flex items-center gap-2">
            <Bookmark class="w-4 h-4" />
            内容导航
          </h3>
          <div class="toc-container max-h-[calc(100vh-400px)] overflow-y-auto">
            <MdCatalog :editorId="'preview-page'" :scrollElement="scrollElement" />
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
:deep(.md-editor-preview) {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #374151;
  line-height: 1.8;
  font-size: 1.125rem;
}

:deep(.md-editor-preview h1),
:deep(.md-editor-preview h2),
:deep(.md-editor-preview h3) {
  color: #111827;
  font-weight: 800;
  margin-top: 2.5rem;
  margin-bottom: 1.25rem;
  scroll-margin-top: 7rem;
}

:deep(.md-editor-preview p) {
  margin-bottom: 1.5rem;
}

:deep(.md-editor-preview blockquote) {
  border-left: 4px solid #6366f1;
  background-color: #f8fafc;
  padding: 1.5rem 2rem;
  border-radius: 0 1rem 1rem 0;
  margin: 2rem 0;
  font-style: italic;
  color: #4b5563;
}

:deep(.md-editor-preview .md-editor-code) {
  border-radius: 1.5rem;
  overflow: hidden;
  margin: 2.5rem 0;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  background-color: #1e293b !important; /* Unified dark background */
}

:deep(.md-editor-preview .md-editor-code-head) {
  background-color: #1e293b !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.md-editor-preview pre) {
  margin: 0 !important;
  padding: 1.5rem !important;
  background-color: transparent !important; /* Remove internal background */
}

:deep(.md-editor-preview code) {
  background-color: transparent !important; /* Clear inline code style when inside pre */
  padding: 0;
  border-radius: 0;
  color: #e2e8f0;
  font-family: 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* Re-apply inline code style for text that is NOT inside pre */
:deep(.md-editor-preview p code),
:deep(.md-editor-preview li code) {
  background-color: #f1f5f9;
  padding: 0.2rem 0.4rem;
  border-radius: 0.4rem;
  font-size: 0.85em;
  color: #4f46e5;
  font-family: inherit;
}

:deep(.prose-container) {
  max-width: none;
}

.toc-container :deep(.md-editor-catalog-link) {
  font-size: 0.875rem;
  font-weight: 700;
  color: #64748b;
  padding: 10px 14px;
  border-radius: 12px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.4;
}

.toc-container :deep(.md-editor-catalog-link:hover) {
  color: #4f46e5;
  background: #f5f3ff;
}

.toc-container :deep(.md-editor-catalog-active > .md-editor-catalog-link) {
  color: #4f46e5;
  background: #f5f3ff;
  font-weight: 800;
  box-shadow: inset 2px 0 0 #4f46e5;
}

.toc-container :deep(.md-editor-catalog-link span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Print Styles */
@media print {
  aside, nav, footer {
    display: none !important;
  }
  .max-w-\[1440px\] {
    max-width: none !important;
    padding: 0 !important;
  }
  main {
    width: 100% !important;
  }
  article {
    border: none !important;
    box-shadow: none !important;
  }
}
</style>
