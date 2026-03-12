<script setup>
import { ref, onMounted, watch } from 'vue'
import { Skull, Lightbulb, Clock } from 'lucide-vue-next'
import { useProjectStore } from '../../../stores/project'
import { graveyardApi } from '../../../api/graveyard'

const projectStore = useProjectStore()
const record = ref(null)
const isLoading = ref(true)

const fetchGraveyardRecord = async () => {
    if (!projectStore.activeProject) return
    isLoading.value = true
    try {
        const res = await graveyardApi.getGraveyards({ project_id: projectStore.activeProject.id })
        if (res.length > 0) {
            record.value = res[0]
        } else {
            record.value = null
        }
    } catch (error) {
        console.error('Failed to fetch graveyard record', error)
    } finally {
        isLoading.value = false
    }
}

watch(() => projectStore.activeProject?.id, () => {
    fetchGraveyardRecord()
}, { immediate: true })
</script>

<template>
  <div class="bg-gray-50/50 rounded-2xl border border-dashed border-gray-200 p-8 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-6">
      <div class="bg-white p-3 rounded-2xl shadow-sm">
        <Skull class="w-8 h-8 text-purple-600" />
      </div>
      <div>
        <h3 class="text-xl font-black text-gray-800 tracking-tight">项目安息地</h3>
        <p class="text-sm font-semibold text-gray-500">每一次死亡都在孕育新生</p>
      </div>
    </div>

    <div v-if="isLoading" class="text-gray-400 py-10 flex-1 flex items-center justify-center">正在翻阅墓志铭...</div>
    
    <div v-else-if="!record" class="text-gray-400 py-10 flex-1 flex flex-col items-center justify-center border-t border-gray-100">
        <Skull class="w-12 h-12 text-gray-200 mb-2" />
        <p>未找到该项目的复盘记录</p>
    </div>

    <div v-else class="space-y-6 flex-1 overflow-y-auto pr-4 custom-scrollbar">
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex items-center gap-2 mb-3">
            <span class="w-8 h-8 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">💔</span>
            <h4 class="font-bold text-gray-800 text-lg">死亡原因</h4>
        </div>
        <p class="text-gray-600 leading-relaxed whitespace-pre-wrap font-medium">{{ record.reason }}</p>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex items-center gap-2 mb-3">
            <span class="w-8 h-8 rounded-xl bg-yellow-50 text-yellow-600 flex items-center justify-center"><Lightbulb class="w-4 h-4" /></span>
            <h4 class="font-bold text-gray-800 text-lg">经验与教训</h4>
        </div>
        <p class="text-gray-600 leading-relaxed whitespace-pre-wrap font-medium">{{ record.lessons }}</p>
      </div>
      
      <div class="text-right text-xs text-gray-400 flex items-center justify-end gap-1 font-semibold">
          <Clock class="w-3 h-3" />
          埋葬于: {{ new Date(record.created_at).toLocaleString() }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e2e8f0; border-radius: 10px; }
</style>
