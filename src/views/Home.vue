<template>
  <Layout>
    <div class="home animate-fade-in-up">
      <div class="hero-section">
        <div class="hero-bg-overlay"></div>
        <div class="hero-content">
          <div class="brand-badge">✨ 全智能闲置商品流转中心</div>
          <h1 class="hero-title">让闲置重新闪光，开启绿色新交易</h1>
          <p class="hero-desc">在这里，您可以快速浏览数千款优质二手好物，保障交易资金安全，闲置物品一键变现，开启极简新生活方式。</p>
          <div class="hero-buttons">
            <el-button type="primary" size="large" class="premium-gradient-btn" @click="$router.push('/customer/products')">
              <el-icon style="margin-right: 6px;"><Goods /></el-icon> 立即浏览好物
            </el-button>
            <el-button size="large" class="secondary-glass-btn" @click="$router.push('/login')">
              注册 / 登录入口 <el-icon style="margin-left: 6px;"><Right /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <el-row :gutter="24" class="features">
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card" shadow="hover">
            <div class="icon-wrapper primary-glow">
              <el-icon :size="28" color="#5e5bf5"><Shop /></el-icon>
            </div>
            <h3>丰富海量好物</h3>
            <p>电子数码、图书、日用百货，各类闲置优质好物经严格审核，应有尽有</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card" shadow="hover">
            <div class="icon-wrapper success-glow">
              <el-icon :size="28" color="#10b981"><Wallet /></el-icon>
            </div>
            <h3>安全交易钱包</h3>
            <p>集成高水准模拟钱包结算，资金闭环控制，保障买卖双方权益无忧</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="feature-card" shadow="hover">
            <div class="icon-wrapper warning-glow">
              <el-icon :size="28" color="#f59e0b"><User /></el-icon>
            </div>
            <h3>尊享多端登录</h3>
            <div class="role-status">
              <div class="status-item">
                <span class="status-label">顾客端</span>
                <el-tag v-if="userSession.token" type="success" size="small">
                  {{ userInfoForRole('user') }} (已登录)
                </el-tag>
                <el-tag v-else type="info" size="small">未登录</el-tag>
              </div>
              <div class="status-item">
                <span class="status-label">商家端</span>
                <el-tag v-if="merchantSession.token" type="success" size="small">
                  {{ userInfoForRole('merchant') }} (已登录)
                </el-tag>
                <el-tag v-else type="info" size="small">未登录</el-tag>
              </div>
              <div class="status-item">
                <span class="status-label">管理端</span>
                <el-tag v-if="adminSession.token" type="danger" size="small">
                  {{ userInfoForRole('admin') }} (管理员)
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
import { Goods, Right, Shop, Wallet, User } from '@element-plus/icons-vue'
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}

.hero-section {
  position: relative;
  border-radius: 24px;
  padding: 80px 40px;
  margin-bottom: 40px;
  background: radial-gradient(circle at 0% 0%, rgba(94, 91, 245, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 100% 100%, rgba(244, 63, 94, 0.08) 0%, transparent 50%),
              rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  overflow: hidden;
  text-align: center;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 100px;
  background: rgba(94, 91, 245, 0.08);
  color: #5e5bf5;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 20px;
  border: 1px solid rgba(94, 91, 245, 0.12);
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: 46px;
  line-height: 1.25;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #1e293b 0%, #3b82f6 50%, #5e5bf5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  letter-spacing: -1px;
}

.hero-desc {
  max-width: 680px;
  margin: 0 auto 36px;
  font-size: 16px;
  line-height: 1.6;
  color: #64748b;
  font-weight: 450;
}

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.secondary-glass-btn {
  background: rgba(255, 255, 255, 0.6) !important;
  border: 1px solid rgba(94, 91, 245, 0.15) !important;
  color: #475569 !important;
  backdrop-filter: blur(8px);
}

.secondary-glass-btn:hover {
  background: rgba(255, 255, 255, 0.9) !important;
  border-color: #5e5bf5 !important;
  color: #5e5bf5 !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(94, 91, 245, 0.15);
}

.features {
  margin-top: 20px;
}

.feature-card {
  padding: 30px 20px;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 20px !important;
}

.icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.primary-glow {
  background: rgba(94, 91, 245, 0.08);
  box-shadow: 0 8px 20px -4px rgba(94, 91, 245, 0.15);
}

.success-glow {
  background: rgba(16, 185, 129, 0.08);
  box-shadow: 0 8px 20px -4px rgba(16, 185, 129, 0.15);
}

.warning-glow {
  background: rgba(245, 158, 11, 0.08);
  box-shadow: 0 8px 20px -4px rgba(245, 158, 11, 0.15);
}

.feature-card:hover .icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 14px;
  line-height: 1.5;
  color: #64748b;
  margin-bottom: 0;
  text-align: center;
}

.role-status {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  margin-top: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.06);
}

.status-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}
</style>
