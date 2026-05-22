<template>
  <Layout>
    <div class="wallet">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-card class="balance-card">
            <div class="balance-label">钱包余额</div>
            <div class="balance-amount">¥{{ formatMoney(wallet?.balance) }}</div>
            <div class="btn-container">
              <el-button size="large" class="wallet-btn-recharge" @click="showRechargeDialog = true">充值余额</el-button>
              <el-button size="large" class="wallet-btn-withdraw" @click="showWithdrawDialog = true">提取现金</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Recharge Dialog -->
      <el-dialog v-model="showRechargeDialog" title="金额充值" width="400px">
        <el-form :model="rechargeForm" label-width="80px">
          <el-form-item label="充值金额 (元)">
            <el-input-number v-model="rechargeForm.amount" :min="0.01" :precision="2" :step="100" style="width: 100%" />
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
          <el-form-item label="提现金额 (元)">
            <el-input-number v-model="withdrawForm.amount" :min="0" :max="(wallet?.balance || 0) / 100" :precision="2" :step="50" style="width: 100%" />
            <div style="color: #909399; font-size: 12px; margin-top: 4px">
              可提现余额 ¥{{ formatMoney(wallet?.balance || 0) }}
            </div>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showWithdrawDialog = false">取消</el-button>
            <el-button type="primary" :loading="withdrawing" @click="handleWithdraw">确认提现</el-button>
          </span>
        </template>
      </el-dialog>

      <h3 class="section-title">交易记录</h3>
      
      <el-table :data="displayTransactions" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="amount" label="金额" min-width="120">
          <template #default="{ row }">
            <span :style="{ color: row.amount > 0 ? '#10b981' : '#f43f5e', fontWeight: '700' }">
              {{ row.amount > 0 ? '+' : '' }}{{ formatMoney(Math.abs(row.amount)) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getTransactionTagType(row.type)" effect="light">
              {{ getTransactionTypeText(row.type) }}
            </el-tag>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'

const getTransactionTagType = (type) => {
  const map = {
    'recharge': 'success',
    'purchase': 'danger',
    'sale': 'primary',
    'refund': 'warning',
    'withdraw': 'info',
    'commission': 'primary'
  }
  return map[type] || 'info'
}
import { ElMessage } from 'element-plus'
import { getWallet, getTransactions, selfRecharge, withdraw } from '../api/wallet'
import store from '../store'
import Layout from '../components/Layout.vue'
import { formatDateTime, formatMoney, toCents } from '../utils/format'
import { getTransactionTypeText } from '../utils/status'

const loading = ref(false)
const recharging = ref(false)
const withdrawing = ref(false)
const showRechargeDialog = ref(false)
const showWithdrawDialog = ref(false)
const rechargeForm = ref({ amount: 100 })
const withdrawForm = ref({ amount: 0 })
const wallet = ref(null)
const transactions = ref([])
const user = computed(() => store.getCurrentSession().user)

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
    await selfRecharge(toCents(rechargeForm.value.amount))
    ElMessage.success('充值成功')
    showRechargeDialog.value = false
    loadWallet() // Refresh balance and transaction list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '充值失败')
  } finally {
    recharging.value = false
  }
}

const handleWithdraw = async () => {
  if (withdrawForm.value.amount <= 0) {
     ElMessage.warning('请输入有效的提现金额')
     return
  }
  if (toCents(withdrawForm.value.amount) > (wallet.value?.balance || 0)) {
     ElMessage.warning('余额不足')
     return
  }

  withdrawing.value = true
  try {
    await withdraw(toCents(withdrawForm.value.amount))
    ElMessage.success('提现成功')
    showWithdrawDialog.value = false
    loadWallet()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提现失败')
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

const refreshAllData = () => {
  loadWallet()
  loadTransactions()
}

onMounted(() => {
  refreshAllData()
  window.addEventListener('refresh-data', refreshAllData)
})

onUnmounted(() => {
  window.removeEventListener('refresh-data', refreshAllData)
})
</script>

<style scoped>
.wallet {
  max-width: 1000px;
  margin: 0 auto;
  padding: 10px 0;
}

.balance-card {
  background: linear-gradient(135deg, #5e5bf5 0%, #7c3aed 50%, #6d28d9 100%) !important;
  color: white !important;
  padding: 30px 40px !important;
  border-radius: 24px !important;
  border: none !important;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 45px -10px rgba(94, 91, 245, 0.4) !important;
  margin-bottom: 20px;
}

.balance-card::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  pointer-events: none;
}

.balance-card::after {
  content: '';
  position: absolute;
  bottom: -30px;
  left: 20%;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  pointer-events: none;
}

.balance-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.balance-amount {
  font-size: 52px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -1.5px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-container {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}

.wallet-btn-recharge {
  background: #ffffff !important;
  color: #5e5bf5 !important;
  border: none !important;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
  font-weight: 700;
}

.wallet-btn-recharge:hover {
  transform: translateY(-2px);
  background: #f8fafc !important;
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15) !important;
}

.wallet-btn-withdraw {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(8px);
  font-weight: 700;
}

.wallet-btn-withdraw:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 16px rgba(94, 91, 245, 0.15) !important;
}

.section-title {
  margin-top: 40px;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}
</style>
