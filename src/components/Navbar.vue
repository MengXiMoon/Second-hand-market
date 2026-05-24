<template>
  <el-header v-if="!isAuthPage" :class="['navbar', getRoleClass()]">
    <div class="navbar-content">
      <div class="logo" @click="handleLogoClick">
        <el-icon :size="24"><ShoppingCart /></el-icon>
        <span>二手市场</span>
      </div>
      <nav class="nav-links">
        <!-- Root path: show neutral links -->
        <template v-if="isRootPath">
          <el-button type="text" @click="$router.push('/customer/products')">商品列表</el-button>
        </template>
        <!-- Admin Context Links -->
        <template v-else-if="activeRole === 'admin'">
          <el-button type="text" @click="$router.push('/admin/dashboard')">数据看板</el-button>
          <el-button type="text" @click="$router.push('/admin/all-products')">全部商品</el-button>
          <el-button type="text" @click="$router.push('/admin/chat')">消息</el-button>
          <el-button type="text" @click="$router.push('/admin/all-users')">全部用户</el-button>
          <el-button type="text" @click="$router.push('/admin/users')">用户审核</el-button>
          <el-button type="text" @click="$router.push('/admin/products')">商品审核</el-button>
          <el-button type="text" @click="$router.push('/admin/orders')">全站订单</el-button>
        </template>

        <!-- Merchant Context Links -->
        <template v-else-if="activeRole === 'merchant'">
          <el-button type="text" @click="$router.push('/merchant/products')">商品列表</el-button>
          <el-button type="text" @click="$router.push('/merchant/chat')">消息</el-button>
          <el-button type="text" @click="$router.push('/merchant/my-products')">我的商品</el-button>
          <el-button type="text" @click="$router.push('/merchant/sales')">销售记录</el-button>
          <el-button type="text" @click="$router.push('/merchant/reviews')">买家评价</el-button>
          <el-button type="text" @click="$router.push('/merchant/wallet')">钱包</el-button>
        </template>

        <!-- User/Public Context Links -->
        <template v-else>
          <el-button type="text" @click="$router.push('/customer/products')">商品列表</el-button>
          <el-button v-if="!userSession.token" type="text" @click="$router.push('/merchant/login')" style="color: #e6a23c">商家入驻</el-button>
          <template v-if="userSession.token">
            <el-button type="text" @click="$router.push('/customer/cart')">购物车</el-button>
            <el-button type="text" @click="$router.push('/customer/chat')">消息</el-button>
            <el-button type="text" @click="$router.push('/customer/orders')">我的订单</el-button>
            <el-button type="text" @click="$router.push('/customer/wallet')">钱包</el-button>
            <el-button type="text" @click="handleContactSupport" style="color: #67c23a">联系客服</el-button>
          </template>
        </template>
      </nav>

      <div class="user-section">
        <template v-if="isRootPath">
          <div class="role-status-bar">
            <div class="status-chip" :class="{ active: !!userSession.token }">
              <span class="status-dot"></span>
              <span class="status-text">顾客端</span>
              <span v-if="userSession.token" class="status-user">{{ userSession.user?.username }}</span>
            </div>
            <div class="status-chip" :class="{ active: !!merchantSession.token }">
              <span class="status-dot"></span>
              <span class="status-text">商家端</span>
              <span v-if="merchantSession.token" class="status-user">{{ merchantSession.user?.username }}</span>
            </div>
            <div class="status-chip" :class="{ active: !!adminSession.token }">
              <span class="status-dot"></span>
              <span class="status-text">管理端</span>
              <span v-if="adminSession.token" class="status-user">{{ adminSession.user?.username }}</span>
            </div>
          </div>
          <el-button v-if="anyLoggedIn" type="danger" size="small" @click="handleLogoutAll">全部退出</el-button>
        </template>
        <template v-else-if="userInfo">
          <el-badge :value="unreadNotifCount" :hidden="unreadNotifCount === 0" style="margin-right:12px">
            <el-button size="small" circle @click="goNotifications">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <span class="user-info">
            {{ userInfo.username }} ({{ userInfo.role === 'merchant' ? '商家' : (userInfo.role === 'admin' ? '管理员' : '用户') }})
          </span>
          <el-button :type="getLogoutButtonType()" size="small" @click="handleLogout">退出当前端</el-button>
        </template>
        <template v-else>
          <el-button @click="handleLoginClick">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ref, onMounted, computed } from 'vue'
import store from '../store'
import { contactSupport } from '../api/chat'
import { getUnreadCount } from '../api/notifications'

const router = useRouter()
const route = useRoute()
const unreadNotifCount = ref(0)

const goNotifications = () => {
  const role = store.getActiveRole()
  const prefix = role === 'merchant' ? '/merchant' : (role === 'admin' ? '/admin' : '/customer')
  router.push(prefix + '/notifications')
}

const fetchUnreadCount = async () => {
  const session = store.getCurrentSession()
  if (!session.token) return
  try {
    const { data } = await getUnreadCount()
    unreadNotifCount.value = data.count
  } catch (_) {}
}

const isRootPath = computed(() => route.path === '/')
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))

// Get session status for ALL roles
const userSession = computed(() => store.state.user)
const merchantSession = computed(() => store.state.merchant)
const adminSession = computed(() => store.state.admin)

// Current active context session
const currentSession = computed(() => store.getCurrentSession())
const userInfo = computed(() => currentSession.value.user)
const activeRole = computed(() => store.getActiveRole())

const isAdmin = computed(() => userInfo.value?.role === 'admin')
const isMerchant = computed(() => userInfo.value?.role === 'merchant')

// Helper to check if ANY role is logged in
const anyLoggedIn = computed(() => !!(userSession.value.token || merchantSession.value.token || adminSession.value.token))

const handleLogoutAll = () => {
  store.logout('user')
  store.logout('merchant')
  store.logout('admin')
  ElMessage.success('已退出所有登录')
  router.push('/')
}

const getRoleClass = () => {
  if (activeRole.value === 'admin') return 'navbar-admin'
  if (activeRole.value === 'merchant') return 'navbar-merchant'
  return 'navbar-user'
}

const handleLogoClick = () => {
  if (activeRole.value === 'admin') router.push('/admin/all-users')
  else if (activeRole.value === 'merchant') router.push('/merchant')
  else router.push('/customer')
}

const handleLoginClick = () => {
  if (activeRole.value === 'admin') router.push('/admin/login')
  else if (activeRole.value === 'merchant') router.push('/merchant/login')
  else router.push('/login')
}

const getLogoutButtonType = () => {
  if (activeRole.value === 'admin') return 'danger'
  if (activeRole.value === 'merchant') return 'warning'
  return 'primary'
}

const handleLogout = () => {
  const role = store.getActiveRole()
  store.logout(role)
  ElMessage.success('已退出登录')
  router.push('/')
}

const handleContactSupport = async () => {
  try {
    await contactSupport()
    router.push('/customer/chat')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '联系客服失败')
  }
}

onMounted(() => {
  fetchUnreadCount()
  setInterval(fetchUnreadCount, 30000)
})
</script>

<style scoped>
.navbar {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  padding: 0;
  height: 70px;
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.navbar-admin {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.9) 0%, rgba(124, 58, 237, 0.95) 100%);
  border-bottom: 1px solid rgba(124, 58, 237, 0.2);
}

.navbar-admin .logo {
  color: #fff;
  text-shadow: 0 2px 10px rgba(79, 70, 229, 0.3);
}

.navbar-admin .nav-links .el-button {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  border-radius: 8px;
  padding: 8px 14px;
}

.navbar-admin .nav-links .el-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}

.navbar-admin .user-info {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.navbar-merchant {
  background: linear-gradient(135deg, rgba(244, 63, 94, 0.9) 0%, rgba(251, 113, 133, 0.95) 100%);
  border-bottom: 1px solid rgba(244, 63, 94, 0.2);
}

.navbar-merchant .logo {
  color: #fff;
  text-shadow: 0 2px 10px rgba(244, 63, 94, 0.3);
}

.navbar-merchant .nav-links .el-button {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  border-radius: 8px;
  padding: 8px 14px;
}

.navbar-merchant .nav-links .el-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}

.navbar-merchant .user-info {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.navbar-user {
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid rgba(94, 91, 245, 0.08);
}

.navbar-user .logo {
  color: #5e5bf5;
  font-weight: 800;
}

.navbar-user .nav-links .el-button {
  color: #475569;
  font-weight: 500;
  border-radius: 8px;
  padding: 8px 14px;
}

.navbar-user .nav-links .el-button:hover {
  color: #5e5bf5;
  background: rgba(94, 91, 245, 0.05);
  transform: translateY(-1px);
}

.navbar-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
  letter-spacing: -0.5px;
  transition: transform 0.2s ease;
}

.logo:hover {
  transform: scale(1.02);
}

.nav-links {
  display: flex;
  gap: 6px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.role-status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 100px;
  background: rgba(148, 163, 184, 0.08);
  font-size: 13px;
  color: #64748b;
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
}

.status-chip.active {
  background: rgba(94, 91, 245, 0.08);
  color: #5e5bf5;
  border: 1px solid rgba(94, 91, 245, 0.15);
  box-shadow: 0 4px 10px -2px rgba(94, 91, 245, 0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
  transition: all 0.3s;
}

.status-chip.active .status-dot {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
}

.status-text {
  font-weight: 600;
}

.status-user {
  font-weight: 700;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 11px;
}
</style>
