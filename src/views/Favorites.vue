<template>
  <Layout>
    <div class="favorites">
      <h2>我的收藏</h2>

      <el-row :gutter="24" v-loading="loading">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="fav in favorites" :key="fav.id">
          <el-card class="product-card" :body-style="{ padding: '0px' }">
            <div class="product-image" @click="goProduct(fav.product)">
              <img v-if="fav.product?.image_url" :src="getImageUrl(fav.product.image_url)" class="product-img" />
              <div v-else class="placeholder-img-wrapper">
                <el-icon :size="50"><Goods /></el-icon>
              </div>
            </div>
            <div class="product-info">
              <h3>{{ fav.product?.name }}</h3>
              <p class="description">{{ fav.product?.description }}</p>
              <div class="product-footer">
                <span class="price">¥{{ formatMoney(fav.product?.price || 0) }}</span>
              </div>
              <el-button type="danger" size="small" @click="handleRemove(fav)" style="margin-top:8px;width:100%">取消收藏</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && favorites.length === 0" description="暂无收藏">
        <el-button type="primary" @click="$router.push('/customer/products')">去逛逛</el-button>
      </el-empty>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFavorites, removeFavorite } from '../api/products'
import { formatMoney } from '../utils/format'
import Layout from '../components/Layout.vue'

const router = useRouter()
const loading = ref(false)
const favorites = ref([])
const staticBaseUrl = import.meta.env.VITE_STATIC_BASE_URL || ''

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${staticBaseUrl}${url}`
}

const loadFavorites = async () => {
  loading.value = true
  try {
    const { data } = await getFavorites()
    favorites.value = data
  } catch (error) {
    ElMessage.error('加载收藏失败')
  } finally {
    loading.value = false
  }
}

const handleRemove = async (fav) => {
  try {
    await removeFavorite(fav.id)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const goProduct = (product) => {
  if (product) router.push('/customer/products')
}

onMounted(loadFavorites)
</script>

<style scoped>
.favorites { max-width: 1300px; margin: 0 auto; }
.favorites h2 { margin-bottom: 20px; }
.product-card { margin-bottom: 24px; border-radius: 18px; overflow: hidden; cursor: pointer; transition: transform 0.3s; }
.product-card:hover { transform: translateY(-4px); }
.product-image { height: 160px; display: flex; align-items: center; justify-content: center; background: #f5f7fa; overflow: hidden; }
.product-img { width: 100%; height: 100%; object-fit: cover; }
.placeholder-img-wrapper { color: #909399; }
.product-info { padding: 16px; }
.product-info h3 { margin: 0 0 8px; font-size: 16px; color: #303133; }
.description { color: #909399; font-size: 14px; margin-bottom: 8px; height: 36px; overflow: hidden; }
.product-footer { display: flex; justify-content: space-between; align-items: center; }
.price { color: #f56c6c; font-size: 20px; font-weight: 600; }
</style>
