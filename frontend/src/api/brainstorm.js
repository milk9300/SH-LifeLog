import axiosInstance from './axios'

export const brainstormApi = {
    getBrainstormStats: () => {
        return axiosInstance.get('/brainstorms/stats')
    },
    getBrainstorms: (params) => {
        return axiosInstance.get('/brainstorms/', { params })
    },
    getBrainstorm: (id) => {
        return axiosInstance.get(`/brainstorms/${id}`)
    },
    createBrainstorm: (data) => {
        return axiosInstance.post('/brainstorms/', data)
    },
    updateBrainstorm: (id, data) => {
        return axiosInstance.put(`/brainstorms/${id}`, data)
    },
    deleteBrainstorm: (id) => {
        return axiosInstance.delete(`/brainstorms/${id}`)
    }
}
