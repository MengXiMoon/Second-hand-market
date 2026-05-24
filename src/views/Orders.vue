<template>
  <Layout>
    <div class="orders">
    <div class="orders-header">
      <h2>我的订单</h2>
      <el-button
        v-if="unpaidOrders.length > 0"
        type="success"
        @click="handlePayAll"
        :loading="payingAll"
      >
        一键付款 ({{ unpaidOrders.length }} 笔，合计 ¥{{ formatMoney(unpaidTotal) }})
      </el-button>
    </div>

      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="订单ID" width="80" />
        <el-table-column prop="product_id" label="商品ID" width="80" />
        <el-table-column prop="total_price" label="金额" width="100">
          <template #default="{ row }">¥{{ formatMoney(row.total_price) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.status)">{{ getOrderStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="240">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-if="row.status === 'ordered'"
                type="success" size="small"
                @click="handlePay(row)">付款</el-button>
              <el-button
                v-if="row.status === 'paid'"
                type="warning" size="small"
                @click="handleCancel(row)">申请退款</el-button>
              <el-button
                v-if="row.status === 'completed'"
                type="warning" size="small"
                @click="handleReview(row)">评价</el-button>
              <el-button
                v-if="row.status === 'shipped'"
                type="primary" size="small"
                @click="handleComplete(row)">确认收货</el-button>
              <el-button
                v-if="row.status === 'ordered'"
                type="danger" size="small"
                @click="handleCancel(row)">取消订单</el-button>
              <span v-if="row.tracking_number" class="tracking">物流: {{ row.tracking_number }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />

      <!-- 评价对话框 -->
      <el-dialog v-model="showReviewDialog" title="评价订单" width="420px">
        <el-form label-width="60px">
          <el-form-item label="评分">
            <el-rate v-model="reviewForm.rating" />
          </el-form-item>
          <el-form-item label="评论">
            <el-input v-model="reviewForm.comment" type="textarea" :rows="2" placeholder="说点什么吧..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showReviewDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitReview">提交评价</el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyOrders, payOrder, completeOrder, cancelOrder } from '../api/orders'
import { createReview } from '../api/reviews'
import { getWallet } from '../api/wallet'
import Layout from '../components/Layout.vue'
import { formatDateTime, formatMoney } from '../utils/format'
import { getOrderStatusText, getOrderStatusType } from '../utils/status'

const loading = ref(false)
const orders = ref([])

const loadOrders = async () => {
  loading.value = true
  try {
    const { data } = await getMyOrders()
    orders.value = data
  } catch (error) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const unpaidOrders = computed(() => orders.value.filter(o => o.status === 'ordered'))
const unpaidTotal = computed(() => unpaidOrders.value.reduce((sum, o) => sum + o.total_price, 0))
const payingAll = ref(false)

const handlePayAll = async () => {
  const list = unpaidOrders.value
  if (list.length === 0) return

  // 先查余额
  let balance = 0
  try {
    const { data } = await getWallet()
    balance = data.balance
  } catch (e) {
    ElMessage.error('无法获取钱包余额')
    return
  }

  const total = unpaidTotal.value
  if (balance < total) {
    ElMessage.warning(
      `余额不足！需要 ¥${formatMoney(total)}，当前余额 ¥${formatMoney(balance)}，还差 ¥${formatMoney(total - balance)}`
    )
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认支付 ${list.length} 笔订单，合计 ¥${formatMoney(total)}？当前余额 ¥${formatMoney(balance)}`,
      '一键付款'
    )
    payingAll.value = true
    let paid = 0
    for (const order of list) {
      try {
        await payOrder(order.id)
        paid++
      } catch (e) {
        const detail = e.response?.data?.detail || '付款失败'
        ElMessage.error(`订单 #${order.id} 付款失败：${detail}`)
        break // 余额不足则剩余也付不了
      }
    }
    if (paid > 0) {
      ElMessage.success(`已付款 ${paid} / ${list.length} 笔`)
    }
    loadOrders()
  } catch (error) {
    /* 用户取消 */
  } finally {
    payingAll.value = false
  }
}

const handlePay = async (order) => {
  try {
    await ElMessageBox.confirm(`确认支付 ¥${formatMoney(order.total_price)}？`, '付款确认')
    await payOrder(order.id)
    ElMessage.success('付款成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error.response?.data?.detail || '付款失败')
    }
  }
}

const handleComplete = async (order) => {
  try {
    await ElMessageBox.confirm('确认已收到商品？确认后资金将结算给商家。', '确认收货')
    await completeOrder(order.id)
    ElMessage.success('已确认收货')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const showReviewDialog = ref(false)
const reviewForm = ref({ order_id: 0, rating: 5, comment: '' })

const handleReview = (order) => {
  reviewForm.value = { order_id: order.id, rating: 5, comment: '' }
  showReviewDialog.value = true
}

const handleSubmitReview = async () => {
  try {
    await createReview(reviewForm.value)
    ElMessage.success('评价成功')
    showReviewDialog.value = false
    loadOrders()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '评价失败')
  }
}

const handleCancel = async (order) => {
  const isRefund = order.status === 'paid'
  const msg = isRefund ? '确认申请退款？已付金额将退回钱包。' : '确认取消此订单？'
  try {
    await ElMessageBox.confirm(msg, isRefund ? '申请退款' : '取消订单')
    await cancelOrder(order.id)
    ElMessage.success(isRefund ? '已退款' : '已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  loadOrders()
  window.addEventListener('refresh-data', loadOrders)
})
</script>

<style scoped>
.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.orders-header h2 {
  margin: 0;
}
.action-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
}
.tracking {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}
</style>
