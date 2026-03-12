<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ChevronLeft, Sparkles, Send, HelpCircle, FileText, 
  CheckCircle2, Search, Zap, BookOpen, Save, Eye, SendHorizonal, 
  MoreHorizontal, Terminal, History, Lightbulb
} from 'lucide-vue-next'
import { problemApi } from '../api/problem'
import { articleApi } from '../api/article'

const route = useRoute()
const router = useRouter()
const problemId = route.params.id

// 基础数据
const problem = ref(null)
const isLoading = ref(true)
const currentStep = ref(1)
const lastSaved = ref(new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }))

// 表单数据
const formData = ref({
  scene: {
    original_problem: '',
    error_info: '',
    background: ''
  },
  investigation: {
    path: '',
    clues: ''
  },
  solution: {
    core_fix: '',
    code_snippet: ''
  },
  sublimation: {
    takeaways: '',
    prevention: ''
  }
})

// AI Copilot 状态
const chatMessages = ref([
  { 
    role: 'assistant', 
    content: '你好！我是你的知识沉淀助手。我看你正在整理技术问题。告诉我你在哪一步遇到了困难，或者直接点【分析】让我帮你梳理。' 
  }
])
const userInput = ref('')
const isAiTyping = ref(false)
const chatContainer = ref(null)

const steps = [
  { id: 1, title: '还原案发现场', subtitle: '描述背景与报错', icon: History },
  { id: 2, title: '探索式排查', subtitle: '记录排查路径', icon: Search },
  { id: 3, title: '解决方案提炼', subtitle: '核心方案代码', icon: Zap },
  { id: 4, title: '知识升华', subtitle: '总结与升华', icon: BookOpen }
]

// 加载初始数据
const loadProblem = async () => {
  try {
    const data = await problemApi.getProblem(problemId)
    problem.value = data
    formData.value.scene.original_problem = data.title
    formData.value.scene.background = data.description || ''
    if (data.knowledge_step) {
      currentStep.value = data.knowledge_step
    }
  } catch (error) {
    console.error('Failed to load problem', error)
  } finally {
    isLoading.value = false
  }
}

// 自动保存逻辑
watch(formData, () => {
  // 模拟自动保存
  lastSaved.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}, { deep: true })

// AI 对话逻辑
const sendToAi = async (customInput = null) => {
  const input = customInput || userInput.value
  if (!input.trim() && !customInput) return

  if (!customInput) {
    chatMessages.value.push({ role: 'user', content: input })
    userInput.value = ''
  }

  isAiTyping.value = true
  scrollToBottom()

  try {
    const context = {
        current_step: steps[currentStep.value - 1].title,
        data: formData.value
    }
    const response = await problemApi.aiAssist(problemId, {
      step: currentStep.value,
      context: context,
      user_input: input
    })
    
    chatMessages.value.push({ 
      role: 'assistant', 
      content: response.reply 
    })
  } catch (error) {
    chatMessages.value.push({ 
      role: 'assistant', 
      content: '抱歉，AI 助手暂时遇到了点问题。' 
    })
  } finally {
    isAiTyping.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 步骤控制
const nextStep = async () => {
  if (currentStep.value < 4) {
    currentStep.value++
    await syncStep()
  } else {
    publishArticle()
  }
}

const prevStep = async () => {
  if (currentStep.value > 1) {
    currentStep.value--
    await syncStep()
  }
}

const syncStep = async () => {
  try {
    await problemApi.updateProblem(problemId, { knowledge_step: currentStep.value })
  } catch (error) {
    console.error('Failed to sync step', error)
  }
}

// 发布文章
const publishArticle = async () => {
  try {
    // 构造最终的 Markdown 内容
    let content = `# ${problem.value?.title || '无标题文章'}\n\n`
    
    content += `## 1. 还原案发现场\n\n`
    content += `**业务背景**：\n${formData.value.scene.background || '未填写'}\n\n`
    content += `**报错信息**：\n\`\`\`\n${formData.value.scene.error_info || '无'}\n\`\`\`\n\n`
    
    content += `## 2. 探索式排查\n\n`
    content += `**排查路径**：\n${formData.value.investigation.path || '未填写'}\n\n`
    content += `**关键线索**：\n${formData.value.investigation.clues || '无'}\n\n`
    
    content += `## 3. 解决方案提炼\n\n`
    content += `**核心修复方案**：\n${formData.value.solution.core_fix || '未填写'}\n\n`
    if (formData.value.solution.code_snippet) {
      content += `**修复代码**：\n\`\`\`\n${formData.value.solution.code_snippet}\n\`\`\`\n\n`
    }
    
    content += `## 4. 知识升华\n\n`
    content += `**复盘心得**：\n${formData.value.sublimation.takeaways || '未填写'}\n\n`
    content += `**预防措施**：\n${formData.value.sublimation.prevention || '未填写'}\n`

    const article = await problemApi.generateArticle(problemId, { content })
    const articleId = article.id || (article.data && article.data.id)
    if (articleId) {
      router.push(`/articles/${articleId}/edit`)
    }
  } catch (error) {
    console.error('Failed to generate article', error)
  }
}

onMounted(() => {
  loadProblem()
})
</script>

<template>
  <div class="fixed inset-0 bg-slate-50 flex flex-col font-sans text-slate-900 overflow-hidden">
    <!-- Header -->
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 relative z-20">
      <div class="flex items-center gap-4">
        <button @click="router.back()" class="p-2 hover:bg-slate-100 rounded-full transition-colors">
          <ChevronLeft class="w-5 h-5 text-slate-500" />
        </button>
        <div class="flex items-center gap-2">
          <span class="text-indigo-600 font-bold">撰写技术文章</span>
          <span class="text-slate-300">/</span>
          <span class="text-slate-500 font-medium truncate max-w-[300px]">{{ problem?.title || '正在加载...' }}</span>
        </div>
      </div>

      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2 text-slate-400 text-sm">
          <span class="inline-block w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
          自动保存于 {{ lastSaved }}
        </div>
        <div class="flex items-center gap-2">
          <button class="flex items-center gap-2 px-4 py-2 text-slate-600 font-bold hover:bg-slate-100 rounded-xl transition-all">
            <Eye class="w-4 h-4" /> 预览文档
          </button>
          <button @click="publishArticle" class="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 shadow-md shadow-indigo-200 transition-all">
            完成并发布
          </button>
        </div>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <!-- Main Content Area -->
      <main class="flex-1 overflow-y-auto custom-scrollbar relative">
        <!-- Stepper -->
        <div class="max-w-4xl mx-auto pt-10 pb-20 px-10">
          <div class="flex justify-between mb-16 relative">
            <!-- Background Line -->
            <div class="absolute top-6 left-0 right-0 h-0.5 bg-slate-200 -z-10"></div>
            
            <div v-for="step in steps" :key="step.id" 
                 class="flex flex-col items-center gap-3 group">
              <div 
                class="w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 shadow-sm"
                :class="currentStep >= step.id ? 'bg-indigo-600 border-indigo-600 text-white ring-4 ring-indigo-50' : 'bg-white border-slate-200 text-slate-400'"
              >
                <component :is="step.icon" class="w-5 h-5" />
              </div>
              <div class="text-center">
                <div class="text-sm font-black" :class="currentStep >= step.id ? 'text-indigo-600' : 'text-slate-400'">{{ step.title }}</div>
                <div class="text-[10px] text-slate-400 font-medium hidden md:block">{{ step.subtitle }}</div>
              </div>
            </div>
          </div>

          <!-- Step Content Container -->
          <div class="bg-white rounded-[2.5rem] p-12 shadow-xl shadow-slate-200/50 border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <!-- Step 1: 还原案发现场 -->
            <div v-if="currentStep === 1" class="space-y-10">
              <div class="space-y-2">
                <h2 class="text-3xl font-black text-slate-800 flex items-center gap-3">
                  <History class="w-8 h-8 text-indigo-500" />
                  还原案发现场
                </h2>
                <p class="text-slate-500">描述业务背景和具体报错现象。</p>
              </div>

              <div class="flex gap-2">
                <button @click="sendToAi('请帮我分析报错日志')" class="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-50 text-indigo-600 rounded-full text-xs font-bold hover:bg-indigo-100 transition-colors">
                  <Sparkles class="w-3.5 h-3.5" /> 分析报错日志
                </button>
                <button @click="sendToAi('如何描述业务背景更好？')" class="flex items-center gap-1.5 px-4 py-1.5 bg-rose-50 text-rose-600 rounded-full text-xs font-bold hover:bg-rose-100 transition-colors">
                  <Lightbulb class="w-3.5 h-3.5" /> 润色背景描述
                </button>
              </div>

              <div class="space-y-8">
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">原始问题</label>
                  <input v-model="formData.scene.original_problem" type="text" 
                         class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-4 outline-none transition-all text-slate-700 font-medium"
                         placeholder="如：移除反思日记导航栏时导致死循环">
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1 flex items-center gap-2">
                    <Terminal class="w-4 h-4" /> 报错信息
                  </label>
                  <textarea v-model="formData.scene.error_info" rows="3" 
                            class="w-full bg-slate-900 border-none rounded-2xl px-6 py-5 outline-none font-mono text-indigo-300 text-sm leading-relaxed shadow-inner"
                            placeholder="粘贴控制台报错内容..."></textarea>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">业务背景</label>
                  <textarea v-model="formData.scene.background" rows="5" 
                            class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-5 outline-none transition-all text-slate-700 leading-relaxed"
                            placeholder="问题的起源和影响范围..."></textarea>
                </div>
              </div>
            </div>

            <!-- Step 2: 探索式排查 -->
            <div v-if="currentStep === 2" class="space-y-10">
              <div class="space-y-2">
                <h2 class="text-3xl font-black text-slate-800 flex items-center gap-3">
                  <Search class="w-8 h-8 text-indigo-500" />
                  探索式排查
                </h2>
                <p class="text-slate-500">记录你的排查思路和发现的关键线索。</p>
              </div>

              <div class="space-y-8">
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">排查路径</label>
                  <textarea v-model="formData.investigation.path" rows="8" 
                            class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-5 outline-none transition-all text-slate-700 leading-relaxed"
                            placeholder="第一步做了什么？第二步？观察到了什么变化？"></textarea>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">关键线索</label>
                  <input v-model="formData.investigation.clues" type="text" 
                         class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-4 outline-none transition-all text-slate-700 font-medium"
                         placeholder="哪个具体的代码行或配置点引起了你的怀疑？">
                </div>
              </div>
            </div>

            <!-- Step 3: 解决方案提炼 -->
            <div v-if="currentStep === 3" class="space-y-10">
              <div class="space-y-2">
                <h2 class="text-3xl font-black text-slate-800 flex items-center gap-3">
                  <Zap class="w-8 h-8 text-indigo-500" />
                  解决方案提炼
                </h2>
                <p class="text-slate-500">提炼核心修复方案并保存代码片段。</p>
              </div>

              <div class="space-y-8">
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">核心修复方案</label>
                  <textarea v-model="formData.solution.core_fix" rows="4" 
                            class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-5 outline-none transition-all text-slate-700 leading-relaxed"
                            placeholder="一句话概括：是如何解决这个问题的？"></textarea>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1 flex items-center gap-2">
                    <Terminal class="w-4 h-4" /> 修复代码
                  </label>
                  <textarea v-model="formData.solution.code_snippet" rows="8" 
                            class="w-full bg-slate-900 border-none rounded-2xl px-6 py-6 outline-none font-mono text-emerald-400 text-sm leading-relaxed shadow-inner"
                            placeholder="// 粘贴核心修复代码..."></textarea>
                </div>
              </div>
            </div>

            <!-- Step 4: 知识升华 -->
            <div v-if="currentStep === 4" class="space-y-10">
              <div class="space-y-2">
                <h2 class="text-3xl font-black text-slate-800 flex items-center gap-3">
                  <BookOpen class="w-8 h-8 text-indigo-500" />
                  知识升华
                </h2>
                <p class="text-slate-500">总结经验教训，防止问题再次发生。</p>
              </div>

              <div class="space-y-8">
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">复盘心得</label>
                  <textarea v-model="formData.sublimation.takeaways" rows="6" 
                            class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-5 outline-none transition-all text-slate-700 leading-relaxed"
                            placeholder="这次排查中学到了什么新的知识点？"></textarea>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-slate-800 mb-3 ml-1">预防措施</label>
                  <textarea v-model="formData.sublimation.prevention" rows="4" 
                            class="w-full bg-slate-50 border-2 border-transparent focus:border-indigo-500/20 focus:bg-white rounded-2xl px-6 py-5 outline-none transition-all text-slate-700 leading-relaxed"
                            placeholder="在工程实践中，如何避免类似问题发生？（如 ESLint 规则, 类型定义等）"></textarea>
                </div>
              </div>
            </div>

            <!-- Navigation Buttons -->
            <div class="mt-20 pt-10 border-t border-slate-100 flex items-center justify-between">
              <button 
                @click="prevStep" 
                :disabled="currentStep === 1"
                class="flex items-center gap-2 px-8 py-3 text-slate-500 font-bold hover:text-slate-800 transition-colors disabled:opacity-0"
              >
                <ArrowLeft class="w-5 h-5" /> 上一步
              </button>
              
              <button 
                @click="nextStep"
                class="flex items-center gap-2 px-10 py-4 bg-slate-900 text-white font-black rounded-2xl hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-slate-200"
              >
                {{ currentStep === 4 ? '生成完整文章' : '下一步' }}
                <ArrowRight class="w-5 h-5" v-if="currentStep < 4" />
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- AI Copilot Sidebar -->
      <aside class="w-[400px] border-l border-slate-200 bg-white flex flex-col shrink-0 relative z-10 shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.05)]">
        <div class="h-16 border-b border-slate-100 flex items-center justify-between px-6 shrink-0">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm ring-4 ring-indigo-50">
              <Sparkles class="w-4 h-4" />
            </div>
            <span class="font-black text-slate-800 tracking-tight">沉淀助手 Copilot</span>
          </div>
          <button class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-400">
            <HelpCircle class="w-5 h-5" />
          </button>
        </div>

        <!-- Chat Container -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar scroll-smooth">
          <div v-for="(msg, idx) in chatMessages" :key="idx" 
               class="flex flex-col gap-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div class="flex items-center gap-2" v-if="msg.role === 'assistant'">
              <div class="w-6 h-6 rounded bg-indigo-100 flex items-center justify-center text-indigo-600">
                <Sparkles class="w-3.5 h-3.5" />
              </div>
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Assistant</span>
            </div>
            
            <div 
              class="max-w-[85%] rounded-3xl p-4 text-sm leading-relaxed"
              :class="msg.role === 'assistant' 
                ? 'bg-slate-50 text-slate-700 self-start rounded-tl-sm' 
                : 'bg-indigo-600 text-white self-end rounded-br-sm shadow-md shadow-indigo-100'"
            >
              {{ msg.content }}
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isAiTyping" class="flex flex-col gap-2">
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded bg-indigo-100 flex items-center justify-center text-indigo-600">
                <Sparkles class="w-3.5 h-3.5" />
              </div>
            </div>
            <div class="bg-indigo-50 p-4 rounded-3xl rounded-tl-sm self-start flex gap-1 items-center">
              <span class="w-1 h-1 bg-indigo-400 rounded-full animate-bounce"></span>
              <span class="w-1 h-1 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span class="w-1 h-1 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 bg-white border-t border-slate-100">
          <div class="relative group">
            <textarea 
              v-model="userInput"
              @keydown.enter.prevent="sendToAi()"
              rows="3"
              class="w-full bg-slate-50 border border-slate-100 focus:border-indigo-500/30 focus:bg-white focus:ring-4 focus:ring-indigo-500/5 rounded-3xl px-5 py-4 text-sm outline-none transition-all resize-none pr-14"
              placeholder="告诉 AI 你在第 {{ currentStep }} 步遇到了什么困难..."
            ></textarea>
            <button 
              @click="sendToAi()"
              :disabled="!userInput.trim() || isAiTyping"
              class="absolute right-3 bottom-3 w-10 h-10 bg-indigo-600 text-white rounded-2xl flex items-center justify-center hover:scale-105 active:scale-95 transition-all shadow-lg shadow-indigo-100 disabled:opacity-30 disabled:hover:scale-100"
            >
              <SendHorizonal class="w-5 h-5" />
            </button>
          </div>
          <div class="mt-3 text-[10px] text-slate-400 text-center font-medium">
            AI 可能会生成不准确的信息，请人工核实。
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.95); }
}

.animate-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
