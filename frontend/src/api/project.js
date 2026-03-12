import axiosInstance from './axios'

export const projectApi = {
    getProjects: (params) => {
        return axiosInstance.get('/projects/', { params })
    },
    getProject: (id) => {
        return axiosInstance.get(`/projects/${id}`)
    },
    createProject: (data) => {
        return axiosInstance.post('/projects/', data)
    },
    updateProject: (id, data) => {
        return axiosInstance.put(`/projects/${id}`, data)
    },
    deleteProject: (id) => {
        return axiosInstance.delete(`/projects/${id}`)
    }
}
