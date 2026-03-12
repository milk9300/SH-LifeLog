import axiosInstance from './axios'

export const dashboardApi = {
    getStats: () => {
        return axiosInstance.get('/dashboard/stats')
    }
}
