import { defineStore } from 'pinia'
import { dashboardApi } from '../api/dashboard'

export const useDashboardStore = defineStore('dashboard', {
    state: () => ({
        stats: {
            active_projects: 0,
            today_remaining_tasks: 0,
            pending_brainstorms: 0,
            active_plans: 0,
            total_reflections: 0,
            total_credentials: 0
        },
        isLoading: false
    }),
    actions: {
        async fetchStats() {
            this.isLoading = true
            try {
                this.stats = await dashboardApi.getStats()
            } catch (error) {
                console.error('Failed to fetch dashboard stats', error)
            } finally {
                this.isLoading = false
            }
        }
    }
})
