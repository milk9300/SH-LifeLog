<script setup>
import { ref, onMounted, computed } from 'vue'
import { Beaker, Plus, ExternalLink, ArrowRight, Trash2, Github, Lightbulb, Sparkles, MessageSquare, Box, BarChart3, MoreVertical, AlertCircle, Clock, Check, Rocket } from 'lucide-vue-next'
import { incubationApi } from '../api/incubation'
import { useRouter } from 'vue-router'

const router = useRouter()
const incubations = ref([])
const isLoading = ref(true)

const loadIncubations = async () => {
  isLoading.value = true
  try {
    incubations.value = await incubationApi.getIncubations()
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// "Generate Idea" Logic
const showCreateModal = ref(false)
const newIdeaTitle = ref('')

const quickCreateIdea = async () => {
  if (!newIdeaTitle.value.trim()) return
  try {
    const res = await incubationApi.createIncubation({
      title: newIdeaTitle.value.trim(),
      current_step: 1,
      mvp_status: 'planning',
      result: 'experiment'
    })
    showCreateModal.value = false
    newIdeaTitle.value = ''
    // Directly navigate to the flow page after creation
    router.push(`/incubation/${res.id}/flow`)
  } catch (error) {
    console.error(error)
  }
}

const deleteIncubation = async (id) => {
  if (!confirm('确定删除此想法吗？')) return
  await incubationApi.deleteIncubation(id)
  loadIncubations()
}

const steps = [
  { id: 1, label: '概念生成', icon: Sparkles },
  { id: 2, label: '痛点与竞品', icon: MessageSquare },
  { id: 3, label: '一页纸方案', icon: Box },
  { id: 4, label: 'MVP 构建', icon: Github },
  { id: 5, label: '市场反馈', icon: Rocket }
]

const getStepStatusClass = (currentStep, stepId) => {
  if (currentStep > stepId) return 'bg-amber-500 text-white border-amber-500' // Completed
  if (currentStep === stepId) return 'bg-white text-amber-500 border-amber-500 ring-4 ring-amber-500/10' // Active
  return 'bg-gray-50 text-gray-300 border-gray-100' // Pending
}

const calculateDaysInStage = (updatedAt) => {
  const diff = new Date() - new Date(updatedAt)
  return Math.floor(diff / (1000 * 60 * 60 * 24)) || 1
}

onMounted(() => {
  loadIncubations()
})
</script>

<template>
  <div class="animate-in max-w-6xl mx-auto min-h-screen pb-20">
    <header class="mb-12 flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-black text-gray-900 tracking-tight flex items-center gap-4">
          <div class="p-3 bg-amber-500 text-white rounded-3xl shadow-xl shadow-amber-200">
            <Beaker class="w-8 h-8" />
          </div>
          产品验证实验室
        </h1>
        <p class="text-gray-500 mt-3 text-lg font-medium">通过五步法验证 Idea，沉淀每一个可能改变世界的种子。</p>
      </div>
      <button @click="showCreateModal = true" class="bg-amber-500 hover:bg-amber-600 text-white px-8 py-4 rounded-[2rem] font-black transition-all flex items-center gap-3 shadow-xl shadow-amber-200 transform hover:-translate-y-1 active:scale-95">
        <Plus class="w-6 h-6" />
        快捷生成想法
      </button>
    </header>

    <!-- Empty State -->
    <div v-if="!isLoading && incubations.length === 0" class="py-32 flex flex-col items-center justify-center text-gray-400 bg-white rounded-[4rem] border-2 border-dashed border-gray-100">
      <div class="p-10 bg-gray-50 rounded-full mb-6">
        <Lightbulb class="w-20 h-20 text-gray-200" />
      </div>
      <p class="font-black text-2xl text-gray-800 mb-2 tracking-tight">实验室中还没有灵感样本</p>
      <p class="text-gray-400 font-medium max-w-sm text-center">每个伟大的产品都始于一瞬的闪念。点击上方按钮，开始你的孵化之旅。</p>
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoading" class="flex flex-col items-center justify-center py-32 space-y-4">
      <div class="w-12 h-12 border-4 border-amber-100 border-t-amber-500 rounded-full animate-spin"></div>
      <p class="text-gray-400 font-bold uppercase tracking-widest text-xs">Idea 样本提取中...</p>
    </div>

    <!-- Idea List (Mockup Design) -->
    <div v-else class="space-y-8">
      <div v-for="item in incubations" :key="item.id" class="group bg-white rounded-[2.5rem] border border-gray-100 shadow-sm hover:shadow-2xl hover:shadow-gray-200/50 transition-all duration-500 overflow-hidden relative">
        <!-- Decoration Left Bar -->
        <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-amber-500 transform scale-y-75 group-hover:scale-y-100 transition-transform origin-center"></div>

        <div class="p-10 space-y-10">
          <!-- Title & Meta -->
          <div class="flex items-start justify-between">
            <div class="space-y-4 flex-1 pr-12">
              <div class="flex items-center gap-3">
                <span class="text-xs font-black px-3 py-1 bg-gray-100 text-gray-400 rounded-lg uppercase tracking-wider">#{{ item.id }}</span>
                <h2 class="text-2xl font-black text-gray-900 tracking-tight leading-tight group-hover:text-amber-600 transition-colors">{{ item.title }}</h2>
                <span :class="[
                  'text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-tighter transition-all',
                  item.result === 'project' ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'
                ]">
                  {{ item.result === 'project' ? '已立项 (Project)' : '验证中 (Experiment)' }}
                </span>
              </div>
              <p class="text-gray-400 font-medium line-clamp-2 leading-relaxed text-sm">{{ item.one_page_doc || '目前仅有一个初步蓝图，等待通过向导进行细节补充与验证。' }}</p>
              
              <div class="flex items-center gap-4 pt-2">
                <div class="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-100">
                  <span class="text-[10px] font-black text-gray-400 uppercase">MVP Status:</span>
                  <span class="text-xs font-bold text-gray-700 capitalize">{{ item.mvp_status }}</span>
                </div>
                <!-- Optional: Tags from Brainstorm if applicable -->
              </div>
            </div>
            
            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
               <button @click="deleteIncubation(item.id)" class="p-3 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-2xl transition-all">
                  <Trash2 class="w-5 h-5" />
               </button>
               <button class="p-3 text-gray-300 hover:text-gray-800 hover:bg-gray-100 rounded-2xl transition-all">
                  <MoreVertical class="w-5 h-5" />
               </button>
            </div>
          </div>

          <!-- Stepper UI (Fixed and Enhanced) -->
          <div class="relative py-8 px-4">
             <!-- Static Background Line -->
             <div class="absolute top-[3.75rem] left-16 right-16 h-1 bg-gray-50 rounded-full"></div>
             <!-- Active Progress Line -->
             <div class="absolute top-[3.75rem] left-16 h-1 bg-amber-500 transition-all duration-1000 rounded-full shadow-[0_0_10px_rgba(245,158,11,0.2)]" :style="{ width: `calc(${Math.min((item.current_step - 1) / 4 * 100, 100)}% - 8px)` }"></div>

             <div class="flex justify-between relative">
                <div v-for="step in steps" :key="step.id" class="flex flex-col items-center gap-4 group/step z-10">
                  <div :class="[
                    'w-14 h-14 rounded-2xl border-4 flex items-center justify-center transition-all duration-500 shadow-sm relative',
                    getStepStatusClass(item.current_step, step.id)
                  ]">
                    <component :is="step.icon" :class="[
                      'w-6 h-6 transition-colors', 
                      item.current_step > step.id ? 'text-white' : (item.current_step === step.id ? 'text-amber-500' : 'text-gray-300')
                    ]" />
                    
                    <!-- Checkmark for completed steps -->
                    <div v-if="item.current_step > step.id" class="absolute -right-2 -top-2 w-6 h-6 bg-green-500 rounded-full border-4 border-white flex items-center justify-center shadow-lg">
                      <Check class="w-2.5 h-2.5 text-white stroke-[4px]" />
                    </div>
                  </div>
                  <div class="flex flex-col items-center gap-1">
                    <span :class="[
                      'text-[11px] font-black tracking-tight transition-colors whitespace-nowrap uppercase',
                      item.current_step >= step.id ? 'text-gray-900' : 'text-gray-300'
                    ]">{{ step.label }}</span>
                  </div>
                </div>
             </div>
          </div>

          <!-- Current Task Alert (From Mockup) -->
          <div :class="[
            'p-8 rounded-[2rem] flex items-center justify-between transition-all duration-500',
            item.result === 'project' ? 'bg-green-50 border border-green-100/50' : 'bg-amber-50 border border-amber-100/50 shadow-sm shadow-amber-500/5'
          ]">
            <div class="flex gap-6 items-center">
               <div :class="[
                 'w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg',
                 item.result === 'project' ? 'bg-green-500 text-white shadow-green-200' : 'bg-white text-amber-500'
               ]">
                  <AlertCircle v-if="item.result !== 'project'" class="w-7 h-7" />
                  <Sparkles v-else class="w-7 h-7" />
               </div>
               <div class="space-y-1">
                  <h4 class="text-lg font-black text-gray-800 tracking-tight">
                    当前任务: <span class="capitalize">{{ steps.find(s => s.id === item.current_step)?.label || '已完成' }}</span>
                  </h4>
                  <p class="text-sm text-gray-500 font-medium">
                    {{ item.current_step < 5 ? '点击进入实验详情，完善下一步所需的验证数据。' : '验证已过半，是时候生成启动计划书了。' }}
                  </p>
               </div>
            </div>
            <router-link :to="`/incubation/${item.id}/flow`" class="bg-gray-900 group-hover:bg-amber-500 text-white px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-xl shadow-gray-200 flex items-center gap-3">
              进入实验详情 <ArrowRight class="w-4 h-4" />
            </router-link>
          </div>

          <!-- Footer Metadata -->
          <div class="flex items-center justify-between text-[11px] font-bold uppercase tracking-widest text-gray-400">
             <div class="flex items-center gap-2">
                <Clock class="w-4 h-4" />
                停留在本阶段 {{ calculateDaysInStage(item.created_at) }} 天
             </div>
             <div class="flex items-center gap-6">
                <a v-if="item.repo_url" :href="item.repo_url" target="_blank" class="hover:text-gray-800 transition-colors flex items-center gap-2">
                  <Github class="w-4 h-4" /> 源码存储库
                </a>
                <a v-if="item.demo_url" :href="item.demo_url" target="_blank" class="hover:text-gray-800 transition-colors flex items-center gap-2 text-amber-500">
                  <ExternalLink class="w-4 h-4" /> 访问实时 DEMO
                </a>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Idea Modal (Simplified) -->
    <div v-if="showCreateModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
      <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-xl animate-in fade-in" @click="showCreateModal = false"></div>
      <div class="bg-white rounded-[3rem] p-12 shadow-2xl w-full max-w-xl relative animate-in zoom-in duration-300">
        <div class="space-y-8">
          <div class="text-center space-y-3">
            <div class="w-20 h-20 bg-amber-500 text-white rounded-[2.5rem] flex items-center justify-center mx-auto shadow-2xl shadow-amber-200">
              <Lightbulb class="w-10 h-10" />
            </div>
            <h3 class="text-3xl font-black text-gray-900 tracking-tight">捕捉新的闪念</h3>
            <p class="text-gray-400 font-medium">暂时只需要一个标题，随后我们将引导你完成孵化。</p>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-black text-gray-400 uppercase tracking-widest ml-4">Idea 名称</label>
            <input 
              v-model="newIdeaTitle" 
              @keyup.enter="quickCreateIdea"
              type="text" 
              placeholder="例如：基于 AI 的全自动化翻译插件..." 
              class="w-full bg-gray-50 border-2 border-transparent focus:border-amber-500/20 focus:bg-white rounded-[2rem] px-8 py-6 outline-none transition-all font-bold text-xl text-gray-800 shadow-inner"
              autofocus
            >
          </div>

          <div class="flex gap-4">
            <button @click="showCreateModal = false" class="flex-1 py-5 text-gray-400 font-black rounded-3xl hover:bg-gray-50 transition-all uppercase tracking-widest text-xs">先存起来</button>
            <button @click="quickCreateIdea" :disabled="!newIdeaTitle.trim()" class="flex-[1.5] py-5 bg-amber-500 text-white font-black rounded-3xl hover:bg-amber-600 transition-all shadow-2xl shadow-amber-200 disabled:opacity-50 uppercase tracking-widest text-xs transform active:scale-95">开始孵化实验</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: slideTop 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideTop {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
