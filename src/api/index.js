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
    if (error.response?.status === 401 || error.response?.status === 403) {
      const isForbidden = error.response.status === 403
      const failedToken = error.config.headers.Authorization?.replace('Bearer ', '')
      
      // Determine which role context this failed token belongs to
      let roleToLogout = null
      if (failedToken) {
        if (failedToken === localStorage.getItem('user_token')) roleToLogout = 'user'
        else if (failedToken === localStorage.getItem('merchant_token')) roleToLogout = 'merchant'
        else if (failedToken === localStorage.getItem('admin_token')) roleToLogout = 'admin'
      }

      if (roleToLogout) {
        store.logout(roleToLogout)
        if (isForbidden) {
          ElMessage.error(`权限不足：当前账号没有${roleToLogout === 'merchant' ? '商家' : (roleToLogout === 'admin' ? '管理' : '相关')}访问权限`)
        }
        
        // Only redirect if the current role being viewed is the one that just logged out
        const currentRole = store.getActiveRole()
        if (currentRole === roleToLogout) {
           window.location.href = '/login'
        }
      } else {
        // Fallback for unidentified role
        const contextRole = store.getActiveRole()
        store.logout(contextRole)
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
