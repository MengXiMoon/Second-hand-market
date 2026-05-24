import api from './index'

export const getProducts = (params = {}) => {
  return api.get('/products', { params })
}

export const getCategories = () => {
  return api.get('/products/categories')
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

export const auditProduct = (productId, approve, remark = '') => {
  return api.put(`/products/${productId}/audit`, null, { params: { approve, remark } })
}

export const updateProduct = (productId, productData) => {
  return api.put(`/products/${productId}`, productData)
}

export const updateProductStatus = (productId, status) => {
  return api.put(`/products/${productId}/status`, null, { params: { status } })
}

export const uploadProductImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/products/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 收藏
export const getFavorites = () => {
  return api.get('/products/favorites')
}

export const addFavorite = (productId) => {
  return api.post('/products/favorites', { product_id: productId })
}

export const removeFavorite = (favoriteId) => {
  return api.delete(`/products/favorites/${favoriteId}`)
}
