import api from './index'

export const createOrder = (productId) => {
  return api.post('/orders', { product_id: productId })
}

export const payOrder = (orderId) => {
  return api.put(`/orders/${orderId}/pay`)
}

export const shipOrder = (orderId, trackingNumber) => {
  return api.put(`/orders/${orderId}/ship`, null, { params: { tracking_number: trackingNumber } })
}

export const completeOrder = (orderId) => {
  return api.put(`/orders/${orderId}/complete`)
}

export const cancelOrder = (orderId) => {
  return api.put(`/orders/${orderId}/cancel`)
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

// 购物车
export const getCart = () => {
  return api.get('/orders/cart')
}

export const addToCart = (productId, quantity = 1) => {
  return api.post('/orders/cart', { product_id: productId, quantity })
}

export const updateCartItem = (itemId, quantity) => {
  return api.put(`/orders/cart/${itemId}`, { quantity })
}

export const removeCartItem = (itemId) => {
  return api.delete(`/orders/cart/${itemId}`)
}

export const cartCheckout = (itemIds) => {
  return api.post('/orders/cart/checkout', { item_ids: itemIds })
}
