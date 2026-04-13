<template>
  <Layout>
    <div class="my-products">
      <div class="header">
        <h2>我的商品</h2>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          发布商品
        </el-button>
      </div>

      <el-table :data="products" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="price" label="价格" min-width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getProductStatusType(row.status)">{{ getProductStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'approved'"
              type="danger" 
              size="small" 
              @click="handleUpdateStatus(row, 'sold_out')"
            >
              标记售罄
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />

      <el-dialog v-model="showAddDialog" title="发布商品" width="500px">
        <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="80px">
          <el-form-item label="商品名称" prop="name">
            <el-input v-model="productForm.name" placeholder="请输入商品名称" />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input 
              v-model="productForm.description" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入商品描述" 
            />
          </el-form-item>
          <el-form-item label="价格" prop="price">
            <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%" />
          </el-form-item>
          <el-form-item label="库存" prop="stock">
            <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddProduct" :loading="adding">发布</el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyProducts, createProduct, updateProductStatus } from '../api/products'
import Layout from '../components/Layout.vue'
import { getProductStatusText, getProductStatusType } from '../utils/status'

const loading = ref(false)
const adding = ref(false)
const products = ref([])
const showAddDialog = ref(false)
const productFormRef = ref(null)

const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 1
})

const productRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

const loadProducts = async () => {
  loading.value = true
  try {
    const { data } = await getMyProducts()
    products.value = data
  } catch (error) {
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const handleAddProduct = async () => {
  if (!productFormRef.value) return
  
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      adding.value = true
      try {
        await createProduct(productForm)
        ElMessage.success('商品发布成功，等待审核')
        showAddDialog.value = false
        Object.assign(productForm, { name: '', description: '', price: 0, stock: 1 })
        loadProducts()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '发布失败')
      } finally {
        adding.value = false
      }
    }
  })
}

const handleUpdateStatus = async (product, status) => {
  try {
    await updateProductStatus(product.id, status)
    ElMessage.success('状态更新成功')
    loadProducts()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h2 {
  margin: 0;
}
</style>
