<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Beaker, ArrowRight, ArrowLeft, ExternalLink, Github, Sparkles, Check, MessageSquare, Box, Rocket, Globe } from 'lucide-vue-next'
import { incubationApi } from '../api/incubation'

const route = useRoute()
const router = useRouter()
const incubationId = route.params.id

const incubation = ref(null)
const isLoading = ref(true)
const currentStep = ref(1)

const steps = [
  { id: 1, title: '概念生成', description: '定义问题' },
  { id: 2, title: '痛点与竞品', description: '验证访谈' },
  { id: 3, title: '一页纸方案', description: '策划方案' },
  { id: 4, title: 'MVP 构建', description: '构建 MVP' },
  { id: 5, title: '市场反馈', description: '收集反馈' }
]

const getStepMeta = (id) => {
  const metas = {
    1: { icon: Sparkles },
    2: { icon: MessageSquare },
    3: { icon: Box },
    4: { icon: Github },
    5: { icon: Rocket }
  }
  return metas[id] || { icon: Beaker }
}

const loadIncubation = async () => {
  isLoading.value = true
  try {
    incubation.value = await incubationApi.getIncubation(incubationId)
    currentStep.value = incubation.value.current_step || 1
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const nextStep = () => {
  if (currentStep.value < 5) currentStep.value++
}

const prevStep = () => {
  if (currentStep.value > 1) currentStep.value--
}

const generatePlan = () => {
  const plan = `# ${incubation.value.title} 启动计划书\n\n` +
    `## 1. 痛点问题\n${incubation.value.problem || '未填写'}\n\n` +
    `## 2. 竞品分析\n${incubation.value.competitor_gap || '未填写'}\n\n` +
    `## 3. 核心方案\n${incubation.value.one_page_doc || '未填写'}\n\n` +
    `## 4. 验证反馈\n${incubation.value.user_feedback || '未填写'}\n`
  
  incubation.value.startup_plan_content = plan
}

const saveAndExit = async () => {
  try {
    incubation.value.current_step = currentStep.value
    await incubationApi.updateIncubation(incubationId, incubation.value)
    router.push('/incubation')
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadIncubation()
})
</script>

<template>
  <div class="h-screen bg-[#fafafa] flex flex-col overflow-hidden relative">
    <!-- Header NavBar -->
    <nav class="bg-white/90 backdrop-blur-2xl border-b border-gray-100 px-8 py-5 flex items-center justify-between fixed top-0 left-0 right-0 z-[100] shadow-sm">
      <div class="flex items-center gap-4">
        <button @click="saveAndExit" class="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-400">
          <ArrowLeft class="w-6 h-6" />
        </button>
        <div class="h-6 w-[1px] bg-gray-200"></div>
        <div>
          <h1 class="text-xl font-black text-gray-800 flex items-center gap-2">
             <Beaker class="text-amber-500 w-5 h-5" />
             {{ incubation?.title || '正在加载...' }}
          </h1>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-0.5">产品孵化向导・PROJECT INCUBATION FLOW</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
         <div class="flex items-center -space-x-2 mr-4">
            <div v-for="step in steps" :key="step.id" 
              :class="['w-8 h-8 rounded-full border-4 border-white flex items-center justify-center text-[10px] font-black transition-all z-10 shadow-sm',
              currentStep >= step.id ? 'bg-amber-500 text-white shadow-amber-200' : 'bg-gray-200 text-gray-400']">
              {{ currentStep > step.id ? '✓' : step.id }}
            </div>
         </div>
         <button @click="saveAndExit" class="px-5 py-2 bg-gray-800 text-white text-xs font-black rounded-xl hover:bg-black transition-all shadow-lg shadow-gray-200 uppercase tracking-wider">
           保存并退出
         </button>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto relative pt-28 pb-12 px-8 custom-scrollbar">
      <div v-if="isLoading" class="flex flex-col items-center justify-center h-full text-gray-400 gap-4">
        <div class="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
        <p class="font-bold text-sm tracking-widest uppercase">实验室数据提取中...</p>
      </div>

      <div v-else class="max-w-7xl mx-auto flex gap-12 items-start">
        <!-- Vertical Stepper Sidebar -->
        <aside class="w-80 sticky top-0 pt-4 space-y-10">
          <div class="space-y-6">
            <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-2 opacity-50">向导进度・INCUBATION PROGRESS</h3>
            
            <div class="relative pl-4 space-y-12">
              <!-- Vertical Line Progress (Background) -->
              <div class="absolute left-[23px] top-6 bottom-6 w-[2px] bg-gray-100 rounded-full"></div>
              
              <!-- Vertical Line Progress (Active) -->
              <div class="absolute left-[23px] top-6 w-[2px] bg-gradient-to-b from-amber-400 to-amber-600 transition-all duration-1000 ease-out rounded-full shadow-[0_0_15px_rgba(245,158,11,0.3)]" 
                   :style="{ height: `calc(${(currentStep - 1) * 25}%)` }"></div>

              <div v-for="step in steps" :key="step.id" 
                @click="currentStep <= incubation.current_step + 1 || step.id <= incubation.current_step ? currentStep = step.id : null"
                :class="['relative group flex items-center gap-6 cursor-pointer transition-all duration-500 ease-out py-1 px-2', 
                currentStep === step.id ? 'scale-105 opacity-100' : 'opacity-40 hover:opacity-100']">
                
                <!-- Active Indicator Background (Moved to front for proper layering) -->
                <div v-if="currentStep === step.id" class="absolute inset-x-0 inset-y-0 bg-amber-500/[0.04] rounded-2xl border border-amber-500/10 -z-10 shadow-inner"></div>

                <!-- Step Node -->
                <div :class="['w-12 h-12 rounded-2xl border-4 border-white flex items-center justify-center z-10 transition-all duration-500 shadow-xl relative',
                  currentStep === step.id ? 'bg-amber-500 shadow-amber-200 rotate-6' : 
                  (currentStep > step.id ? 'bg-amber-600 shadow-amber-100' : 'bg-white text-gray-300')]">
                  
                  <component :is="getStepMeta(step.id).icon" 
                    :class="['w-5 h-5 transition-transform duration-500', 
                    currentStep >= step.id ? 'text-white' : 'text-gray-300 group-hover:scale-110']" />
                    
                  <!-- Checkmark for completed -->
                  <div v-if="currentStep > step.id" class="absolute -right-1 -top-1 w-5 h-5 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
                    <Check class="w-2.5 h-2.5 text-white stroke-[4px]" />
                  </div>
                </div>

                <!-- Labels -->
                <div class="space-y-1 flex-1 relative z-10 transition-all duration-500" :class="{ 'translate-x-1': currentStep === step.id }">
                  <div class="flex items-center gap-2">
                    <p :class="['text-sm font-black tracking-tight leading-none', currentStep === step.id ? 'text-gray-900' : 'text-gray-400']">
                      {{ step.title }}
                    </p>
                    <span v-if="currentStep === step.id" class="px-2 py-0.5 bg-amber-100 text-amber-600 text-[8px] font-black rounded-full uppercase tracking-tighter animate-pulse">Running</span>
                  </div>
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-none">{{ step.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Laboratory Tip Box -->
          <div class="bg-gradient-to-br from-white to-amber-50/30 rounded-[2.5rem] p-8 border border-amber-100/50 shadow-sm relative overflow-hidden group">
            <div class="absolute -top-12 -right-12 w-32 h-32 bg-amber-500/5 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-1000"></div>
            <div class="flex items-center gap-4 mb-4">
              <div class="w-10 h-10 bg-amber-500 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-amber-200">
                <Beaker class="w-5 h-5" />
              </div>
              <span class="text-xs font-black text-amber-800 uppercase tracking-[0.2em]">LAB INSIGHTS</span>
            </div>
            <p class="text-xs text-amber-700/70 font-bold leading-relaxed">
              {{ steps[currentStep-1].description }}阶段是确保 Idea 落地成真实产品的关键。在这里记录的每一行文字都将成为后续计划书的灵魂。
            </p>
          </div>
        </aside>

        <!-- Step UI Content Card -->
        <div class="flex-1 bg-white rounded-[3rem] shadow-2xl shadow-gray-200/50 p-12 border border-gray-100 min-h-[650px] flex flex-col overflow-hidden relative">
          
          <!-- Background Decoration -->
          <div class="absolute -top-24 -right-24 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl text-xs"></div>
          <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl text-xs"></div>

          <!-- Content Wrapper -->
          <div class="relative z-10 flex-1">
             <div v-if="currentStep === 1" class="animate-in slide-in-from-right-4 duration-500 space-y-10">
                <div class="space-y-3">
                  <div class="w-12 h-12 bg-amber-500 text-white rounded-3xl flex items-center justify-center shadow-lg shadow-amber-200">
                    <Sparkles class="w-6 h-6" />
                  </div>
                  <h2 class="text-4xl font-black text-gray-800 tracking-tight">确立价值锚点</h2>
                  <p class="text-gray-400 text-lg">深入挖掘用户痛点，寻找市场空白。逻辑是孵化的第一步。</p>
                </div>

                <div class="grid gap-8">
                   <div class="group">
                      <label class="block text-sm font-black text-gray-800 mb-3 ml-2 flex items-center gap-2">
                        问题真实性访谈 (PROBLEM)
                        <span class="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                      </label>
                      <textarea v-model="incubation.problem" rows="5" class="w-full bg-gray-50/50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] p-8 outline-none transition-all text-gray-700 text-lg leading-relaxed shadow-inner" placeholder="这个需求真的是痛点吗？用户现在是如何忍受它的？"></textarea>
                   </div>
                   <div class="group">
                      <label class="block text-sm font-black text-gray-800 mb-3 ml-2">竞品生命缝隙 (COMPETITOR GAP)</label>
                      <textarea v-model="incubation.competitor_gap" rows="5" class="w-full bg-gray-50/50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] p-8 outline-none transition-all text-gray-700 text-lg leading-relaxed shadow-inner" placeholder="现有产品（如微信、Notion等）为什么没能解决好？"></textarea>
                   </div>
                </div>
             </div>

             <div v-else-if="currentStep === 2" class="animate-in slide-in-from-right-4 duration-500 space-y-10">
                <div class="space-y-4">
                  <div class="w-12 h-12 bg-amber-500 text-white rounded-3xl flex items-center justify-center shadow-lg shadow-amber-200">
                    <MessageSquare class="w-6 h-6" />
                  </div>
                  <h2 class="text-4xl font-black text-gray-800 tracking-tight tracking-tight">痛点与竞品确认</h2>
                  <p class="text-gray-400 text-lg">基于访谈数据，确认我们的切入点是否足够锋利。</p>
                </div>
                <div class="bg-gray-50 p-8 rounded-[2rem] border border-gray-100">
                  <p class="text-gray-500 text-sm font-medium leading-relaxed">
                    此步骤会自动同步您在“头脑风暴”阶段的初始想法。请在这里进行深度的“Pest 验证”。
                  </p>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-gray-800 mb-3 ml-2">核心洞察 (INSIGHTS)</label>
                  <textarea v-model="incubation.insights_summary" rows="8" class="w-full bg-gray-50/50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] p-8 outline-none transition-all text-gray-700 text-lg leading-relaxed shadow-inner" placeholder="总结前期的调研。我们发现了什么别人没发现的？"></textarea>
                </div>
             </div>

             <div v-else-if="currentStep === 3" class="animate-in slide-in-from-right-4 duration-500 space-y-10">
                <div class="space-y-3">
                  <div class="w-12 h-12 bg-amber-500 text-white rounded-3xl flex items-center justify-center shadow-lg shadow-amber-200">
                    <Box class="w-6 h-6" />
                  </div>
                  <h2 class="text-4xl font-black text-gray-800 tracking-tight tracking-tight">一页纸方案</h2>
                  <p class="text-gray-400 text-lg">简洁地描述你的解决方案。不要写代码，写价值。</p>
                </div>
                <div class="space-y-8">
                  <div class="group">
                    <label class="block text-sm font-black text-gray-800 mb-3 ml-2">IDEA 命名</label>
                    <input v-model="incubation.title" type="text" class="w-full bg-gray-50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-2xl px-8 py-5 outline-none transition-all font-bold text-2xl text-gray-800">
                  </div>
                  <div class="group">
                    <label class="block text-sm font-black text-gray-800 mb-3 ml-2">核心解决方案 (VALUE PROP)</label>
                    <textarea v-model="incubation.one_page_doc" rows="8" class="w-full bg-gray-50/50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] p-8 outline-none transition-all text-gray-700 text-lg leading-relaxed shadow-inner" placeholder="三句话描述：它是谁、由于什么、所以能做什么。"></textarea>
                  </div>
                </div>
             </div>

             <div v-else-if="currentStep === 4" class="animate-in slide-in-from-right-4 duration-500 space-y-10">
                <div class="space-y-3">
                  <div class="w-12 h-12 bg-amber-500 text-white rounded-3xl flex items-center justify-center shadow-lg shadow-amber-200">
                    <Github class="w-6 h-6" />
                  </div>
                  <h2 class="text-4xl font-black text-gray-800 tracking-tight tracking-tight">MVP 构建与验证</h2>
                  <p class="text-gray-400 text-lg">实操环节。管理开发进度与交付链接。</p>
                </div>
                <div class="grid md:grid-cols-2 gap-8">
                  <div class="group">
                    <label class="block text-sm font-black text-gray-800 mb-3 ml-2">源码仓库 (REPO)</label>
                    <input v-model="incubation.repo_url" type="text" class="w-full bg-gray-50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-2xl px-8 py-5 outline-none transition-all font-bold text-gray-800" placeholder="https://github.com/...">
                  </div>
                  <div class="group">
                    <label class="block text-sm font-black text-gray-800 mb-3 ml-2">演示地址 (DEMO)</label>
                    <input v-model="incubation.demo_url" type="text" class="w-full bg-gray-50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-2xl px-8 py-5 outline-none transition-all font-bold text-gray-800" placeholder="https://demo.example.com">
                  </div>
                </div>
                <div class="group">
                  <label class="block text-sm font-black text-gray-800 mb-3 ml-2">MVP 完成情况备注</label>
                  <textarea v-model="incubation.user_feedback" rows="4" class="w-full bg-gray-50/50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] p-8 outline-none transition-all text-gray-700 text-lg leading-relaxed shadow-inner" placeholder="目前的 MVP 实现了哪些核心功能？"></textarea>
                </div>
             </div>

             <div v-else-if="currentStep === 5" class="animate-in slide-in-from-right-4 duration-500 space-y-10">
                <div class="text-center space-y-4 py-8">
                   <h2 class="text-5xl font-black text-gray-800">市场反馈与立项</h2>
                   <p class="text-gray-400">所有验证已完成，点击下方按钮生成您的最终立项计划书。</p>
                </div>
                <div class="grid md:grid-cols-2 gap-8">
                   <button @click="generatePlan" class="p-12 bg-amber-500 text-white rounded-[3rem] shadow-2xl shadow-amber-200 hover:scale-[1.02] transition-transform flex flex-col items-center justify-center gap-4 group">
                      <Sparkles class="w-12 h-12 group-hover:rotate-12 transition-transform" />
                      <span class="text-2xl font-black">生成启动计划书</span>
                   </button>
                   <div class="bg-gray-900 rounded-[3rem] p-10 font-mono text-xs text-amber-500 overflow-y-auto h-[400px] shadow-2xl border border-gray-800 custom-scrollbar">
                      <pre class="whitespace-pre-wrap">{{ incubation.startup_plan_content || '等待生成...' }}</pre>
                   </div>
                </div>
             </div>
          </div>

          <!-- Footer Navigation inside Page Container -->
          <div class="mt-12 pt-8 border-t border-gray-100 flex items-center justify-between">
            <button @click="prevStep" :disabled="currentStep === 1" class="px-8 py-4 text-gray-400 font-bold hover:text-gray-800 disabled:opacity-0 transition-all flex items-center gap-2 uppercase tracking-widest text-xs">
              <ArrowLeft class="w-5 h-5" /> OVERVIEW
            </button>
            
            <div class="flex items-center gap-4">
               <button v-if="currentStep < 5" @click="nextStep" class="px-12 py-5 bg-amber-500 text-white font-black rounded-3xl hover:bg-amber-600 transition-all flex items-center gap-3 shadow-xl shadow-amber-200 transform hover:-translate-y-1 uppercase tracking-widest text-xs">
                 NEXT FLOW <ArrowRight class="w-6 h-6" />
               </button>
               <button v-else @click="saveAndExit" class="px-12 py-5 bg-black text-white font-black rounded-3xl hover:bg-gray-900 transition-all flex items-center gap-3 shadow-xl shadow-gray-400 transform hover:-translate-y-1 uppercase tracking-widest text-xs">
                 COMPLETE & DEPLOY <Beaker class="w-6 h-6" />
               </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.animate-in {
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>
