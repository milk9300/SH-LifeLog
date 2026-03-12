import { defineStore } from 'pinia'
import { brainstormApi } from '../api/brainstorm'

export const useBrainstormStore = defineStore('brainstorm', {
    state: () => ({
        brainstorms: [],
        stats: { inbox: 0, archived: 0, converted: 0 },
        isLoading: false,
        currentTab: 'inbox'
    }),

    actions: {
        async fetchStats() {
            try {
                this.stats = await brainstormApi.getBrainstormStats()
            } catch (error) {
                console.error('Failed to load stats', error)
            }
        },

        async fetchBrainstorms(status = null) {
            this.isLoading = true
            const targetStatus = status || this.currentTab
            try {
                this.brainstorms = await brainstormApi.getBrainstorms({ status: targetStatus })
                await this.fetchStats()
            } catch (error) {
                console.error('Failed to load brainstorms', error)
            } finally {
                this.isLoading = false
            }
        },

        async switchTab(tab) {
            this.currentTab = tab
            await this.fetchBrainstorms(tab)
        },

        async createIdea(content, tags) {
            try {
                await brainstormApi.createBrainstorm({ content, tags, status: 'inbox' })
                await this.fetchBrainstorms()
            } catch (error) {
                console.error('Failed to create idea', error)
            }
        },

        async updateStatus(id, status) {
            try {
                await brainstormApi.updateBrainstorm(id, { status })
                await this.fetchBrainstorms()
            } catch (error) {
                console.error('Failed to update status', error)
            }
        },

        async updateTags(id, tags) {
            try {
                await brainstormApi.updateBrainstorm(id, { tags })
                await this.fetchBrainstorms()
            } catch (error) {
                console.error('Failed to update tags', error)
            }
        }
    }
})
