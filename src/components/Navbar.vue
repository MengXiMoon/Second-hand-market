<template>
  <el-header class="navbar">
    <div class="navbar-content">
      <div class="logo" @click="$router.push('/')">
        <el-icon :size="24"><ShoppingCart /></el-icon>
        <span>二手市场</span>
      </div>
      <nav class="nav-links">
        <el-button type="text" @click="$router.push('/products')">商品列表</el-button>
        <template v-if="user">
          <el-button v-if="isMerchantOrAdmin" type="text" @click="$router.push('/my-products')">我的商品</el-button>
          <el-button v-if="isMerchantOrAdmin" type="text" @click="$router.push('/sales')">销售记录</el-button>
          <el-button type="text" @click="$router.push('/orders')">我的订单</el-button>
          <el-button type="text" @click="$router.push('/wallet')">钱包</el-button>
          <template v-if="isAdmin">
            <el-button type="text" @click="$router.push('/admin/users')">用户审核</el-button>
            <el-button type="text" @click="$router.push('/admin/products')">商品审核</el-button>
          </template>
        </template>
      </nav>
      <div class="user-section">
        <template v-if="user">
          <span class="user-info">
            {{ user.username }} ({{ user.role }})
          </span>
          <el-button type="primary" size="small" @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button @click="$router.push('/login')">登录</el-button>
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

const user = computed(() => store.state.user)

const isAdmin = computed(() => user.value?.role === 'admin')
const isMerchantOrAdmin = computed(() => 
  user.value?.role === 'merchant' || user.value?.role === 'admin'
)

const handleLogout = () => {
  store.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.navbar {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 64px;
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
  color: #409eff;
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
  color: #606266;
  font-size: 14px;
}
</style>
