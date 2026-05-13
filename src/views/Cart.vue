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
        <el-table-column label="单价" width="100">
          <template #default="{ row }">¥{{ formatMoney(row.product?.price || 0) }}</template>
        </el-table-column>
        <el-table-column label="数量" width="140">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              :max="row.product?.stock || 99"
              size="small"
              @change="(val) => handleQuantityChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="100">
          <template #default="{ row }">¥{{ formatMoney((row.product?.price || 0) * row.quantity) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && cartItems.length === 0" description="购物车是空的">
        <el-button type="primary" @click="$router.push('/customer/products')">去逛逛</el-button>
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
}
.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.cart-header h2 {
  margin: 0;
}
.cart-product {
  display: flex;
  align-items: center;
  gap: 12px;
}
.cart-img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
}
.cart-name {
  font-weight: 600;
  font-size: 14px;
}
.cart-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
