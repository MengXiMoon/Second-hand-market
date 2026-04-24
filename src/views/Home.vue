<template>
  <Layout>
    <div class="home">
      <el-row :gutter="20" class="hero-section">
        <el-col :span="24">
          <div class="hero-content">
            <h1>欢迎来到二手市场</h1>
            <p>发现优质二手商品，轻松买卖，闲置变宝</p>
            <el-button type="primary" size="large" @click="$router.push('/products')">
              浏览商品
            </el-button>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="features">
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card">
            <el-icon :size="40" color="#409eff"><Shop /></el-icon>
            <h3>丰富商品</h3>
            <p>各类二手商品应有尽有</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card">
            <el-icon :size="40" color="#67c23a"><Wallet /></el-icon>
            <h3>安全交易</h3>
            <p>内置钱包系统，交易有保障</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card">
            <el-icon :size="40" color="#e6a23c"><User /></el-icon>
            <h3>多重角色</h3>
            <p>买家、卖家、管理员一应俱全</p>
            <div class="role-entry">
              <el-button type="primary" plain size="small" @click="$router.push('/login')">顾客入口</el-button>
              <el-button type="warning" plain size="small" @click="$router.push('/merchant/login')">商家入口</el-button>
              <el-button type="danger" plain size="small" @click="$router.push('/admin/login')">后台管理</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { computed } from 'vue'
import Layout from '../components/Layout.vue'
import store from '../store'

const anyLoggedIn = computed(() => {
  return !!(store.state.user.token || store.state.merchant.token || store.state.admin.token)
})
</script>

<style scoped>
.home {
  text-align: center;
}

.hero-section {
  padding: 60px 0;
}

.hero-content h1 {
  font-size: 48px;
  margin-bottom: 16px;
  color: #303133;
}

.hero-content p {
  font-size: 18px;
  color: #606266;
  margin-bottom: 32px;
}

.features {
  margin-top: 40px;
}

.feature-card {
  text-align: center;
  padding: 40px 20px;
}

.feature-card h3 {
  margin: 16px 0 8px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  margin-bottom: 20px;
}

.role-entry {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
