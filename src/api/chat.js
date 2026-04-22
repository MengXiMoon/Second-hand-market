import api from './index'

export const getConversations = () => {
  return api.get('/chat/conversations')
}

export const getMessages = (conversationId, skip = 0, limit = 50) => {
  return api.get(`/chat/messages/${conversationId}`, {
    params: { skip, limit }
  })
}

export const startConversation = (recipientId) => {
  return api.post('/chat/start', null, {
    params: { recipient_id: recipientId }
  })
}

export const uploadChatImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/chat/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
