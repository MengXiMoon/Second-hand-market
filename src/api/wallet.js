import api from './index'

export const getWallet = () => {
  return api.get('/wallet/me')
}

export const rechargeWallet = (userId, amount, description) => {
  return api.post('/wallet/recharge', null, { params: { user_id: userId, amount, description } })
}

export const selfRecharge = (amount) => {
  return api.post('/wallet/self-recharge', null, { params: { amount } })
}

export const withdraw = (amount) => {
  return api.post('/wallet/withdraw', null, { params: { amount } })
}

export const getTransactions = () => {
  return api.get('/wallet/transactions')
}
