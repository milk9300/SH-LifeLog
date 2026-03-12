import axios from './axios'

export const credentialApi = {
    getCredentials: (params = {}) => axios.get('/credentials', { params }),
    getCredential: (id) => axios.get(`/credentials/${id}`),
    createCredential: (data) => axios.post('/credentials', data),
    updateCredential: (id, data) => axios.put(`/credentials/${id}`, data),
    deleteCredential: (id) => axios.delete(`/credentials/${id}`)
}
