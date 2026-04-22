<script setup>
import { RouterView } from 'vue-router'
import { onMounted, watch, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'
import store from './store'

const sockets = {}
let refreshTimer = null

const connectWebSocket = (uid) => {
  if (sockets[uid]) return 
  
  const ws = new WebSocket(`ws://localhost:8000/v1/ws/${uid}`)
  sockets[uid] = ws
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    const roleMap = {
      'new_order': 'merchant',
      'product_audit': 'merchant',
      'admin_event': 'admin',
      'chat_message': 'any',
      'typing': 'any'
    }
    
    const eventType = data.type
    const targetRole = roleMap[eventType]
    const currentRole = store.getActiveRole()
    
    // Dispatch specific chat events
    if (['chat_message', 'typing'].includes(eventType)) {
      window.dispatchEvent(new CustomEvent(`chat-${eventType.replace('_', '-')}`, { detail: data.data }))
      
      if (eventType === 'chat_message' && window.location.pathname !== '/chat') {
        ElNotification({
          title: '新消息',
          message: data.data.content.length > 20 ? data.data.content.substring(0, 20) + '...' : data.data.content,
          type: 'info',
          position: 'bottom-right',
          onClick: () => { window.location.href = '/chat' }
        })
      }
      return
    }

    if (targetRole && (targetRole === 'any' || currentRole === targetRole)) {
      const typeMap = {
        'new_order': { title: '新订单通知', type: 'success' },
        'product_audit': { title: '商品审核通知', type: data.data.status === 'approved' ? 'success' : 'warning' },
        'admin_event': { title: '管理提醒', type: 'info' }
      }
      const config = typeMap[data.type] || { title: '通知', type: 'info' }
      
      ElNotification({
        title: config.title,
        message: data.message,
        type: config.type,
        duration: 4500,
        position: 'bottom-right'
      })
    }
    
    clearTimeout(refreshTimer)
    refreshTimer = setTimeout(() => {
      window.dispatchEvent(new CustomEvent('refresh-data'))
    }, 300)
  }

  ws.onclose = () => {
    if (sockets[uid] === ws) {
      delete sockets[uid]
    }
    setTimeout(() => {
      checkAndReconnect(uid)
    }, 5000)
  }
}

const checkAndReconnect = (uid) => {
  const roles = ['user', 'merchant', 'admin']
  const stillLoggedIn = roles.some(role => {
    const session = store.state[role]
    return session?.token && session?.user && session.user.id === uid
  })
  if (stillLoggedIn && !sockets[uid]) {
    connectWebSocket(uid)
  }
}

const updateConnections = () => {
  const roles = ['user', 'merchant', 'admin']
  const activeUserIds = new Set()
  
  roles.forEach(role => {
    const session = store.state[role]
    if (session?.token && session?.user) {
      const uid = session.user.id
      activeUserIds.add(uid)
      if (!sockets[uid]) {
        connectWebSocket(uid)
      }
    }
  })

  Object.keys(sockets).forEach(uidStr => {
    const uid = Number(uidStr)
    if (!activeUserIds.has(uid)) {
      if (sockets[uid]) {
        sockets[uid].close()
        delete sockets[uid]
      }
    }
  })
}

onMounted(() => {
  updateConnections()
  
  window.sendChatAction = (uid, action) => {
    const ws = sockets[uid]
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(action))
      return true
    }
    return false
  }

  watch(() => [store.state.user.token, store.state.merchant.token, store.state.admin.token], () => {
    updateConnections()
  })
})

onUnmounted(() => {
  Object.values(sockets).forEach(ws => ws.close())
})
</script>

<template>
  <RouterView />
</template>
