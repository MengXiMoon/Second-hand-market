<template>
  <Layout>
    <div class="products">
      <h2>商品列表</h2>
      
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
              <el-button 
                type="primary" 
                style="width: 100%; margin-top: 12px"
                @click="handleBuy(product)"
                :disabled="!user || product.stock < 1"
              >
                {{ !user ? '请先登录' : product.stock < 1 ? '已售罄' : '立即购买' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProducts } from '../api/products'
import { createOrder } from '../api/orders'
import store from '../store'
import Layout from '../components/Layout.vue'

const loading = ref(false)
const products = ref([])
const user = computed(() => store.state.user)

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
