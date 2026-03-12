import { defineStore } from 'pinia'
import { projectApi } from '../api/project'
import { taskApi } from '../api/task'

export const useProjectStore = defineStore('project', {
    state: () => ({
        projects: [],
        activeProject: null,
        tasks: [],
        isLoading: false
    }),

    getters: {
        projectProgress: (state) => {
            if (state.tasks.length === 0) return 0
            const doneTasks = state.tasks.filter(t => t.status === 'done').length
            return Math.round((doneTasks / state.tasks.length) * 100)
        },
        projectCounts: (state) => {
            const counts = { preparation: 0, active: 0, deploying: 0, done: 0, graveyard: 0 }
            state.projects.forEach(p => {
                if (p.status in counts) counts[p.status]++
            })
            return counts
        }
    },

    actions: {
        async fetchProjects() {
            this.isLoading = true
            try {
                const res = await projectApi.getProjects()
                this.projects = res
                return res
            } catch (error) {
                console.error('Failed to load projects', error)
            } finally {
                this.isLoading = false
            }
        },

        async selectProject(project) {
            this.activeProject = project
            await this.fetchTasks(project.id)
        },

        async fetchProjectById(id) {
            this.isLoading = true
            try {
                const res = await projectApi.getProject(id)
                this.activeProject = res
                await this.fetchTasks(id)
                return res
            } catch (error) {
                console.error('Failed to fetch project by id', error)
            } finally {
                this.isLoading = false
            }
        },

        async fetchTasks(projectId) {
            try {
                const res = await taskApi.getTasks({ project_id: projectId })
                // 排序逻辑：未完成任务在前，且按创建时间倒序排列
                this.tasks = res.sort((a, b) => {
                    if (a.status === 'done' && b.status !== 'done') return 1
                    if (a.status !== 'done' && b.status === 'done') return -1
                    return new Date(b.created_at) - new Date(a.created_at)
                })
            } catch (error) {
                console.error('Failed to load tasks', error)
            }
        },

        async updateProjectStatus(projectId, newStatus) {
            try {
                await projectApi.updateProject(projectId, { status: newStatus })
                if (this.activeProject && this.activeProject.id === projectId) {
                    this.activeProject.status = newStatus
                }
                await this.fetchProjects()
            } catch (error) {
                console.error('Failed to update project status', error)
            }
        }
    }
})
