<template>
  <Layout>
    <div class="wallet">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-card class="balance-card">
            <div class="balance-label">钱包余额</div>
            <div class="balance-amount">¥{{ wallet?.balance || 0 }}</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 style="margin-top: 32px; margin-bottom: 16px;">交易记录</h3>
      
      <el-table :data="displayTransactions" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.amount > 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="时间" />
      </el-table>

      <el-empty v-if="!loading && displayTransactions.length === 0" description="暂无交易记录" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWallet, getTransactions } from '../api/wallet'
import store from '../store'
import Layout from '../components/Layout.vue'

const loading = ref(false)
const wallet = ref(null)
const transactions = ref([])
const user = computed(() => store.state.user)

const displayTransactions = computed(() => {
  if (user.value?.role === 'admin') {
    return transactions.value
  }
  return wallet.value?.transactions || []
})

const loadWallet = async () => {
  loading.value = true
  try {
    const { data } = await getWallet()
    wallet.value = data
  } catch (error) {
    ElMessage.error('加载钱包信息失败')
  } finally {
    loading.value = false
  }
}

const loadTransactions = async () => {
  if (user.value?.role === 'admin') {
    try {
      const { data } = await getTransactions()
      transactions.value = data
    } catch (error) {
      ElMessage.error('加载交易记录失败')
    }
  }
}

onMounted(() => {
  loadWallet()
  loadTransactions()
})
</script>

<style scoped>
.balance-card {
  text-align: center;
  padding: 40px;
}

.balance-label {
  color: #909399;
  font-size: 16px;
  margin-bottom: 8px;
}

.balance-amount {
  font-size: 48px;
  font-weight: 600;
  color: #409eff;
}
</style>
