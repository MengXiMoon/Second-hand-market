import api from './index'

export const createOrder = (productId) => {
  return api.post('/orders', { product_id: productId })
}

export const getMyOrders = () => {
  return api.get('/orders/my')
}

export const getMySales = () => {
  return api.get('/orders/sales')
}

export const getAllOrders = () => {
  return api.get('/orders/all')
}
