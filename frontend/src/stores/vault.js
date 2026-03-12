import { defineStore } from 'pinia'
import { ref, readonly } from 'vue'

export const useVaultStore = defineStore('vault', () => {
    const masterPassword = ref('')
    const isLocked = ref(true)
    let lockTimer = null
    const LOCK_TIMEOUT = 5 * 60 * 1000 // 5分钟无操作自动锁定
    let listenersAttached = false

    function resetTimer() {
        if (!isLocked.value && masterPassword.value) {
            if (lockTimer) clearTimeout(lockTimer)
            lockTimer = setTimeout(() => {
                lockVault()
            }, LOCK_TIMEOUT)
        }
    }

    function lockVault() {
        masterPassword.value = ''
        isLocked.value = true
        if (lockTimer) clearTimeout(lockTimer)

        if (listenersAttached) {
            window.removeEventListener('mousemove', resetTimer)
            window.removeEventListener('keydown', resetTimer)
            window.removeEventListener('click', resetTimer)
            listenersAttached = false
        }
    }

    function unlockVault(password) {
        masterPassword.value = password
        isLocked.value = false
        resetTimer()

        if (!listenersAttached) {
            window.addEventListener('mousemove', resetTimer)
            window.addEventListener('keydown', resetTimer)
            window.addEventListener('click', resetTimer)
            listenersAttached = true
        }
    }

    return {
        masterPassword: readonly(masterPassword),
        isLocked: readonly(isLocked),
        unlockVault,
        lockVault,
        resetTimer
    }
})
