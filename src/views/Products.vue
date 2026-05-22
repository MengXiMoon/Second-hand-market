<template>
  <Layout>
    <div class="products">
      <h2>{{ pageTitle }}</h2>
      
      <template v-if="isAdminOrMerchant">
        <el-table :data="products" v-loading="loading" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="商品名称" min-width="200" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="price" label="价格" min-width="100">
            <template #default="{ row }">¥{{ formatMoney(row.price) }}</template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="80" />
          <el-table-column prop="merchant_id" label="商家ID" min-width="100" />
          <el-table-column prop="status" label="状态" min-width="120">
            <template #default="{ row }">
              <el-tag :type="getProductStatusType(row.status)">{{ getProductStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </template>
      
      <template v-else>
        <el-row :gutter="24" v-loading="loading">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="product in products" :key="product.id">
            <el-card class="product-card" :body-style="{ padding: '0px' }">
              <div class="product-image">
                <img v-if="product.image_url" :src="getImageUrl(product.image_url)" class="product-img" />
                <div v-else class="placeholder-img-wrapper">
                  <el-icon :size="50"><Goods /></el-icon>
                </div>
                <!-- Fancy premium overlays -->
                <span class="product-tag-overlay" :class="product.stock > 0 ? 'in-stock' : 'out-of-stock'">
                  {{ product.stock > 0 ? `有货 (${product.stock})` : '已售罄' }}
                </span>
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <p class="description">{{ product.description }}</p>
                <div class="product-merchant">
                  <span class="merchant-icon">👤</span>
                  <span class="merchant-name-label">商家：</span>
                  <span class="merchant-name-value">{{ product.merchant_name || `商家 #${product.merchant_id}` }}</span>
                </div>
                <div class="product-footer">
                  <span class="price">¥{{ formatMoney(product.price) }}</span>
                  <span class="stock">库存: {{ product.stock }}</span>
                </div>
                <div class="product-actions">
                  <el-button
                    type="primary"
                    size="default"
                    class="buy-button"
                    @click="handleBuy(product)"
                    :disabled="!user || product.stock < 1"
                  >
                    {{ !user ? '请先登录' : product.stock < 1 ? '已售罄' : '立即购买' }}
                  </el-button>
                  <el-tooltip v-if="user && user.id !== product.merchant_id" content="加入购物车" placement="top">
                    <el-button
                      type="warning"
                      size="default"
                      circle
                      plain
                      @click="handleAddCart(product)"
                    >
                      <el-icon><ShoppingCart /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip v-if="user && user.id !== product.merchant_id" content="联系卖家" placement="top">
                    <el-button
                      type="success"
                      size="default"
                      circle
                      plain
                      @click="handleContact(product)"
                    >
                      <el-icon><ChatDotRound /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </template>

      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProducts } from '../api/products'
import { createOrder, addToCart } from '../api/orders'
import store from '../store'
import Layout from '../components/Layout.vue'
import { getProductStatusText, getProductStatusType } from '../utils/status'
import { formatMoney } from '../utils/format'

const router = useRouter()

const staticBaseUrl = import.meta.env.VITE_STATIC_BASE_URL || ''

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${staticBaseUrl}${url}`
}

const loading = ref(false)
const products = ref([])
const user = computed(() => store.getCurrentSession().user)

const isAdmin = computed(() => user.value?.role === 'admin')
const isMerchant = computed(() => user.value?.role === 'merchant')
const isAdminOrMerchant = computed(() => isAdmin.value || isMerchant.value)

const pageTitle = computed(() => {
  if (isAdmin.value) return '全部商品列表'
  if (isMerchant.value) return '商品列表'
  return '商品列表'
})

const loadProducts = async () => {
  loading.value = true
  try {
    const { data } = await getProducts()
    products.value = data
  } catch (error) {
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const handleAddCart = async (product) => {
  try {
    await addToCart(product.id)
    ElMessage.success(`「${product.name}」已加入购物车`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加入购物车失败')
  }
}

const handleContact = (product) => {
  const chatPath = isMerchant.value ? '/merchant/chat' : (isAdmin.value ? '/admin/chat' : '/customer/chat')
  router.push({
    path: chatPath,
    query: { target_id: product.merchant_id }
  })
}

const handleBuy = async (product) => {
  try {
    await ElMessageBox.confirm(
      `确定要购买「${product.name}」吗？价格：¥${formatMoney(product.price)}`,
      '确认购买',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await createOrder(product.id)
    ElMessage.success('购买成功')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '购买失败')
    }
  }
}

onMounted(() => {
  loadProducts()
  window.addEventListener('refresh-data', loadProducts)
})

onUnmounted(() => {
  window.removeEventListener('refresh-data', loadProducts)
})
</script>

<style scoped>
.products {
  max-width: 1300px;
  margin: 0 auto;
  padding: 10px 0;
}

.products h2 {
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #0f172a 0%, #5e5bf5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 30px;
  font-size: 28px;
}

.product-card {
  margin-bottom: 24px;
  border-radius: 18px !important;
  overflow: hidden;
  box-shadow: 0 4px 20px -2px rgba(94, 91, 245, 0.04), 0 2px 8px -1px rgba(0, 0, 0, 0.02) !important;
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 35px -5px rgba(94, 91, 245, 0.15), 0 8px 15px -4px rgba(0, 0, 0, 0.03) !important;
  border-color: rgba(94, 91, 245, 0.2) !important;
}

.product-image {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, #ffffff 0%, #f1f5f9 100%);
  color: #94a3b8;
  overflow: hidden;
  position: relative;
}

.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.product-card:hover .product-img {
  transform: scale(1.06);
}

.placeholder-img-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.product-tag-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 700;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  z-index: 2;
  letter-spacing: 0.3px;
}

.in-stock {
  background: rgba(16, 185, 129, 0.85) !important;
  color: white !important;
}

.out-of-stock {
  background: rgba(244, 63, 94, 0.85) !important;
  color: white !important;
}

.product-merchant {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  background: rgba(94, 91, 245, 0.04);
  padding: 4px 10px;
  border-radius: 8px;
  width: fit-content;
}

.merchant-icon {
  font-size: 12px;
}

.merchant-name-label {
  color: #64748b;
}

.merchant-name-value {
  color: #5e5bf5;
  font-weight: 700;
}

.product-info {
  padding: 20px;
}

.product-info h3 {
  margin: 0 0 6px;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.description {
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 16px;
  height: 38px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(94, 91, 245, 0.05);
  padding-top: 14px;
}

.price {
  color: #f43f5e;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.stock {
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  background: rgba(100, 116, 139, 0.08);
  padding: 2px 8px;
  border-radius: 6px;
}

.product-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  align-items: center;
}

.buy-button {
  flex: 1;
  height: 38px !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px !important;
  font-weight: 600;
}

.product-actions .el-button--primary {
  box-shadow: 0 4px 12px rgba(94, 91, 245, 0.25);
}

.product-actions .el-button--primary:hover {
  box-shadow: 0 6px 16px rgba(94, 91, 245, 0.35);
}

.product-actions :deep(.el-button.is-circle) {
  width: 38px !important;
  height: 38px !important;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  flex-shrink: 0;
  border-radius: 50% !important;
}

.product-actions :deep(.el-button.is-circle):hover {
  transform: scale(1.1);
}
</style>
