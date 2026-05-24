import api from './index'

export const createReview = (data) => {
  return api.post('/reviews', data)
}

export const replyReview = (reviewId, reply) => {
  return api.put(`/reviews/${reviewId}/reply`, { reply })
}

export const getProductReviews = (productId) => {
  return api.get(`/reviews/product/${productId}`)
}

export const getMyReviews = () => {
  return api.get('/reviews/my')
}

export const checkReviewed = (orderId) => {
  return api.get(`/reviews/check/${orderId}`)
}
