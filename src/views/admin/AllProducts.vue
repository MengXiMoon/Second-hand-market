<template>
  <Layout>
    <div class="admin-products">
      <h2>全部商品列表</h2>
      
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

      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProducts } from '../../api/products'
import Layout from '../../components/Layout.vue'
import { getProductStatusText, getProductStatusType } from '../../utils/status'
import { formatMoney } from '../../utils/format'

const loading = ref(false)
const products = ref([])

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

onMounted(() => {
  loadProducts()
  window.addEventListener('refresh-data', loadProducts)
})

onUnmounted(() => {
  window.removeEventListener('refresh-data', loadProducts)
})
</script>

<style scoped>
.admin-products h2 {
  margin-bottom: 24px;
}
</style>
