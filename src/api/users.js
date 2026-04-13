import api from './index'

export const getUsers = (skip = 0, limit = 100) => {
  return api.get('/users', { params: { skip, limit } })
}

export const getPendingUsers = () => {
  return api.get('/users/pending')
}

export const verifyUser = (userId) => {
  return api.put(`/users/${userId}/verify`)
}

export const deleteUser = (userId) => {
  return api.delete(`/users/${userId}`)
}
