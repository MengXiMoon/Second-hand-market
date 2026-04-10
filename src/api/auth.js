import api from './index'

export const login = (username, password) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return api.post('/login/access-token', formData)
}

export const register = (userData) => {
  return api.post('/register', userData)
}

export const getCurrentUser = () => {
  return api.get('/users/me')
}
