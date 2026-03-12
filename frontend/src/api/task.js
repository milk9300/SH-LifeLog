import axiosInstance from './axios'

export const taskApi = {
    getTasks: (params) => {
        return axiosInstance.get('/tasks/', { params })
    },
    getTask: (id) => {
        return axiosInstance.get(`/tasks/${id}`)
    },
    createTask: (data) => {
        return axiosInstance.post('/tasks/', data)
    },
    updateTask: (id, data) => {
        return axiosInstance.put(`/tasks/${id}`, data)
    },
    deleteTask: (id) => {
        return axiosInstance.delete(`/tasks/${id}`)
    },
    // 任务 → 知识沉淀（问题记录）
    convertToProblem: (id) => {
        return axiosInstance.post(`/tasks/${id}/convert-to-problem`)
    }
}

