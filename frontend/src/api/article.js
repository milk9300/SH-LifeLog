import axiosInstance from './axios'

export const articleApi = {
    getArticles: (params) => {
        return axiosInstance.get('/articles/', { params })
    },
    getArticle: (id) => {
        return axiosInstance.get(`/articles/${id}`)
    },
    createArticle: (data) => {
        return axiosInstance.post('/articles/', data)
    },
    updateArticle: (id, data) => {
        return axiosInstance.put(`/articles/${id}`, data)
    },
    deleteArticle: (id) => {
        return axiosInstance.delete(`/articles/${id}`)
    }
}
