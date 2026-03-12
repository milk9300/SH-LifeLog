import axiosInstance from './axios'

export const planApi = {
    getPlans: (params) => {
        return axiosInstance.get('/plans/', { params })
    },
    getPlan: (id) => {
        return axiosInstance.get(`/plans/${id}`)
    },
    createPlan: (data) => {
        return axiosInstance.post('/plans/', data)
    },
    updatePlan: (id, data) => {
        return axiosInstance.put(`/plans/${id}`, data)
    },
    deletePlan: (id) => {
        return axiosInstance.delete(`/plans/${id}`)
    },
    getMilestones: (planId, params) => {
        return axiosInstance.get(`/plans/${planId}/milestones`, { params })
    },
    getMilestone: (id) => {
        return axiosInstance.get(`/milestones/${id}`)
    },
    createMilestone: (data) => {
        return axiosInstance.post('/milestones/', data)
    },
    updateMilestone: (id, data) => {
        return axiosInstance.put(`/milestones/${id}`, data)
    },
    deleteMilestone: (id) => {
        return axiosInstance.delete(`/milestones/${id}`)
    }
}

export const getPlans = planApi.getPlans
export const getPlan = planApi.getPlan
export const addPlan = planApi.createPlan
export const updatePlan = planApi.updatePlan
export const deletePlan = planApi.deletePlan

export const getMilestones = planApi.getMilestones
export const addMilestone = planApi.createMilestone
export const updateMilestone = planApi.updateMilestone
export const deleteMilestone = planApi.deleteMilestone
