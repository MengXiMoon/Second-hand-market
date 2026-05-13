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
          <template #default="{ row }">¥{{ formatMoney(row.price) }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="{ row }">
            <el-popover
              v-if="row.status === 'rejected' && row.audit_remark"
              placement="top"
              title="驳回理由"
              :width="200"
              trigger="hover"
              :content="row.audit_remark"
            >
              <template #reference>
                <el-tag :type="getProductStatusType(row.status)" style="cursor: pointer">
                  {{ getProductStatusText(row.status) }}
                  <el-icon><InfoFilled /></el-icon>
                </el-tag>
              </template>
            </el-popover>
            <el-tag v-else :type="getProductStatusType(row.status)">{{ getProductStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
            >
              编辑/重审
            </el-button>
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

      <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑商品' : '发布商品'" width="500px">
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
          <el-form-item label="商品图片">
            <el-upload
              class="product-image-upload"
              :action="uploadAction"
              :headers="uploadHeaders"
              :show-file-list="false"
              :on-success="handleImageSuccess"
              :on-error="handleImageError"
              :before-upload="beforeImageUpload"
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              <img v-if="productForm.image_url" :src="getImageUrl(productForm.image_url)" class="upload-preview" />
              <el-icon v-else class="upload-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="价格 (元)" prop="price">
            <el-input-number v-model="productForm.price" :min="0.01" :precision="2" style="width: 100%" />
          </el-form-item>
          <el-form-item label="库存" prop="stock">
            <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
          </el-form-item>
          <div v-if="isEdit && currentProduct?.status === 'rejected'" class="audit-hint">
            <el-alert
              title="提示：保存后将重新进入待审核状态"
              type="warning"
              show-icon
              :closable="false"
            />
          </div>
        </el-form>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="saving">
            {{ isEdit ? '保存并重审' : '发布' }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Plus } from '@element-plus/icons-vue'
import { getMyProducts, createProduct, updateProduct, updateProductStatus, uploadProductImage } from '../api/products'
import Layout from '../components/Layout.vue'
import { getProductStatusText, getProductStatusType } from '../utils/status'
import { formatMoney, toCents } from '../utils/format'
import store from '../store'

const staticBaseUrl = import.meta.env.VITE_STATIC_BASE_URL || ''

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${staticBaseUrl}${url}`
}

const loading = ref(false)
const saving = ref(false)
const products = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const currentProduct = ref(null)
const productFormRef = ref(null)

const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 1,
  image_url: ''
})

const uploadAction = computed(() => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/v1'
  return `${baseURL}/products/upload-image`
})

const uploadHeaders = computed(() => {
  const token = store.getAuthToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
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

const handleEdit = (product) => {
  isEdit.value = true
  currentProduct.value = product
  Object.assign(productForm, {
    name: product.name,
    description: product.description,
    price: product.price / 100,  // Convert cents → yuan for display
    stock: product.stock,
    image_url: product.image_url || ''
  })
  showAddDialog.value = true
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

const handleImageSuccess = (response) => {
  productForm.image_url = response.image_url
  ElMessage.success('图片上传成功')
}

const handleImageError = () => {
  ElMessage.error('图片上传失败')
}

const handleSubmit = async () => {
  if (!productFormRef.value) return
  
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const payload = {
          ...productForm,
          price: toCents(productForm.price)  // Convert yuan → cents for API
        }
        if (isEdit.value) {
          await updateProduct(currentProduct.value.id, payload)
          ElMessage.success('更新成功，已重新提交审核')
        } else {
          await createProduct(payload)
          ElMessage.success('商品发布成功，等待审核')
        }
        showAddDialog.value = false
        resetForm()
        loadProducts()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const resetForm = () => {
  isEdit.value = false
  currentProduct.value = null
  Object.assign(productForm, { name: '', description: '', price: 0, stock: 1, image_url: '' })
}

watch(showAddDialog, (val) => {
  if (!val) resetForm()
})

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
  window.addEventListener('refresh-data', loadProducts)
})

onUnmounted(() => {
  window.removeEventListener('refresh-data', loadProducts)
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

.product-image-upload :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  width: 148px;
  height: 148px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.product-image-upload :deep(.el-upload:hover) {
  border-color: #409eff;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-preview {
  width: 148px;
  height: 148px;
  object-fit: cover;
  border-radius: 6px;
}
</style>
