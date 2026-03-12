<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, FileText, HelpCircle, Plus, Edit, Trash2, CheckCircle2, Bug, Zap, Layers, Rocket, Hash, X } from 'lucide-vue-next'
import { problemApi } from '../api/problem'
import { articleApi } from '../api/article'
import ProblemModal from '../components/business/projects/ProblemModal.vue'

const router = useRouter()

const problems = ref([])
const isLoading = ref(false)

const categories = {
  bug: { label: 'Bug修复', icon: Bug, color: 'indigo', lightBg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-100', bar: 'bg-indigo-600' },
  performance: { label: '性能瓶颈', icon: Zap, color: 'amber', lightBg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-100', bar: 'bg-amber-500' },
  architecture: { label: '架构设计', icon: Layers, color: 'emerald', lightBg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100', bar: 'bg-emerald-500' },
  other: { label: '其他记录', icon: Rocket, color: 'blue', lightBg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-100', bar: 'bg-blue-600' }
}

const showProblemModal = ref(false)
const selectedProblemId = ref(null)
const initialFormData = ref(null)

const loadProblems = async () => {
  isLoading.value = true
  try {
    problems.value = await problemApi.getProblems()
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// Problem actions
const openProblemModal = () => {
  selectedProblemId.value = null
  initialFormData.value = null
  showProblemModal.value = true
}

const openEditModal = (p) => {
  selectedProblemId.value = p.id
  initialFormData.value = null
  showProblemModal.value = true
}

const handleModalSuccess = () => {
  loadProblems()
}

const deleteProblem = async (id) => {
  if (!confirm('确定删除该问题吗？')) return
  await problemApi.deleteProblem(id)
  loadProblems()
}

const goToEditArticle = (id) => {
  router.push(`/articles/${id}/edit`)
}

// 问题记录 → 进入文章流转流程
const generateArticleFromProblem = (problem) => {
  router.push(`/knowledge/${problem.id}/article-flow`)
}

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}

const getStatusInfo = (p) => {
  if (p.article_id || p.knowledge_step === 4) {
    return { label: '已入库', color: 'emerald' }
  }
  if (p.knowledge_step > 1) {
    return { label: '整理中', color: 'amber', icon: true }
  }
  return { label: '待复盘', color: 'gray' }
}

const getStepText = (step) => {
  const steps = {
    1: '探索排查',
    2: '方案制定',
    3: '深度复盘',
    4: '知识升华'
  }
  return steps[step] || '知识升华'
}

const getThemeStyles = (p) => {
  const status = getStatusInfo(p)
  const cat = categories[p.category] || categories.bug
  
  if (status.color === 'emerald') {
    return {
      bar: 'bg-emerald-500',
      text: 'text-emerald-600',
      lightBg: 'bg-emerald-50',
      border: 'border-emerald-100',
      btn: 'bg-emerald-600 hover:bg-emerald-700',
      title: 'group-hover:text-emerald-600'
    }
  }
  if (status.color === 'amber') {
    return {
      bar: 'bg-amber-500',
      text: 'text-amber-600',
      lightBg: 'bg-amber-50',
      border: 'border-amber-100',
      btn: 'bg-amber-500 hover:bg-amber-600',
      title: 'group-hover:text-amber-600'
    }
  }
  
  return {
    bar: cat.bar,
    text: cat.text,
    lightBg: cat.lightBg,
    border: cat.border,
    btn: 'bg-gray-900 group-hover:bg-indigo-600',
    title: 'group-hover:text-indigo-600'
  }
}

onMounted(() => {
  loadProblems()
})
</script>

<template>
  <div class="animate-in max-w-6xl mx-auto min-h-screen pb-20">
    <header class="mb-12 flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-black text-gray-900 tracking-tight flex items-center gap-4">
          <div class="p-3 bg-indigo-600 text-white rounded-3xl shadow-xl shadow-indigo-200">
            <BookOpen class="w-8 h-8" />
          </div>
          知识沉淀库
        </h1>
        <p class="text-gray-500 mt-3 text-lg font-medium">记录遇到的问题，通过 AI 助手将其复盘、升华为高质量技术文章。</p>
      </div>
      <button @click="openProblemModal" class="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-[2rem] font-black transition-all flex items-center gap-3 shadow-xl shadow-indigo-200 transform hover:-translate-y-1 active:scale-95">
        <Plus class="w-6 h-6" />
        记录新问题
      </button>
    </header>

    <!-- Loading -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32 space-y-4">
      <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
      <p class="text-gray-400 font-bold uppercase tracking-widest text-xs">知识抽样中...</p>
    </div>

    <!-- Problems List -->
    <div v-else class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      <div v-if="problems.length === 0" class="col-span-full py-32 flex flex-col items-center justify-center text-gray-400 bg-white rounded-[4rem] border-2 border-dashed border-gray-100">
         <HelpCircle class="w-20 h-20 text-gray-100 mb-6" />
         <p class="font-black text-2xl text-gray-800 mb-2 tracking-tight">库中尚无沉淀样本</p>
         <p class="text-gray-400 font-medium text-center max-w-sm">每个技术细节都值得被挖掘。点击上方按钮，开启第一条沉淀记录。</p>
      </div>
      
      <div v-for="p in problems" :key="p.id" 
           class="group bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-sm hover:shadow-2xl hover:shadow-indigo-200/40 transition-all duration-500 flex flex-col relative overflow-hidden">
        <!-- Decoration Left Bar -->
        <div class="absolute left-0 top-0 bottom-0 w-1.5 transition-all duration-500 transform scale-y-75 group-hover:scale-y-100 origin-center"
             :class="getThemeStyles(p).bar"></div>

        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-3">
             <div class="p-2 rounded-xl" :class="getThemeStyles(p).lightBg">
                <component :is="categories[p.category]?.icon || Bug" class="w-4 h-4" :class="getThemeStyles(p).text" />
             </div>
             <div class="flex flex-col">
                <span class="text-[11px] font-black uppercase tracking-wider" :class="getThemeStyles(p).text">
                  {{ categories[p.category]?.label || '技术记录' }}
                </span>
                <span class="text-[9px] text-gray-300 font-bold">{{ new Date(p.created_at).toLocaleDateString() }}</span>
             </div>
          </div>
          
          <div class="flex items-center gap-2">
            <button @click="openEditModal(p)" class="text-gray-200 hover:text-indigo-500 opacity-0 group-hover:opacity-100 transition-all p-2 hover:bg-indigo-50 rounded-xl">
              <Edit class="w-4 h-4" />
            </button>
            <button @click="deleteProblem(p.id)" class="text-gray-200 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all p-2 hover:bg-red-50 rounded-xl">
              <Trash2 class="w-4 h-4" />
            </button>
            <div class="px-3 py-1.5 rounded-xl text-[10px] font-black tracking-tight flex items-center gap-1.5"
                 :class="getStatusInfo(p).color === 'emerald' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 
                        getStatusInfo(p).color === 'amber' ? 'bg-amber-50 text-amber-600 border border-amber-100' : 
                        'bg-gray-50 text-gray-400 border border-gray-200'">
              <span v-if="getStatusInfo(p).icon" class="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>
              <Hash v-if="getStatusInfo(p).color === 'amber'" class="w-3 h-3" />
              <CheckCircle2 v-if="getStatusInfo(p).color === 'emerald'" class="w-3 h-3" />
              {{ getStatusInfo(p).label }}
            </div>
          </div>
        </div>
        
        <h3 class="font-black text-gray-900 text-xl mb-4 pr-8 leading-tight transition-colors line-clamp-2 min-h-[3.5rem]"
            :class="getThemeStyles(p).title">{{ p.title }}</h3>
        
        <!-- Description Card -->
        <div class="bg-gray-50/50 rounded-2xl p-4 mb-6 border border-gray-100/50 group-hover:bg-white transition-colors">
          <p class="text-[13px] text-gray-500 font-medium line-clamp-3 leading-relaxed italic">
            "{{ p.description || '暂无详细描述信息...' }}"
          </p>
        </div>

        <div class="flex flex-wrap gap-2 mb-8">
          <span v-for="tag in formatTags(p.tags)" :key="tag" 
                class="px-3 py-1 bg-white border border-indigo-100 text-indigo-600 text-[10px] font-black rounded-lg shadow-sm">
            # {{ tag }}
          </span>
          <span v-if="!p.tags" class="text-[10px] text-gray-200 font-bold uppercase tracking-widest"># 无内置标签</span>
        </div>
        
        <div class="mt-auto pt-6 border-t border-gray-50 flex items-center justify-between">
          <div class="flex flex-col w-full max-w-[140px]">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Progress</span>
              <span class="text-[10px] font-bold text-gray-400">{{ p.knowledge_step }}/4 ({{ getStepText(p.knowledge_step) }})</span>
            </div>
            <div class="flex gap-1.5 overflow-hidden">
               <div v-for="i in 4" :key="i" 
                    class="h-1.5 flex-1 rounded-full transition-all duration-700"
                    :class="p.article_id || p.knowledge_step >= i ? getThemeStyles(p).bar : 'bg-gray-100'"></div>
            </div>
          </div>
          
          <button v-if="p.article_id" @click="goToEditArticle(p.article_id)" 
                  class="bg-emerald-50 hover:bg-emerald-600 text-emerald-600 hover:text-white px-6 py-3 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all shadow-sm flex items-center gap-2 transform active:scale-95 group/btn">
            查看文章 <FileText class="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
          </button>
          <button v-else @click="generateArticleFromProblem(p)" 
                  class="text-white px-6 py-3 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all shadow-xl shadow-gray-200 flex items-center gap-2 transform active:scale-95 group/btn"
                  :class="getThemeStyles(p).btn">
            {{ p.knowledge_step > 1 ? '继续整理' : '开始整理' }} <Edit class="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
          </button>
        </div>
        
      </div>
    </div>

    <!-- Problem Modal -->
    <ProblemModal 
      :show="showProblemModal"
      :problemId="selectedProblemId"
      :initialData="initialFormData"
      @close="showProblemModal = false"
      @success="handleModalSuccess"
    />
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
