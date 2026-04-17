import axios from 'axios'
import store from '../store'

const api = axios.create({
  baseURL: 'http://localhost:8000/v1',
  timeout: 10000
})

api.interceptors.request.use(
  config => {
    const token = store.getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.logout('user')
      store.logout('merchant')
      store.logout('admin')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
