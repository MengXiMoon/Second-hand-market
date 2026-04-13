<template>
  <Layout>
    <div class="wallet">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-card class="balance-card">
            <div class="balance-label">钱包余额</div>
            <div class="balance-amount">¥{{ wallet?.balance || 0 }}</div>
            <div style="margin-top: 20px;">
              <el-button type="primary" size="large" @click="showRechargeDialog = true">充值</el-button>
              <el-button type="success" size="large" plain @click="showWithdrawDialog = true">提现</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Recharge Dialog -->
      <el-dialog v-model="showRechargeDialog" title="金额充值" width="400px">
        <el-form :model="rechargeForm" label-width="80px">
          <el-form-item label="充值金额">
            <el-input-number v-model="rechargeForm.amount" :min="0.01" :precision="2" :step="10" style="width: 100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showRechargeDialog = false">取消</el-button>
            <el-button type="primary" :loading="recharging" @click="handleRecharge">确认充值</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- Withdraw Dialog -->
      <el-dialog v-model="showWithdrawDialog" title="余额提现" width="400px">
        <el-form :model="withdrawForm" label-width="80px">
          <el-form-item label="提现金额">
            <el-input-number v-model="withdrawForm.amount" :min="0.01" :max="wallet?.balance || 0" :precision="2" :step="10" style="width: 100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showWithdrawDialog = false">取消</el-button>
            <el-button type="primary" :loading="withdrawing" @click="handleWithdraw">确认提现</el-button>
          </span>
        </template>
      </el-dialog>

      <h3 style="margin-top: 32px; margin-bottom: 16px;">交易记录</h3>
      
      <el-table :data="displayTransactions" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="amount" label="金额" min-width="120">
          <template #default="{ row }">
            <span :style="{ color: row.amount > 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" min-width="120">
          <template #default="{ row }">
            {{ getTransactionTypeText(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && displayTransactions.length === 0" description="暂无交易记录" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWallet, getTransactions, selfRecharge, withdraw } from '../api/wallet'
import store from '../store'
import Layout from '../components/Layout.vue'
import { formatDateTime } from '../utils/format'
import { getTransactionTypeText } from '../utils/status'

const loading = ref(false)
const recharging = ref(false)
const withdrawing = ref(false)
const showRechargeDialog = ref(false)
const showWithdrawDialog = ref(false)
const rechargeForm = ref({ amount: 100 })
const withdrawForm = ref({ amount: 100 })
const wallet = ref(null)
const transactions = ref([])
const user = computed(() => store.state.user)

const displayTransactions = computed(() => {
  if (user.value?.role === 'admin') {
    return transactions.value
  }
  return wallet.value?.transactions || []
})

const handleRecharge = async () => {
  if (rechargeForm.value.amount <= 0) {
     ElMessage.warning('请输入有效的金额')
     return
  }
  
  recharging.value = true
  try {
    await selfRecharge(rechargeForm.value.amount)
    ElMessage.success('充值成功')
    showRechargeDialog.value = false
    loadWallet() // Refresh balance and transaction list
  } catch (error) {
    ElMessage.error('充值失败，请稍后重试')
  } finally {
    recharging.value = false
  }
}

const handleWithdraw = async () => {
  if (withdrawForm.value.amount <= 0) {
     ElMessage.warning('请输入有效的提现金额')
     return
  }
  if (withdrawForm.value.amount > wallet.value.balance) {
     ElMessage.warning('余额不足')
     return
  }
  
  withdrawing.value = true
  try {
    await withdraw(withdrawForm.value.amount)
    ElMessage.success('提现成功')
    showWithdrawDialog.value = false
    loadWallet() // Refresh
  } catch (error) {
    ElMessage.error('提现失败，请稍后重试')
  } finally {
    withdrawing.value = false
  }
}

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
