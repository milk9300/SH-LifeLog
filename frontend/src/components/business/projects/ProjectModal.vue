<script setup>
import { ref, watch } from 'vue'
import { FolderKanban, X } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  editingProject: Object,
  projectForm: Object
})

const emit = defineEmits(['close', 'save'])

const currentTag = ref('')
const tagList = ref([])

const formatTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(t => t.trim()).filter(t => t)
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    tagList.value = formatTags(props.projectForm.tech_stack)
    currentTag.value = ''
  }
})

const addTag = () => {
  const tag = currentTag.value.trim()
  if (tag && !tagList.value.includes(tag)) {
    tagList.value.push(tag)
    updateTechStack()
  }
  currentTag.value = ''
}

const removeTag = (index) => {
  tagList.value.splice(index, 1)
  updateTechStack()
}

const handleTagKeydown = (e) => {
  if (e.key === ',' || e.key === '，' || e.key === 'Enter') {
    e.preventDefault()
    addTag()
  }
}

const updateTechStack = () => {
  props.projectForm.tech_stack = tagList.value.join(', ')
}
</script>


<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-gray-900/30 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-lg relative z-10 animate-in">
      <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        <FolderKanban class="w-5 h-5 text-primary" />
        {{ editingProject ? '编辑项目' : '新建项目' }}
      </h3>
      
      <div class="space-y-4 mb-8">
        <div>
          <label class="block text-sm font-bold text-gray-600 mb-2">项目名称</label>
          <input 
            v-model="projectForm.name"
            type="text"
            class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-bold text-gray-800"
            placeholder="例如: 个人博客重构"
            autoFocus
          >
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-600 mb-2">项目类型</label>
            <select 
              v-model="projectForm.project_type"
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800 font-bold"
            >
              <option value="Web">Web 应用</option>
              <option value="Mobile">移动端</option>
              <option value="AI">AI/架构</option>
              <option value="Tool">实用工具</option>
              <option value="Other">其他</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-600 mb-2">技术栈</label>
            <div class="flex flex-wrap gap-2 p-2 bg-gray-50 border border-gray-200 rounded-xl focus-within:border-primary focus-within:bg-white focus-within:ring-4 focus-within:ring-primary/5 transition-all min-h-[48px]">
              <span v-for="(tag, index) in tagList" :key="index" 
                    class="flex items-center gap-1 px-2.5 py-1 bg-white border border-primary/20 text-primary text-[11px] font-black rounded-lg shadow-sm">
                # {{ tag }}
                <button @click="removeTag(index)" class="hover:text-red-500 p-0.5">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <input v-model="currentTag" type="text" placeholder="输入技术按回车..." 
                     @keydown="handleTagKeydown"
                     @blur="addTag"
                     class="flex-1 bg-transparent border-none outline-none py-1 font-bold text-gray-800 placeholder:text-gray-300 text-xs min-w-[100px]">
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-600 mb-2">项目链接 (运行)</label>
            <input 
              v-model="projectForm.reference_url"
              type="url"
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800"
              placeholder="https://..."
            >
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-600 mb-2">Git 地址</label>
            <input 
              v-model="projectForm.git_url"
              type="url"
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800"
              placeholder="https://github.com/..."
            >
          </div>
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-600 mb-2">开发备忘 (Notes)</label>
          <textarea 
            v-model="projectForm.description"
            class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800 resize-none"
            rows="3"
            placeholder="项目的技术文档、设计草图或备忘记录..."
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
          :disabled="!projectForm.name.trim()"
          class="flex-1 py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          保存并继续
        </button>
      </div>
    </div>
  </div>
</template>
