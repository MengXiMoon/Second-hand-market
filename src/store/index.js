import { reactive } from 'vue'

const state = reactive({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token')
})

const setUser = (user, token) => {
  state.user = user
  state.token = token
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
}

const logout = () => {
  state.user = null
  state.token = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}

export default {
  state,
  setUser,
  logout
}
