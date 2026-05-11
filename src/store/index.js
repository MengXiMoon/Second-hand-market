import { reactive } from 'vue'
import { logoutRequest } from '../api/auth'

const getRoleData = (role) => {
  return {
    user: JSON.parse(localStorage.getItem(`${role}_info`) || 'null'),
    token: localStorage.getItem(`${role}_token`)
  }
}

const state = reactive({
  user: getRoleData('user'),
  merchant: getRoleData('merchant'),
  admin: getRoleData('admin')
})

const getActiveRole = () => {
  const params = new URLSearchParams(window.location.search)
  const roleParam = params.get('role')
  if (roleParam && ['user', 'merchant', 'admin'].includes(roleParam)) {
    return roleParam
  }

  const path = window.location.pathname
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/merchant')) return 'merchant'

  if (path.startsWith('/customer') || path === '/' || path === '/login' || path === '/register') {
    const params = new URLSearchParams(window.location.search)
    if (!params.get('role')) return 'user'
  }

  return localStorage.getItem('last_active_role') || 'user'
}

const setContextRole = (role) => {
  if (['user', 'merchant', 'admin'].includes(role)) {
    localStorage.setItem('last_active_role', role)
  }
}

const setUser = (userInfo, token) => {
  const role = userInfo.role === 'admin' ? 'admin' : (userInfo.role === 'merchant' ? 'merchant' : 'user')
  state[role].user = userInfo
  state[role].token = token
  localStorage.setItem(`${role}_info`, JSON.stringify(userInfo))
  localStorage.setItem(`${role}_token`, token)
}

const logout = async (role) => {
  const r = role || getActiveRole()
  if (state[r]) {
    // 通知后端释放会话，允许其他设备登录
    try { await logoutRequest() } catch (_) { /* 网络错误也继续本机登出 */ }
    state[r].user = null
    state[r].token = null
    localStorage.removeItem(`${r}_info`)
    localStorage.removeItem(`${r}_token`)

    if (localStorage.getItem('last_active_role') === r) {
      localStorage.setItem('last_active_role', 'user')
    }
  }
}

const getCurrentSession = () => {
  const role = getActiveRole()
  return state[role]
}

const getAuthToken = () => {
  return getCurrentSession().token
}

export default {
  state,
  setUser,
  logout,
  getAuthToken,
  getCurrentSession,
  getActiveRole,
  setContextRole
}
