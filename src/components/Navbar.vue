<template>
  <el-header :class="['navbar', getRoleClass()]">
    <div class="navbar-content">
      <div class="logo" @click="handleLogoClick">
        <el-icon :size="24"><ShoppingCart /></el-icon>
        <span>二手市场</span>
      </div>
      <nav class="nav-links">
        <!-- 路由路径隔离：基于当前 URL 前缀展示对应的端入口，实现视觉上的多端分离 -->
        <!-- Admin Context Links -->
        <template v-if="activeRole === 'admin'">
          <el-button type="text" @click="$router.push('/admin/all-products')">全部商品</el-button>
          <el-button type="text" @click="$router.push('/chat?role=admin')">消息</el-button>
          <el-button type="text" @click="$router.push('/admin/all-users')">全部用户</el-button>
          <el-button type="text" @click="$router.push('/admin/users')">用户审核</el-button>
          <el-button type="text" @click="$router.push('/admin/products')">商品审核</el-button>
          <el-button type="text" @click="$router.push('/admin/orders')">全站订单</el-button>
        </template>

        <!-- Merchant Context Links -->
        <template v-else-if="activeRole === 'merchant'">
          <el-button type="text" @click="$router.push('/merchant/products')">商品列表</el-button>
          <el-button type="text" @click="$router.push('/chat?role=merchant')">消息</el-button>
          <el-button type="text" @click="$router.push('/merchant/my-products')">我的商品</el-button>
          <el-button type="text" @click="$router.push('/merchant/sales')">销售记录</el-button>
          <el-button type="text" @click="$router.push('/merchant/wallet')">钱包</el-button>
        </template>

        <!-- User/Public Context Links -->
        <template v-else>
          <el-button type="text" @click="$router.push('/products')">商品列表</el-button>
          <el-button v-if="!userSession.token" type="text" @click="$router.push('/merchant/login')" style="color: #e6a23c">商家入驻</el-button>
          <template v-if="userSession.token">
            <el-button type="text" @click="$router.push('/chat?role=user')">消息</el-button>
            <el-button type="text" @click="$router.push('/orders')">我的订单</el-button>
            <el-button type="text" @click="$router.push('/wallet')">钱包</el-button>
          </template>
        </template>
      </nav>

      <div class="user-section">
        <template v-if="userInfo">
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import store from '../store'

const router = useRouter()

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

const getRoleClass = () => {
  if (activeRole.value === 'admin') return 'navbar-admin'
  if (activeRole.value === 'merchant') return 'navbar-merchant'
  return 'navbar-user'
}

const handleLogoClick = () => {
  if (activeRole.value === 'admin') router.push('/admin/all-users')
  else if (activeRole.value === 'merchant') router.push('/merchant')
  else router.push('/')
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
  router.push('/login')
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
</style>
