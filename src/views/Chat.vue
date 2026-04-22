<template>
  <Layout>
    <div class="chat-container">
      <el-container class="chat-wrapper">
        <!-- Sidebar: Conversation List -->
        <el-aside width="300px" class="conversation-aside">
          <div class="aside-header">
            <h3>消息列表</h3>
          </div>
          <el-scrollbar>
            <div 
              v-for="conv in conversations" 
              :key="conv.id" 
              :class="['conversation-item', { active: currentConversation?.id === conv.id }]"
              @click="selectConversation(conv)"
            >
              <el-badge :is-dot="hasUnread(conv)" class="item-badge">
                <el-avatar :size="40">{{ conv.other_user?.username?.charAt(0).toUpperCase() }}</el-avatar>
              </el-badge>
              <div class="item-info">
                <div class="item-top">
                  <span class="username">{{ conv.other_user?.username }}</span>
                  <span class="time">{{ formatTime(conv.updated_at) }}</span>
                </div>
                <div class="last-msg">
                  <span v-if="typingStatus[conv.id]" class="typing-text">正在输入...</span>
                  <span v-else>{{ conv.last_message?.content || '暂无消息' }}</span>
                </div>
              </div>
            </div>
            <el-empty v-if="conversations.length === 0" description="暂无会话" />
          </el-scrollbar>
        </el-aside>

        <!-- Main: Chat Box -->
        <el-main class="chat-main">
          <template v-if="currentConversation">
            <div class="chat-header">
              <div class="header-info">
                <span class="header-username">{{ currentConversation.other_user?.username }}</span>
                <el-tag size="small" type="info">{{ currentConversation.other_user?.role === 'merchant' ? '商家' : '用户' }}</el-tag>
                <span v-if="typingStatus[currentConversation.id]" class="typing-indicator">对方正在输入...</span>
              </div>
            </div>

            <div class="message-list" ref="messageListRef">
              <div v-if="hasMore" class="load-more">
                <el-link type="primary" @click="loadHistory">加载更多历史消息</el-link>
              </div>
              <div 
                v-for="msg in messages" 
                :key="msg.id" 
                :class="['message-item', { 'message-mine': msg.sender_id === userId }]"
              >
                <el-avatar :size="32" class="message-avatar">
                  {{ msg.sender_id === userId ? '我' : msg.sender_name?.charAt(0) }}
                </el-avatar>
                <div class="message-content">
                  <div class="message-bubble">
                    <template v-if="msg.msg_type === 'image'">
                      <el-image 
                        :src="getFullUrl(msg.content)" 
                        :preview-src-list="[getFullUrl(msg.content)]"
                        class="chat-image"
                      />
                    </template>
                    <template v-else>
                      {{ msg.content }}
                    </template>
                  </div>
                  <div class="message-time">{{ formatFullTime(msg.timestamp) }}</div>
                </div>
              </div>
            </div>

            <div class="chat-footer">
              <div class="toolbar">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleImageUpload"
                  accept="image/*"
                >
                  <el-button circle><el-icon><Picture /></el-icon></el-button>
                </el-upload>
              </div>
              <div class="input-area">
                <el-input
                  v-model="inputText"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入消息..."
                  @keydown.enter.prevent="handleSend"
                  @input="handleTyping"
                />
                <div class="send-btn">
                  <el-button type="primary" @click="handleSend" :disabled="!inputText.trim()">发送 (Enter)</el-button>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="empty-chat">
            <el-empty description="选择一个会话开始聊天吧" />
          </div>
        </el-main>
      </el-container>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import Layout from '../components/Layout.vue'
import { getConversations, getMessages, startConversation, uploadChatImage } from '../api/chat'
import store from '../store'

const route = useRoute()
const userId = computed(() => store.getCurrentSession().user?.id)

const conversations = ref([])
const currentConversation = ref(null)
const messages = ref([])
const inputText = ref('')
const messageListRef = ref(null)
const loading = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const limit = 50

const typingStatus = ref({}) // { conversation_id: boolean }
let typingTimer = null

// Real-time events
const handleNewMessage = (event) => {
  const newMsg = event.detail
  if (currentConversation.value && newMsg.conversation_id === currentConversation.value.id) {
    // Prevent duplicate messages (especially important when server echos back to sender)
    const exists = messages.value.some(m => m.id === newMsg.id)
    if (!exists) {
      messages.value.push(newMsg)
      scrollToBottom()
    }
  }
  // Refresh conversations list to show last message
  loadConversations()
}

const handleTypingEvent = (event) => {
  const data = event.detail
  if (data.user_id !== userId.value) {
    typingStatus.value[data.conversation_id] = data.is_typing
    // Auto clear after 3 seconds if no more typing events
    setTimeout(() => {
      typingStatus.value[data.conversation_id] = false
    }, 3000)
  }
}

const loadConversations = async () => {
  try {
    const { data } = await getConversations()
    conversations.value = data
    
    // If we have a target user ID in route, start/get that conversation
    if (route.query.target_id && !currentConversation.value) {
      const targetId = parseInt(route.query.target_id)
      const existing = conversations.value.find(c => c.other_user.id === targetId)
      if (existing) {
        selectConversation(existing)
      } else {
        const { data: newConv } = await startConversation(targetId)
        loadConversations()
        selectConversation(newConv)
      }
    }
  } catch (error) {
    console.error('加载会话失败', error)
  }
}

const selectConversation = (conv) => {
  currentConversation.value = conv
  messages.value = []
  skip.value = 0
  hasMore.value = true
  loadHistory()
}

const loadHistory = async () => {
  if (!currentConversation.value) return
  try {
    const { data } = await getMessages(currentConversation.value.id, skip.value, limit)
    if (data.length < limit) hasMore.value = false
    
    // Add to top while keeping scroll position (simplified: just concat and scroll for now)
    messages.value = [...data, ...messages.value]
    skip.value += data.length
    
    if (skip.value === data.length) {
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('加载消息失败')
  }
}

const handleSend = async () => {
  if (!inputText.value.trim() || !currentConversation.value) return
  
  const action = {
    type: 'chat_message',
    conversation_id: currentConversation.value.id,
    content: inputText.value,
    msg_type: 'text'
  }
  
  const success = window.sendChatAction(userId.value, action)
  if (success) {
    inputText.value = ''
    sendTypingStatus(false)
  } else {
    ElMessage.error('发送失败，请检查网络连接')
  }
}

const handleImageUpload = async (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  
  try {
    const { data } = await uploadChatImage(file)
    const action = {
      type: 'chat_message',
      conversation_id: currentConversation.value.id,
      content: data.url,
      msg_type: 'image'
    }
    window.sendChatAction(userId.value, action)
  } catch (error) {
    ElMessage.error('图片上传失败')
  }
}

const handleTyping = () => {
  sendTypingStatus(true)
  clearTimeout(typingTimer)
  typingTimer = setTimeout(() => {
    sendTypingStatus(false)
  }, 2000)
}

const sendTypingStatus = (status) => {
  if (!currentConversation.value) return
  window.sendChatAction(userId.value, {
    type: 'typing',
    conversation_id: currentConversation.value.id,
    is_typing: status
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const formatFullTime = (dateStr) => {
  return new Date(dateStr).toLocaleString([], { 
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
  })
}

const getFullUrl = (url) => {
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const hasUnread = (conv) => {
  return false // TODO: Backend implementation for unread counts
}

onMounted(() => {
  loadConversations()
  window.addEventListener('chat-chat-message', handleNewMessage)
  window.addEventListener('chat-typing', handleTypingEvent)
})

onUnmounted(() => {
  window.removeEventListener('chat-chat-message', handleNewMessage)
  window.removeEventListener('chat-typing', handleTypingEvent)
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 120px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.chat-wrapper {
  height: 100%;
}

.conversation-aside {
  border-right: 1px solid #ebeef5;
  background: #fcfcfc;
}

.aside-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.aside-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.conversation-item {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f5f7fa;
}

.conversation-item.active {
  background: #ecf5ff;
  border-right: 2px solid #409eff;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.username {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.time {
  font-size: 12px;
  color: #909399;
}

.last-msg {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.typing-text {
  color: #409eff;
}

.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  background: #fdfdfd;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-username {
  font-size: 18px;
  font-weight: 600;
}

.typing-indicator {
  font-size: 12px;
  color: #409eff;
  margin-left: 8px;
}

.message-list {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.load-more {
  text-align: center;
  margin-bottom: 10px;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message-mine {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-bubble {
  padding: 10px 16px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  font-size: 15px;
  line-height: 1.5;
  color: #303133;
  word-break: break-word;
}

.message-mine .message-bubble {
  background: #409eff;
  color: #fff;
  border: none;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}

.message-mine .message-time {
  text-align: right;
}

.chat-image {
  max-width: 200px;
  border-radius: 4px;
  cursor: pointer;
}

.chat-footer {
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.toolbar {
  margin-bottom: 8px;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.send-btn {
  align-self: flex-end;
}

.empty-chat {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
