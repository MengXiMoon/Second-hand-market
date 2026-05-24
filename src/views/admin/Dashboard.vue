<template>
  <Layout>
    <div class="dashboard">
      <h2>管理看板</h2>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" v-for="card in cards" :key="card.title">
          <el-card :class="['stat-card', card.color]" shadow="hover">
            <div class="stat-icon"><el-icon :size="28"><component :is="card.icon" /></el-icon></div>
            <div class="stat-title">{{ card.title }}</div>
            <div class="stat-value">{{ card.value }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ShoppingCart, Money, Clock, Warning, TrendCharts } from '@element-plus/icons-vue'
import { getAdminStats } from '../../api/users'
import { formatMoney } from '../../utils/format'
import Layout from '../../components/Layout.vue'

const cards = ref([])

const loadStats = async () => {
  try {
    const { data } = await getAdminStats()
    cards.value = [
      { title: '总用户数', value: data.total_users, icon: 'User', color: 'blue' },
      { title: '总订单数', value: data.total_orders, icon: 'ShoppingCart', color: 'green' },
      { title: '今日订单', value: data.today_orders, icon: 'TrendCharts', color: 'purple' },
      { title: '平台收入', value: '¥' + formatMoney(data.total_revenue), icon: 'Money', color: 'orange' },
      { title: '今日收入', value: '¥' + formatMoney(data.today_revenue), icon: 'Money', color: 'teal' },
      { title: '待审核用户', value: data.pending_users, icon: 'Warning', color: 'red' },
      { title: '待审核商品', value: data.pending_products, icon: 'Clock', color: 'yellow' },
    ]
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

onMounted(loadStats)
</script>

<style scoped>
.dashboard h2 { margin-bottom: 24px; }
.stat-card { margin-bottom: 20px; text-align: center; padding: 20px 0; border-radius: 12px; }
.stat-card.blue { border-top: 3px solid #409eff; }
.stat-card.green { border-top: 3px solid #67c23a; }
.stat-card.orange { border-top: 3px solid #e6a23c; }
.stat-card.red { border-top: 3px solid #f56c6c; }
.stat-card.purple { border-top: 3px solid #9b59b6; }
.stat-card.teal { border-top: 3px solid #1abc9c; }
.stat-card.yellow { border-top: 3px solid #f39c12; }
.stat-icon { margin-bottom: 8px; opacity: 0.7; }
.stat-title { color: #909399; font-size: 13px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; }
</style>
