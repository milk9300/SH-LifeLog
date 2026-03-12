import axiosInstance from './axios'

export const problemApi = {
    getProblems: (params) => {
        return axiosInstance.get('/problems/', { params })
    },
    getProblem: (id) => {
        return axiosInstance.get(`/problems/${id}`)
    },
    createProblem: (data) => {
        return axiosInstance.post('/problems/', data)
    },
    updateProblem: (id, data) => {
        return axiosInstance.put(`/problems/${id}`, data)
    },
    deleteProblem: (id) => {
        return axiosInstance.delete(`/problems/${id}`)
    },
    // 问题记录 → 技术文章
    generateArticle: (id, payload = null) => {
        return axiosInstance.post(`/problems/${id}/generate-article`, payload)
    },
    // AI 助手协同
    aiAssist: (id, payload) => {
        return axiosInstance.post(`/problems/${id}/ai-assist`, payload)
    }
}
