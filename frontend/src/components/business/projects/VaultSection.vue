<script setup>
import { ref } from 'vue'
import { Shield, Lock, Key, Copy, Check, Download } from 'lucide-vue-next'
import { useVaultStore } from '../../../stores/vault'
import { useProjectStore } from '../../../stores/project'
import { storeToRefs } from 'pinia'
import { credentialApi } from '../../../api/credential'
import { decryptData } from '../../../utils/crypto'

const vaultStore = useVaultStore()
const projectStore = useProjectStore()
const { isLocked, masterPassword } = storeToRefs(vaultStore)
const { activeProject } = storeToRefs(projectStore)

const props = defineProps({
  hideHeader: {
    type: Boolean,
    default: false
  }
})

const projectCredentials = ref([])
const isFetchingCredentials = ref(false)
const copiedId = ref(null)

const loadProjectCredentials = async (projectId) => {
  if (isLocked.value || !masterPassword.value) {
    projectCredentials.value = []
    return
  }
  
  isFetchingCredentials.value = true
  try {
    const data = await credentialApi.getCredentials({ project_id: projectId })
    const decryptedData = []
    for (const item of data) {
      try {
        const decryptedStr = await decryptData(item.encrypted_data, masterPassword.value)
        decryptedData.push({ ...item, ...JSON.parse(decryptedStr) })
      } catch (e) {
        console.error('Decrypt failed for', item.id)
      }
    }
    projectCredentials.value = decryptedData
  } catch (error) {
    console.error('Failed to load credentials', error)
  } finally {
    isFetchingCredentials.value = false
  }
}

const copyToClipboard = async (text, id) => {
    try {
        await navigator.clipboard.writeText(text)
        copiedId.value = id
        setTimeout(() => { copiedId.value = null }, 2000)
        vaultStore.resetTimer()
    } catch (err) {
        console.error('Failed to copy', err)
    }
}

const exportEnvFile = () => {
    if (projectCredentials.value.length === 0) return
    
    let envContent = `# Environment Variables for ${activeProject.value.name}\n# Exported from Dev Dash Vault\n\n`
    
    projectCredentials.value.forEach(c => {
        const keyName = c.name.toUpperCase().replace(/[^A-Z0-9]/g, '_')
        envContent += `${keyName}="${c.password}"\n`
        if (c.username) {
            envContent += `${keyName}_USER="${c.username}"\n`
        }
    })
    
    const blob = new Blob([envContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '.env'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    vaultStore.resetTimer()
}

// Watch for project changes or unlocking
import { watch } from 'vue'
watch(() => [activeProject.value?.id, isLocked.value], ([newId, locked]) => {
  if (newId && !locked) {
    loadProjectCredentials(newId)
  } else {
    projectCredentials.value = []
  }
}, { immediate: true })
</script>

<template>
  <div :class="hideHeader ? '' : 'mb-8'" v-if="activeProject">
    <div v-if="!hideHeader" class="flex items-center justify-between mb-4">
       <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
         <Shield class="w-5 h-5 text-primary" />
         项目凭证 <span class="text-xs font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded">Vault</span>
       </h3>
       
       <button 
         v-if="!isLocked && projectCredentials.length > 0"
         @click="exportEnvFile"
         class="flex items-center gap-1.5 text-xs font-bold text-gray-600 bg-white border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50 hover:text-primary hover:border-primary/30 transition-colors shadow-sm"
       >
         <Download class="w-3.5 h-3.5" />
         导出 .env
       </button>
    </div>
    
    <div v-if="isLocked" class="bg-gray-50 border border-gray-100 rounded-2xl p-6 text-center">
      <Lock class="w-8 h-8 text-gray-300 mx-auto mb-2" />
      <p class="text-sm text-gray-500 mb-3">密钥库当前处于锁定状态</p>
      <router-link to="/vault" class="text-xs font-bold text-primary bg-primary/10 px-4 py-2 rounded-lg hover:bg-primary/20 transition-colors inline-block">
        前往解锁
      </router-link>
    </div>
    
    <div v-else-if="isFetchingCredentials" class="text-center py-6 text-gray-400 text-sm">
        加载凭证中...
    </div>
    
    <div v-else-if="projectCredentials.length === 0" class="bg-white border border-gray-100 border-dashed rounded-2xl p-6 text-center text-gray-400">
        暂无绑定的凭证，可以在 <router-link to="/vault" class="text-primary hover:underline">密钥库</router-link> 中新建并关联此项目。
    </div>
    
    <div v-else :class="[
      'grid grid-cols-1 gap-3',
      hideHeader ? '' : 'xl:grid-cols-2'
    ]">
       <div 
         v-for="cred in projectCredentials" 
         :key="cred.id"
         :class="[
           'bg-white border border-gray-100 rounded-xl shadow-sm hover:border-primary/30 transition-colors group flex flex-col',
           hideHeader ? 'p-2.5 gap-1.5' : 'p-3 gap-2'
         ]"
       >
         <div class="flex items-center gap-3 overflow-hidden">
            <div :class="[
              'bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 shrink-0',
              hideHeader ? 'w-7 h-7' : 'w-8 h-8'
            ]">
                <Key :class="hideHeader ? 'w-3.5 h-3.5' : 'w-4 h-4'" />
            </div>
            <div class="flex-1 min-w-0">
                <div :class="[
                  'font-bold text-gray-800 truncate pr-2',
                  hideHeader ? 'text-xs' : 'text-sm'
                ]">{{ cred.name }}</div>
                <div class="text-[9px] text-gray-400 uppercase tracking-widest">{{ cred.category || 'NO CATEGORY' }}</div>
            </div>
         </div>
         
         <div class="bg-gray-50/50 rounded-lg border border-gray-100 flex flex-col text-[11px] text-gray-600">
             <div v-if="cred.username" class="px-2 py-1 border-b border-gray-50 flex items-center justify-between">
                 <span class="text-gray-400 uppercase text-[9px] tracking-wider font-black">User</span>
                 <span class="font-bold flex items-center gap-1.5">
                     {{ cred.username }}
                     <button @click="copyToClipboard(cred.username, cred.id + '-user')" class="text-gray-300 hover:text-primary transition-colors">
                         <Check v-if="copiedId === cred.id + '-user'" class="w-3 h-3 text-green-500" />
                         <Copy v-else class="w-3 h-3" />
                     </button>
                 </span>
             </div>
             <div class="px-2 py-1 flex items-center justify-between group/secret">
                 <div class="flex items-center gap-2 flex-1 min-w-0">
                     <span class="text-gray-400 uppercase text-[9px] tracking-wider font-black shrink-0">Key</span>
                     <span class="font-mono truncate focus:outline-none opacity-50">••••••••</span>
                 </div>
                 <button 
                    @click="copyToClipboard(cred.password, cred.id)"
                    class="p-1 text-gray-300 hover:text-primary hover:bg-primary/5 rounded transition-colors relative shrink-0"
                 >
                    <Check v-if="copiedId === cred.id" class="w-3 h-3 text-green-500" />
                    <Copy v-else class="w-3 h-3" />
                 </button>
             </div>
         </div>
       </div>
    </div>
  </div>
</template>
