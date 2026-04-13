<template>
  <Layout>
    <div class="sales">
      <h2>销售记录</h2>
      
      <el-table :data="sales" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="订单ID" width="100" />
        <el-table-column prop="product_id" label="商品ID" width="100" />
        <el-table-column prop="buyer_id" label="买家ID" width="100" />
        <el-table-column prop="total_price" label="金额" min-width="120">
          <template #default="{ row }">¥{{ row.total_price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.status)">{{ getOrderStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && sales.length === 0" description="暂无销售记录" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMySales } from '../api/orders'
import Layout from '../components/Layout.vue'
import { formatDateTime } from '../utils/format'
import { getOrderStatusText, getOrderStatusType } from '../utils/status'

const loading = ref(false)
const sales = ref([])

const loadSales = async () => {
  loading.value = true
  try {
    const { data } = await getMySales()
    sales.value = data
  } catch (error) {
    ElMessage.error('加载销售记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSales()
})
</script>

<style scoped>
.sales h2 {
  margin-bottom: 24px;
}
</style>
