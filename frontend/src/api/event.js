import axiosInstance from './axios'

export const eventApi = {
    getEvents: (params) => {
        return axiosInstance.get('/events', { params })
    },
    getEvent: (id) => {
        return axiosInstance.get(`/events/${id}`)
    },
    createEvent: (data) => {
        return axiosInstance.post('/events', data)
    },
    updateEvent: (id, data) => {
        return axiosInstance.put(`/events/${id}`, data)
    },
    deleteEvent: (id) => {
        return axiosInstance.delete(`/events/${id}`)
    }
}

// Map the individual functions as expected by the existing EventTracker.vue Component
export const getEvents = eventApi.getEvents
export const addEvent = eventApi.createEvent
export const updateEvent = eventApi.updateEvent
export const deleteEvent = eventApi.deleteEvent
