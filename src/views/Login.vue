<template>
  <Layout>
    <div class="login">
      <el-card class="login-card">
        <template #header>
          <h2>{{ title }}</h2>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
              登录
            </el-button>
          </el-form-item>
          <el-form-item>
            <span>还没有账号？</span>
            <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, getCurrentUser } from '../api/auth'
import store from '../store'
import Layout from '../components/Layout.vue'



const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

// Determine the target role context from the path
const getRoleContext = () => {
  const path = window.location.pathname
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/merchant')) return 'merchant'
  return 'user'
}

const targetRole = getRoleContext()
const title = computed(() => {
  if (targetRole === 'admin') return '管理员登录'
  if (targetRole === 'merchant') return '商家登录'
  return '登录'
})

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { data: tokenData } = await login(form.username, form.password)
        
        // Fetch profile to verify role permission for this specific entryway
        const { data: user } = await getCurrentUser(tokenData.access_token)
        
        // Role Access Control for login page
        if (targetRole === 'admin' && user.role !== 'admin') {
          throw { response: { data: { detail: '此账号没有管理员权限' } } }
        }
        if (targetRole === 'merchant' && user.role !== 'merchant' && user.role !== 'admin') {
          throw { response: { data: { detail: '此账号没有商家权限' } } }
        }

        // Set session for the specific intended role
        store.setUser(user, tokenData.access_token)
        store.setContextRole(targetRole)
        
        ElMessage.success({
          message: '登录成功',
          duration: 500,
          showClose: false
        })
        
        setTimeout(() => {
          if (targetRole === 'admin') {
            router.push('/admin/all-users')
          } else if (targetRole === 'merchant') {
            router.push('/merchant/my-products')
          } else {
            router.push('/')
          }
        }, 500)
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.login-card {
  width: 400px;
}

.login-card h2 {
  margin: 0;
  text-align: center;
}
</style>
