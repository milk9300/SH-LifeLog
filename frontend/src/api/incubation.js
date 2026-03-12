import axiosInstance from './axios'

export const incubationApi = {
    getIncubations: (params) => {
        return axiosInstance.get('/incubations/', { params })
    },
    getIncubation: (id) => {
        return axiosInstance.get(`/incubations/${id}`)
    },
    createIncubation: (data) => {
        return axiosInstance.post('/incubations/', data)
    },
    updateIncubation: (id, data) => {
        return axiosInstance.put(`/incubations/${id}`, data)
    },
    deleteIncubation: (id) => {
        return axiosInstance.delete(`/incubations/${id}`)
    }
}

