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
              :loading="auditLoading === row.id"
              :disabled="auditLoading !== null && auditLoading !== row.id"
            >
              通过
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleAudit(row, false)"
              style="margin-left: 8px"
              :loading="auditLoading === row.id"
              :disabled="auditLoading !== null && auditLoading !== row.id"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingProducts, auditProduct } from '../../api/products'
import Layout from '../../components/Layout.vue'

const loading = ref(false)
const auditLoading = ref(null) // Stores current auditing product ID
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
    let remark = ''
    if (!approve) {
      // Use prompt for rejection reason
      const { value } = await ElMessageBox.prompt(
        `请输入对商品「${product.name}」的驳回理由：`,
        '驳回确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /.+/,
          inputErrorMessage: '理由不能为空'
        }
      )
      remark = value
    } else {
      await ElMessageBox.confirm(
        `确定要通过商品「${product.name}」吗？`,
        '审核通过确认',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'success' }
      )
    }
    auditLoading.value = product.id
    await auditProduct(product.id, approve, remark)
    ElMessage.success('操作成功')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  } finally {
    auditLoading.value = null
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
