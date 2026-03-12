import axiosInstance from './axios'

export const graveyardApi = {
    getGraveyards: (params) => {
        return axiosInstance.get('/graveyards/', { params })
    },
    getGraveyard: (id) => {
        return axiosInstance.get(`/graveyards/${id}`)
    },
    createGraveyard: (data) => {
        return axiosInstance.post('/graveyards/', data)
    },
    updateGraveyard: (id, data) => {
        return axiosInstance.put(`/graveyards/${id}`, data)
    },
    deleteGraveyard: (id) => {
        return axiosInstance.delete(`/graveyards/${id}`)
    }
}
