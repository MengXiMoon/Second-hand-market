<template>
  <Layout>
    <div class="notif-page">
      <div class="notif-header">
        <h2>通知中心</h2>
        <el-button v-if="hasUnread" type="primary" size="small" @click="handleMarkAllRead">全部已读</el-button>
      </div>

      <div v-loading="loading">
        <div v-for="n in notifications" :key="n.id" :class="['notif-item', { unread: !n.is_read }]" @click="handleRead(n)">
          <div class="notif-icon">
            <el-icon :size="20" :color="n.is_read ? '#c0c4cc' : '#409eff'"><Bell /></el-icon>
          </div>
          <div class="notif-body">
            <div class="notif-title">
              {{ n.title }}
              <span v-if="!n.is_read" class="unread-dot">●</span>
            </div>
            <div class="notif-content">{{ n.content }}</div>
            <div class="notif-time">{{ formatTime(n.created_at) }}</div>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && notifications.length === 0" description="暂无通知" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getNotifications, markRead, markAllRead } from '../api/notifications'
import Layout from '../components/Layout.vue'

const loading = ref(false)
const notifications = ref([])
const hasUnread = computed(() => notifications.value.some(n => !n.is_read))

const loadNotifications = async () => {
  loading.value = true
  try {
    const { data } = await getNotifications()
    notifications.value = data
  } catch (error) {
    ElMessage.error('加载通知失败')
  } finally {
    loading.value = false
  }
}

const handleRead = async (n) => {
  if (!n.is_read) {
    try {
      await markRead(n.id)
      n.is_read = true
    } catch (_) {}
  }
}

const handleMarkAllRead = async () => {
  try {
    await markAllRead()
    notifications.value.forEach(n => n.is_read = true)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const formatTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(loadNotifications)
</script>

<style scoped>
.notif-page { max-width: 700px; margin: 0 auto; }
.notif-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.notif-header h2 { margin: 0; }
.notif-item { display: flex; gap: 12px; padding: 14px 16px; border-radius: 8px; cursor: pointer; margin-bottom: 6px; border: 1px solid #ebeef5; }
.notif-item.unread { background: #ecf5ff; border-color: #d9ecff; }
.notif-body { flex: 1; min-width: 0; }
.notif-title { font-weight: 600; color: #303133; margin-bottom: 4px; }
.notif-content { color: #606266; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notif-time { color: #c0c4cc; font-size: 12px; margin-top: 4px; }
.unread-dot { color: #409eff; font-size: 10px; margin-left: 4px; }
</style>
