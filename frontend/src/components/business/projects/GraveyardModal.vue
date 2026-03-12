<script setup>
import { Skull, CornerDownRight } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  buryingProject: Object,
  graveyardForm: Object
})

const emit = defineEmits(['close', 'save'])
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-gray-900/30 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-lg relative z-10 animate-in">
      <h3 class="text-xl font-bold text-gray-800 mb-2 flex items-center gap-2">
        <Skull class="w-6 h-6 text-purple-600" />
        项目坟场复盘
      </h3>
      <p class="text-gray-500 mb-6 flex items-center gap-1 text-sm">
        <CornerDownRight class="w-4 h-4" /> 记录痛点，为了下一次的重生。
      </p>
      
      <div class="space-y-4 mb-8">
        <div>
          <label class="block text-sm font-bold text-gray-600 mb-2">失败原因 (Reason)</label>
          <textarea 
            v-model="graveyardForm.reason"
            class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all text-gray-800 resize-none"
            rows="3"
            placeholder="为什么这个项目最终没成？（技术难题、需求伪命题、缺乏时间等）..."
            autoFocus
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-600 mb-2">经验教训 (Lessons)</label>
          <textarea 
            v-model="graveyardForm.lessons"
            class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all text-gray-800 resize-none"
            rows="4"
            placeholder="学到了什么可以带入到下一个项目中的经验？"
          ></textarea>
        </div>
      </div>
      
      <div class="flex gap-4">
        <button 
          @click="emit('close')"
          class="flex-1 py-3 text-gray-600 font-semibold bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors"
        >
          取消
        </button>
        <button 
          @click="emit('save')"
          :disabled="!graveyardForm.reason.trim()"
          class="flex-1 py-3 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-md shadow-purple-600/20"
        >
          <Skull class="w-4 h-4" />确认埋葬
        </button>
      </div>
    </div>
  </div>
</template>
