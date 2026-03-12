<script setup>
import { ref, onMounted, computed } from 'vue'
import { Shield, ShieldAlert, Lock, Unlock, Search, Plus, Key, Copy, Check, Eye, EyeOff, X, Server, Database, Globe } from 'lucide-vue-next'
import { useVaultStore } from '../stores/vault'
import { credentialApi } from '../api/credential'
import { projectApi } from '../api/project'
import { encryptData, decryptData } from '../utils/crypto'
import { storeToRefs } from 'pinia'

const vaultStore = useVaultStore()
const { isLocked, masterPassword } = storeToRefs(vaultStore)
const { unlockVault, lockVault, resetTimer } = vaultStore

// UI State
const passwordInput = ref('')
const loginError = ref('')
const searchQuery = ref('')
const activeCategory = ref('All')

const credentials = ref([])
const isLoading = ref(false)

const handleUnlock = async () => {
    if (!passwordInput.value) {
        loginError.value = '请输入主密码'
        return
    }
    
    unlockVault(passwordInput.value)
    passwordInput.value = ''
    loginError.value = ''
    
    await fetchCredentials()
}

const fetchCredentials = async () => {
    if (isLocked.value) return
    
    isLoading.value = true
    try {
        const data = await credentialApi.getCredentials()
        const decryptedData = []
        let hasDecryptionError = false
        for (const item of data) {
            try {
                const decryptedStr = await decryptData(item.encrypted_data, masterPassword.value)
                const parsedData = JSON.parse(decryptedStr)
                decryptedData.push({ ...item, ...parsedData })
            } catch (e) {
                console.error('Failed to decrypt item', item.id)
                hasDecryptionError = true
            }
        }
        
        if (data.length > 0 && hasDecryptionError) {
            lockVault()
            loginError.value = '解密失败：主密码错误'
            return
        }

        credentials.value = decryptedData
    } catch (error) {
        console.error('Failed to fetch credentials:', error)
    } finally {
        isLoading.value = false
    }
}

const filteredCredentials = computed(() => {
    let result = credentials.value
    if (activeCategory.value !== 'All') {
        result = result.filter(c => c.category === activeCategory.value)
    }
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        result = result.filter(c => 
            c.name.toLowerCase().includes(q) || 
            (c.username && c.username.toLowerCase().includes(q))
        )
    }
    return result
})

const categories = [
    { name: 'All', icon: Key },
    { name: 'Server', icon: Server },
    { name: 'Database', icon: Database },
    { name: 'API', icon: Globe }
]

const copiedId = ref(null)
const revealedId = ref(null)

const copyToClipboard = async (text, id) => {
    try {
        await navigator.clipboard.writeText(text)
        copiedId.value = id
        setTimeout(() => { copiedId.value = null }, 2000)
        resetTimer()
    } catch (err) {
        console.error('Failed to copy', err)
    }
}

const toggleReveal = (id) => {
    revealedId.value = revealedId.value === id ? null : id
    resetTimer()
}

const showModal = ref(false)
const modalForm = ref({ name: '', category: 'Server', username: '', password: '', notes: '', project_id: null })
const projectsList = ref([])
const editingId = ref(null)

const fetchProjects = async () => {
    try {
        const res = await projectApi.getProjects()
        projectsList.value = res
    } catch(e) {
        console.error(e)
    }
}

const openModal = () => {
    editingId.value = null
    modalForm.value = { name: '', category: 'Server', username: '', password: '', notes: '', project_id: null }
    if (projectsList.value.length === 0) fetchProjects()
    showModal.value = true
}

const editCredential = async (item) => {
    modalForm.value = {
        name: item.name,
        category: item.category || 'Server',
        username: item.username || '',
        password: item.password || '',
        notes: item.notes || '',
        project_id: item.project_id || null
    }
    editingId.value = item.id
    if (projectsList.value.length === 0) fetchProjects()
    showModal.value = true
}

const confirmDelete = async (item) => {
    if (!confirm(`确定要永久删除凭证 "${item.name}" 吗？此操作无法撤销。`)) return
    try {
        await credentialApi.deleteCredential(item.id)
        await fetchCredentials()
    } catch (e) {
        console.error('Delete failed', e)
    }
}

const saveCredential = async () => {
    if(!modalForm.value.name || !modalForm.value.password) return
    const payloadObject = { password: modalForm.value.password, notes: modalForm.value.notes }
    try {
        const encryptedData = await encryptData(JSON.stringify(payloadObject), masterPassword.value)
        const dbPayload = {
            name: modalForm.value.name,
            category: modalForm.value.category,
            username: modalForm.value.username,
            project_id: modalForm.value.project_id || null,
            encrypted_data: encryptedData
        }
        if (editingId.value) {
            await credentialApi.updateCredential(editingId.value, dbPayload)
        } else {
            await credentialApi.createCredential(dbPayload)
        }
        showModal.value = false
        await fetchCredentials()
    } catch(e) {
        console.error("Save/Update failed", e)
    }
}

const generatePassword = () => {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
    let pwd = ""
    for(let i=0; i<16; i++) pwd += chars.charAt(Math.floor(Math.random() * chars.length))
    modalForm.value.password = pwd
}

const generateUUID = () => { modalForm.value.password = crypto.randomUUID() }

const generateHex = () => {
    const bytes = window.crypto.getRandomValues(new Uint8Array(32))
    modalForm.value.password = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('')
}

onMounted(() => {
    if (!isLocked.value) fetchCredentials()
})
</script>

<template>
  <div class="h-full flex flex-col pt-6 md:pt-0 pb-10">
    <!-- Header -->
    <header class="flex justify-between items-center mb-8 px-2">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
          密钥库 <span class="bg-primary/10 text-primary text-xs px-2 py-1 rounded-md font-medium">Vault</span>
        </h1>
        <p class="text-gray-500 mt-2 text-sm max-w-xl">
          本地无痕，零信任架构。所有凭证均在客户端使用 Web Crypto API 进行 AES-GCM 加密，主密码仅留存内存。
        </p>
      </div>

      <div v-if="!isLocked" class="flex items-center gap-4">
        <button 
            @click="lockVault"
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
            <Lock class="w-4 h-4" />
            <span>锁定</span>
        </button>
        <button 
            @click="openModal"
            class="flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-xl hover:bg-primary-hover transition-colors shadow-sm shadow-primary/30 font-medium"
        >
          <Plus class="w-5 h-5" />
          <span>新建凭证</span>
        </button>
      </div>
    </header>

    <!-- Locked State View -->
    <div v-if="isLocked" class="flex-1 flex items-center justify-center animate-in">
        <div class="bg-white p-10 rounded-2xl shadow-sm border border-gray-100 max-w-md w-full text-center">
            <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield class="w-10 h-10 text-primary" />
            </div>
            <h2 class="text-2xl font-bold text-gray-900 mb-2">密钥库已锁定</h2>
            <p class="text-gray-500 mb-8">请输入主密码以解密并查看您的凭证。</p>
            
            <form @submit.prevent="handleUnlock" class="space-y-4 text-left">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">主密码</label>
                    <div class="relative">
                        <Lock class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input 
                            v-model="passwordInput"
                            type="password" 
                            class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-gray-900"
                            placeholder="••••••••"
                            autocomplete="current-password"
                        >
                    </div>
                    <p v-if="loginError" class="text-red-500 text-sm mt-2 flex items-center gap-1">
                        <ShieldAlert class="w-4 h-4" /> {{ loginError }}
                    </p>
                </div>
                <button 
                    type="submit"
                    class="w-full flex items-center justify-center gap-2 bg-gray-900 text-white px-5 py-3 rounded-xl hover:bg-gray-800 transition-colors font-medium"
                >
                    <Unlock class="w-5 h-5" />
                    <span>解密并进入</span>
                </button>
            </form>
        </div>
    </div>

    <!-- Unlocked State View -->
    <div v-else class="flex-1 flex flex-col gap-6 animate-in">
        <!-- Toolbar -->
        <div class="flex flex-col md:flex-row gap-4 justify-between">
            <!-- Search -->
            <div class="relative max-w-md w-full">
                <Search class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                    v-model="searchQuery"
                    type="text" 
                    placeholder="搜索凭证、标签或用户名... (Ctrl+K)"
                    class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-sm"
                >
            </div>

            <!-- Categories -->
            <div class="flex bg-white border border-gray-200 rounded-xl p-1 shadow-sm overflow-x-auto">
                <button 
                    v-for="cat in categories" 
                    :key="cat.name"
                    @click="activeCategory = cat.name"
                    class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                    :class="activeCategory === cat.name ? 'bg-primary/10 text-primary' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'"
                >
                    <component :is="cat.icon" class="w-4 h-4" />
                    {{ cat.name }}
                </button>
            </div>
        </div>

        <!-- Credentials List -->
        <div v-if="isLoading" class="flex-1 flex items-center justify-center">
            <div class="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
        </div>
        
        <div v-else-if="filteredCredentials.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
            <Key class="w-16 h-16 mb-4 text-gray-200" />
            <p>还没有记录任何凭证，或者搜索无结果。</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
                v-for="item in filteredCredentials" 
                :key="item.id"
                class="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-primary/30 transition-all group"
            >
                <div class="flex justify-between items-start mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-center text-gray-500">
                            <Server v-if="item.category === 'Server'" class="w-5 h-5" />
                            <Database v-else-if="item.category === 'Database'" class="w-5 h-5" />
                            <Globe v-else-if="item.category === 'API'" class="w-5 h-5" />
                            <Key v-else class="w-5 h-5" />
                        </div>
                        <div>
                            <h3 class="font-bold text-gray-900">{{ item.name }}</h3>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-medium px-2 py-1 bg-gray-100 text-gray-600 rounded-md uppercase tracking-wider">
                            {{ item.category || 'Other' }}
                        </span>
                        
                        <div class="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <button @click="editCredential(item)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                                <Edit2 class="w-3.5 h-3.5" />
                            </button>
                            <button @click="confirmDelete(item)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                                <Trash2 class="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>
                </div>

                <div class="bg-gray-50 rounded-xl border border-gray-100 relative group/secret">
                    <div v-if="item.username" class="px-3 py-2 border-b border-gray-100 flex items-center justify-between">
                        <div class="text-[10px] font-medium text-gray-500 uppercase tracking-widest">USERNAME</div>
                        <div class="text-sm font-medium text-gray-700 flex items-center gap-2">
                           {{ item.username }}
                           <button @click="copyToClipboard(item.username, item.id + '-user')" class="p-1 text-gray-400 hover:text-primary transition-colors relative">
                                <Check v-if="copiedId === item.id + '-user'" class="w-3.5 h-3.5 text-green-500" />
                                <Copy v-else class="w-3.5 h-3.5" />
                           </button>
                        </div>
                    </div>
                    
                    <div class="px-3 py-2.5 flex items-center justify-between">
                        <div class="flex-1 min-w-0 pr-2">
                             <div class="text-[10px] font-medium text-gray-500 uppercase tracking-widest mb-0.5">PASSWORD / KEY</div>
                             <div class="font-mono text-sm text-gray-900 truncate flex items-center gap-2">
                                <span>{{ revealedId === item.id ? item.password : '••••••••••••••••' }}</span>
                             </div>
                        </div>
                        
                        <div class="flex gap-0.5 opacity-0 group-hover/secret:opacity-100 transition-opacity shrink-0">
                            <button @click="toggleReveal(item.id)" class="p-1.5 text-gray-400 hover:text-gray-900 hover:bg-gray-200 rounded-md transition-colors">
                                <EyeOff v-if="revealedId === item.id" class="w-4 h-4" />
                                <Eye v-else class="w-4 h-4" />
                            </button>
                            <button @click="copyToClipboard(item.password, item.id)" class="p-1.5 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-md transition-colors relative">
                                <Check v-if="copiedId === item.id" class="w-4 h-4 text-green-500" />
                                <Copy v-else class="w-4 h-4" />
                                <div v-if="copiedId === item.id" class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[10px] px-2 py-1 rounded whitespace-nowrap z-10">已复制</div>
                            </button>
                        </div>
                    </div>
                </div>

                <div v-if="item.notes" class="mt-3 px-3 py-2 bg-yellow-50/50 border border-yellow-100/50 rounded-lg">
                    <div class="text-[10px] font-medium text-yellow-800/60 uppercase tracking-widest mb-1">NOTES</div>
                    <p class="text-xs text-yellow-900/80 font-mono whitespace-pre-wrap leading-relaxed">{{ item.notes }}</p>
                </div>
            </div>
        </div>
    </div>

    <!-- New Credential Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-gray-900/30 backdrop-blur-sm" @click="showModal = false"></div>
      
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl relative z-10 animate-in overflow-hidden flex flex-col max-h-[90vh]">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
            <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Shield class="w-6 h-6 text-primary" />
                新增安全凭证
            </h3>
            <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors"><X class="w-5 h-5" /></button>
        </div>

        <div class="p-6 overflow-y-auto space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                    <label class="block text-sm font-bold text-gray-700">凭证名称 *</label>
                    <input v-model="modalForm.name" type="text" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800" placeholder="e.g. 生产环境 MySQL">
                </div>
                <div class="space-y-1">
                    <label class="block text-sm font-bold text-gray-700">分类</label>
                    <select v-model="modalForm.category" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800">
                        <option value="Server">服务器 (Server)</option>
                        <option value="Database">数据库 (Database)</option>
                        <option value="API">API 密钥 (API)</option>
                        <option value="Other">其他 (Other)</option>
                    </select>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                    <label class="block text-sm font-bold text-gray-700">账号/用户名</label>
                    <input v-model="modalForm.username" type="text" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800" placeholder="e.g. root, admin">
                </div>
                <div class="space-y-1">
                    <label class="block text-sm font-bold text-gray-700">关联项目 (可选)</label>
                    <select v-model="modalForm.project_id" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800">
                        <option :value="null">-- 不关联 --</option>
                        <option v-for="p in projectsList" :key="p.id" :value="p.id">{{ p.name }}</option>
                    </select>
                </div>
            </div>

            <div class="space-y-2 border border-primary/20 bg-primary/5 rounded-2xl p-4">
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-bold text-primary">密码 / 密钥 (加密存储) *</label>
                    <div class="flex items-center gap-1">
                        <span class="text-[10px] text-gray-500 font-medium uppercase mr-1">生成器:</span>
                        <button @click.prevent="generatePassword" class="px-2 py-1 text-xs bg-white border border-gray-200 rounded text-gray-600 hover:text-primary hover:border-primary transition-colors">PWD</button>
                        <button @click.prevent="generateUUID" class="px-2 py-1 text-xs bg-white border border-gray-200 rounded text-gray-600 hover:text-primary hover:border-primary transition-colors">UUID</button>
                        <button @click.prevent="generateHex" class="px-2 py-1 text-xs bg-white border border-gray-200 rounded text-gray-600 hover:text-primary hover:border-primary transition-colors">HEX</button>
                    </div>
                </div>
                <input v-model="modalForm.password" type="text" class="w-full bg-white border border-primary/30 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/40 transition-all font-mono text-gray-900" placeholder="输入密钥内容或使用右上角一键生成...">
                <p class="text-xs text-gray-500 mt-1 flex items-center gap-1"><Lock class="w-3 h-3" /> 此内容将仅保留在本地内存，落盘前将使用 AES-GCM 加密。</p>
            </div>

            <div class="space-y-1">
                <label class="block text-sm font-bold text-gray-700">备注</label>
                <textarea v-model="modalForm.notes" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all text-gray-800 resize-none font-mono text-sm" rows="3" placeholder="例如：Host IP, Port, SSH 端口号, 配置文件路径等..."></textarea>
            </div>
        </div>

        <div class="p-6 border-t border-gray-100 bg-gray-50/50 flex gap-4 justify-end">
            <button @click="showModal = false" class="px-6 py-2.5 text-gray-600 font-semibold bg-white border border-gray-200 hover:bg-gray-50 rounded-xl transition-colors">取消</button>
            <button @click="saveCredential" :disabled="!modalForm.name || !modalForm.password" class="px-8 py-2.5 bg-gray-900 text-white font-bold rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center gap-2">
                <Lock class="w-4 h-4" />加密并保存
            </button>
        </div>
      </div>
    </div>
  </div>
</template>
