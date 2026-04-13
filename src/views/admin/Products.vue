<template>
  <Layout>
    <div class="admin-products">
      <h2>商品审核</h2>
      
      <el-table :data="products" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="price" label="价格" min-width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="merchant_id" label="商家ID" min-width="100" />
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag type="warning">待审核</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="success" 
              size="small" 
              @click="handleAudit(row, true)"
            >
              通过
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleAudit(row, false)"
              style="margin-left: 8px"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && products.length === 0" description="暂无待审核商品" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingProducts, auditProduct } from '../../api/products'
import Layout from '../../components/Layout.vue'

const loading = ref(false)
const products = ref([])

const loadProducts = async () => {
  loading.value = true
  try {
    const { data } = await getPendingProducts()
    products.value = data
  } catch (error) {
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const handleAudit = async (product, approve) => {
  try {
    await ElMessageBox.confirm(
      `确定要${approve ? '通过' : '拒绝'}商品「${product.name}」吗？`,
      '确认审核',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await auditProduct(product.id, approve)
    ElMessage.success('审核成功')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败')
    }
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.admin-products h2 {
  margin-bottom: 24px;
}
</style>
