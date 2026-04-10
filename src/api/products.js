import api from './index'

export const getProducts = (skip = 0, limit = 100) => {
  return api.get('/products', { params: { skip, limit } })
}

export const getMyProducts = () => {
  return api.get('/products/my')
}

export const getPendingProducts = () => {
  return api.get('/products/pending')
}

export const createProduct = (productData) => {
  return api.post('/products', productData)
}

export const auditProduct = (productId, approve) => {
  return api.put(`/products/${productId}/audit`, null, { params: { approve } })
}

export const updateProductStatus = (productId, status) => {
  return api.put(`/products/${productId}/status`, null, { params: { status } })
}
