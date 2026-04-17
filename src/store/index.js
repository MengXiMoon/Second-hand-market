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
  const path = window.location.pathname
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/merchant')) return 'merchant'
  return 'user'
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
  getActiveRole
}
