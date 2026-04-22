import { reactive } from 'vue'

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
  // 1. Check URL query params first (e.g. /chat?role=merchant)
  const params = new URLSearchParams(window.location.search)
  const roleParam = params.get('role')
  if (roleParam && ['user', 'merchant', 'admin'].includes(roleParam)) {
    return roleParam
  }

  // 2. Check URL prefix & Specific Login Paths
  const path = window.location.pathname
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/merchant')) return 'merchant'
  
  // Explicitly force 'user' role for common buyer-facing paths to prevent token leakage from other roles
  if (path === '/' || path === '/products' || path === '/orders' || path === '/wallet' || path === '/chat') {
    // Note: /chat handles its own role via query param usually, but default should be user if no param
    const params = new URLSearchParams(window.location.search)
    if (!params.get('role')) return 'user'
  }
  
  // 3. Fallback to localStorage context saved by router
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

const logout = (role) => {
  const r = role || getActiveRole()
  if (state[r]) {
    state[r].user = null
    state[r].token = null
    localStorage.removeItem(`${r}_info`)
    localStorage.removeItem(`${r}_token`)
    
    // If the logged-out role was the active context, reset to user
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
