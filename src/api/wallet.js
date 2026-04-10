import api from './index'

export const getWallet = () => {
  return api.get('/wallet/me')
}

export const rechargeWallet = (userId, amount, description) => {
  return api.post('/wallet/recharge', null, { params: { user_id: userId, amount, description } })
}

export const getTransactions = () => {
  return api.get('/wallet/transactions')
}
