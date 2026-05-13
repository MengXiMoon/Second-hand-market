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
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import store from '../store'
import { contactSupport } from '../api/chat'

const router = useRouter()
const route = useRoute()

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
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 64px;
}

.navbar-admin {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.navbar-admin .logo {
  color: #fff;
}

.navbar-admin .nav-links .el-button {
  color: #fff;
}

.navbar-admin .nav-links .el-button:hover {
  color: #e0e0e0;
  background: rgba(255, 255, 255, 0.1);
}

.navbar-admin .user-info {
  color: #fff;
}

.navbar-merchant {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.navbar-merchant .logo {
  color: #fff;
}

.navbar-merchant .nav-links .el-button {
  color: #fff;
}

.navbar-merchant .nav-links .el-button:hover {
  color: #e0e0e0;
  background: rgba(255, 255, 255, 0.1);
}

.navbar-merchant .user-info {
  color: #fff;
}

.navbar-user {
  background: #fff;
}

.navbar-user .logo {
  color: #409eff;
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
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  font-size: 14px;
}

.role-status-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 16px;
  background: #f5f7fa;
  font-size: 13px;
  color: #909399;
  transition: all 0.3s;
}

.status-chip.active {
  background: #ecf5ff;
  color: #409eff;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c0c4cc;
  transition: background 0.3s;
}

.status-chip.active .status-dot {
  background: #67c23a;
  box-shadow: 0 0 4px rgba(103, 194, 58, 0.6);
}

.status-text {
  font-weight: 500;
}

.status-user {
  font-weight: 600;
  color: #303133;
}
</style>
