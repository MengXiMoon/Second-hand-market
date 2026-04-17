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
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type) {
      /**
       * 严格隔离逻辑：仅当通知类型与当前页面所属的角色端一致时，才显示弹窗。
       * 比如：用户在买东西（user端）时，不会被商家的订单消息通知打扰，实现纯净的多端分离体验。
       */
      const roleMap = {
        'new_order': 'merchant',   // 新订单属于商家端
        'product_audit': 'merchant', // 商品审核属于商家端
        'admin_event': 'admin'      // 管理事件属于管理端
      }
      
      const targetRole = roleMap[data.type]
      const currentRole = store.getActiveRole()
      
      // 只有在匹配的角色端页面，才弹出 UI 提醒
      if (targetRole && currentRole === targetRole) {
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
          duration: 4500, // 自动消失，避免堆积
          position: 'bottom-right'
        })
      }
      
      // 增加 300ms 延迟，确保后端数据库写入完全完成后再刷新前端数据
      // 解决管理员端看到通知但列表没刷新的“竞态”问题
      clearTimeout(refreshTimer)
      refreshTimer = setTimeout(() => {
        window.dispatchEvent(new CustomEvent('refresh-data'))
      }, 300)
    }
  }

  ws.onclose = () => {
    if (sockets[uid] === ws) {
      delete sockets[uid]
    }
    // Reconnect after 5 seconds if anyone still needs this UID
    setTimeout(() => {
      checkAndReconnect(uid)
    }, 5000)
  }

  sockets[uid] = ws
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

  // Close sockets for users that are no longer logged in any role
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
  // Watch all role slots for changes in login state
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
