<template>
  <Layout>
    <div class="reviews-page">
      <h2>我的评价</h2>
      <div v-loading="loading">
        <div v-for="r in reviews" :key="r.id" class="review-card">
          <div class="review-header">
            <span class="reviewer">{{ r.reviewer_name }}</span>
            <el-rate v-model="r.rating" disabled size="small" />
            <span class="review-date">{{ formatTime(r.created_at) }}</span>
          </div>
          <div class="review-comment">{{ r.comment }}</div>
          <div v-if="r.reply" class="review-reply">
            <span class="reply-label">我的回复：</span>{{ r.reply }}
          </div>
          <div v-else style="margin-top:8px">
            <el-input v-model="replyInputs[r.id]" size="small" placeholder="回复买家评价..." style="width:300px" />
            <el-button size="small" type="primary" @click="handleReply(r)" style="margin-left:8px">回复</el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && reviews.length === 0" description="暂无评价" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyReviews, replyReview } from '../api/reviews'
import Layout from '../components/Layout.vue'

const loading = ref(false)
const reviews = ref([])
const replyInputs = reactive({})

const loadReviews = async () => {
  loading.value = true
  try {
    const { data } = await getMyReviews()
    reviews.value = data
  } catch (error) {
    ElMessage.error('加载评价失败')
  } finally {
    loading.value = false
  }
}

const handleReply = async (review) => {
  const txt = replyInputs[review.id]
  if (!txt || !txt.trim()) return
  try {
    await replyReview(review.id, txt)
    review.reply = txt
    replyInputs[review.id] = ''
    ElMessage.success('已回复')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '回复失败')
  }
}

const formatTime = (dateStr) => new Date(dateStr).toLocaleString('zh-CN')

onMounted(loadReviews)
</script>

<style scoped>
.reviews-page { max-width: 800px; margin: 0 auto; }
.reviews-page h2 { margin-bottom: 20px; }
.review-card { padding: 16px; border-radius: 8px; border: 1px solid #ebeef5; margin-bottom: 12px; }
.review-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.reviewer { font-weight: 600; }
.review-date { color: #c0c4cc; font-size: 12px; margin-left: auto; }
.review-comment { color: #606266; margin-bottom: 8px; }
.review-reply { background: #f0f9eb; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #606266; }
.reply-label { font-weight: 600; color: #67c23a; }
</style>
