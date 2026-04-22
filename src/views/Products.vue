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
            <template #default="{ row }">¥{{ row.price }}</template>
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
        <el-row :gutter="20" v-loading="loading">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="product in products" :key="product.id">
            <el-card class="product-card" :body-style="{ padding: '0px' }">
              <div class="product-image">
                <el-icon :size="60"><Goods /></el-icon>
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <p class="description">{{ product.description }}</p>
                <div class="product-footer">
                  <span class="price">¥{{ product.price }}</span>
                  <span class="stock">库存: {{ product.stock }}</span>
                </div>
                <div class="product-actions" style="display: flex; gap: 8px; margin-top: 12px">
                  <el-button 
                    type="primary" 
                    style="flex: 1"
                    @click="handleBuy(product)"
                    :disabled="!user || product.stock < 1"
                  >
                    {{ !user ? '请先登录' : product.stock < 1 ? '已售罄' : '立即购买' }}
                  </el-button>
                  <el-button 
                    v-if="user && user.id !== product.merchant_id"
                    type="success"
                    plain
                    style="flex: 1"
                    @click="handleContact(product)"
                  >
                    联系卖家
                  </el-button>
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
import { createOrder } from '../api/orders'
import store from '../store'
import Layout from '../components/Layout.vue'
import { getProductStatusText, getProductStatusType } from '../utils/status'

const router = useRouter()

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

const handleContact = (product) => {
  router.push({
    path: '/chat',
    query: { target_id: product.merchant_id }
  })
}

const handleBuy = async (product) => {
  try {
    await ElMessageBox.confirm(
      `确定要购买「${product.name}」吗？价格：¥${product.price}`,
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
.products h2 {
  margin-bottom: 24px;
}

.product-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-4px);
}

.product-image {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
}

.product-info {
  padding: 16px;
}

.product-info h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.description {
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: 600;
}

.stock {
  color: #909399;
  font-size: 12px;
}
</style>
