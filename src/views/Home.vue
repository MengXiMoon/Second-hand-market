<template>
  <Layout>
    <div class="home">
      <el-row :gutter="20" class="hero-section">
        <el-col :span="24">
          <div class="hero-content">
            <h1>欢迎来到二手市场</h1>
            <p>发现优质二手商品，轻松买卖，闲置变宝</p>
            <div class="hero-buttons">
              <el-button type="primary" size="large" @click="$router.push('/customer/products')">
                浏览商品
              </el-button>
              <el-button type="success" size="large" @click="$router.push('/login')">
                登录账号
              </el-button>
            </div>
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
            <h3>登录状态</h3>
            <div class="role-status">
              <div class="status-item">
                <span class="status-label">顾客端</span>
                <el-tag v-if="userSession.token" type="success" size="small">
                  {{ userInfoForRole('user') }}
                </el-tag>
                <el-tag v-else type="info" size="small">未登录</el-tag>
              </div>
              <div class="status-item">
                <span class="status-label">商家端</span>
                <el-tag v-if="merchantSession.token" type="success" size="small">
                  {{ userInfoForRole('merchant') }}
                </el-tag>
                <el-tag v-else type="info" size="small">未登录</el-tag>
              </div>
              <div class="status-item">
                <span class="status-label">管理端</span>
                <el-tag v-if="adminSession.token" type="success" size="small">
                  {{ userInfoForRole('admin') }}
                </el-tag>
                <el-tag v-else type="info" size="small">未登录</el-tag>
              </div>
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

const userSession = computed(() => store.state.user)
const merchantSession = computed(() => store.state.merchant)
const adminSession = computed(() => store.state.admin)

const userInfoForRole = (role) => {
  const session = store.state[role]
  if (session && session.user) {
    return session.user.username
  }
  return ''
}
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

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
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

.role-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 14px;
  color: #606266;
}
</style>
