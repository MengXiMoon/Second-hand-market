<template>
  <Layout>
    <div class="cart-page">
      <div class="cart-header">
        <h2>购物车</h2>
        <el-button type="primary" @click="handleCheckout" :disabled="selectedIds.length === 0">
          结算选中商品 ({{ selectedIds.length }})
        </el-button>
      </div>

      <el-table
        :data="cartItems"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="商品" min-width="250">
          <template #default="{ row }">
            <div class="cart-product">
              <img v-if="row.product?.image_url" :src="getImageUrl(row.product.image_url)" class="cart-img" />
              <el-icon v-else :size="40"><Goods /></el-icon>
              <div>
                <div class="cart-name">{{ row.product?.name || '商品已下架' }}</div>
                <div class="cart-desc">{{ row.product?.description?.substring(0, 30) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="110">
          <template #default="{ row }"><span class="price-text">¥{{ formatMoney(row.product?.price || 0) }}</span></template>
        </el-table-column>
        <el-table-column label="数量" width="150">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              :max="row.product?.stock || 99"
              size="default"
              style="width: 120px"
              @change="(val) => handleQuantityChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="120">
          <template #default="{ row }"><span class="subtotal-text">¥{{ formatMoney((row.product?.price || 0) * row.quantity) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="default" plain @click="handleRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && cartItems.length === 0" description="您的购物车目前空空如也">
        <el-button type="primary" size="large" class="premium-gradient-btn" @click="$router.push('/customer/products')">去逛逛商场</el-button>
      </el-empty>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Goods } from '@element-plus/icons-vue'
import { getCart, updateCartItem, removeCartItem, cartCheckout } from '../api/orders'
import { formatMoney } from '../utils/format'
import Layout from '../components/Layout.vue'

const router = useRouter()
const staticBaseUrl = import.meta.env.VITE_STATIC_BASE_URL || ''

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${staticBaseUrl}${url}`
}

const loading = ref(false)
const cartItems = ref([])
const selectedIds = ref([])

const loadCart = async () => {
  loading.value = true
  try {
    const { data } = await getCart()
    cartItems.value = data
  } catch (error) {
    ElMessage.error('加载购物车失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleQuantityChange = async (item, quantity) => {
  if (quantity < 1) {
    await removeCartItem(item.id)
    loadCart()
    return
  }
  try {
    await updateCartItem(item.id, quantity)
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleRemove = async (item) => {
  try {
    await removeCartItem(item.id)
    ElMessage.success('已移除')
    loadCart()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleCheckout = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认下单 ${selectedIds.value.length} 件商品？下单后请前往订单页付款。`,
      '确认下单'
    )
    await cartCheckout(selectedIds.value)
    ElMessage.success('下单成功，请前往订单页付款')
    router.push('/customer/orders')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '下单失败')
    }
  }
}

onMounted(loadCart)
</script>

<style scoped>
.cart-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 10px 0;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.cart-header h2 {
  margin: 0;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #0f172a 0%, #5e5bf5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 26px;
}

.cart-product {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 6px 0;
}

.cart-img {
  width: 70px;
  height: 70px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(94, 91, 245, 0.1);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.cart-product:hover .cart-img {
  transform: scale(1.05);
}

.cart-name {
  font-weight: 700;
  font-size: 15px;
  color: #0f172a;
}

.cart-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  line-height: 1.4;
}

.price-text {
  font-weight: 600;
  color: #334155;
  font-size: 15px;
}

.subtotal-text {
  font-weight: 800;
  color: #f43f5e;
  font-size: 16px;
  letter-spacing: -0.3px;
}

:deep(.el-empty) {
  padding: 80px 0 !important;
  background: rgba(255, 255, 255, 0.45) !important;
  border-radius: 24px !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04) !important;
  margin-top: 30px;
}
</style>
