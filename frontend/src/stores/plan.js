import { defineStore } from 'pinia'
import { getPlans, addPlan, updatePlan, deletePlan, getMilestones } from '../api/plan'

export const usePlanStore = defineStore('plan', {
    state: () => ({
        plans: [],
        isLoading: false
    }),

    actions: {
        async fetchPlans() {
            this.isLoading = true
            try {
                const data = await getPlans()
                const plansWithProgress = await Promise.all(data.map(async (plan) => {
                    const milestones = await getMilestones(plan.id)
                    const total = milestones.length
                    const done = milestones.filter(m => m.status === 'done').length
                    const progress = total === 0 ? 0 : Math.round((done / total) * 100)
                    return { ...plan, progress, milestonesCount: total }
                }))
                this.plans = plansWithProgress
            } catch (error) {
                console.error('Failed to load plans:', error)
            } finally {
                this.isLoading = false
            }
        },

        async createPlan(planData) {
            try {
                await addPlan(planData)
                await this.fetchPlans()
            } catch (error) {
                console.error('Failed to add plan:', error)
            }
        },

        async toggleStatus(plan) {
            const cycle = ['active', 'paused', 'completed']
            const idx = cycle.indexOf(plan.status)
            const nextStatus = cycle[(idx + 1) % cycle.length]
            try {
                await updatePlan(plan.id, { status: nextStatus })
                await this.fetchPlans()
            } catch (error) {
                console.error('Failed to change status:', error)
            }
        },

        async removePlan(id) {
            try {
                await deletePlan(id)
                await this.fetchPlans()
            } catch (error) {
                console.error('Failed to delete plan:', error)
            }
        }
    }
})
