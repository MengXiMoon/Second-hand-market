import api from './index'

export const getNotifications = () => {
  return api.get('/notifications')
}

export const getUnreadCount = () => {
  return api.get('/notifications/unread-count')
}

export const markRead = (id) => {
  return api.put(`/notifications/${id}/read`)
}

export const markAllRead = () => {
  return api.put('/notifications/read-all')
}
