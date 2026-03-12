import axiosInstance from './axios'

export const focusApi = {
    getRecords: (params) => {
        return axiosInstance.get('/focus/', { params })
    },
    createRecord: (data) => {
        return axiosInstance.post('/focus/', data)
    },
    updateRecord: (id, data) => {
        return axiosInstance.patch(`/focus/${id}`, data)
    },
    deleteRecord: (id) => {
        return axiosInstance.delete(`/focus/${id}`)
    }
}
