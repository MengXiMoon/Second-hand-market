<script setup>
import { RouterView } from 'vue-router'
import { onMounted, watch, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'
import store from './store'

const sockets = {}

const connectWebSocket = (role, user) => {
  if (sockets[role]) return // Already connected
  
  const ws = new WebSocket(`ws://localhost:8000/v1/ws/${user.id}`)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type) {
      /**
       * 严格隔离逻辑：仅当通知类型与当前页面所属的角色端一致时，才显示弹窗。
       * 比如：用户在买东西（user端）时，不会被商家的订单消息通知打扰，实现纯净的多端分离体验。
       */
      const roleMap = {
        'new_order': 'merchant',   // 新订单属于商家端
        'product_audit': 'merchant' // 商品审核属于商家端
      }
      
      const targetRole = roleMap[data.type]
      const currentRole = store.getActiveRole()
      
      // 只有在匹配的角色端页面，才弹出 UI 提醒
      if (targetRole && currentRole === targetRole) {
        const typeMap = {
          'new_order': { title: '新订单通知', type: 'success' },
          'product_audit': { title: '商品审核通知', type: data.data.status === 'approved' ? 'success' : 'warning' }
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
      
      // 无论是否弹出窗口，都在后台触发全局数据更新（确保切换标签页时数据已刷新）
      window.dispatchEvent(new CustomEvent('refresh-data'))
    }
  }

  ws.onclose = () => {
    delete sockets[role]
    // Reconnect after 5 seconds if still logged in
    setTimeout(() => {
      const currentSession = store.state[role]
      if (currentSession?.token && currentSession?.user) {
        connectWebSocket(role, currentSession.user)
      }
    }, 5000)
  }

  sockets[role] = ws
}

const updateConnections = () => {
  const roles = ['user', 'merchant', 'admin']
  roles.forEach(role => {
    const session = store.state[role]
    if (session?.token && session?.user) {
      connectWebSocket(role, session.user)
    } else if (sockets[role]) {
      sockets[role].close()
      delete sockets[role]
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
