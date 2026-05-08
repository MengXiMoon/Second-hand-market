<template>
  <Layout>
    <div class="login">
      <el-card class="login-card" v-if="showRoleSelection">
        <template #header>
          <h2>选择登录入口</h2>
        </template>
        <div class="role-selection">
          <el-card class="role-card" shadow="hover" @click="selectRole('user')">
            <el-icon :size="48" color="#409eff"><User /></el-icon>
            <h3>顾客登录</h3>
            <p>浏览商品，购买二手好物</p>
          </el-card>
          <el-card class="role-card" shadow="hover" @click="selectRole('merchant')">
            <el-icon :size="48" color="#e6a23c"><Shop /></el-icon>
            <h3>商家登录</h3>
            <p>发布商品，管理店铺</p>
          </el-card>
          <el-card class="role-card" shadow="hover" @click="selectRole('admin')">
            <el-icon :size="48" color="#f56c6c"><Setting /></el-icon>
            <h3>管理员登录</h3>
            <p>审核商品，管理用户</p>
          </el-card>
        </div>
      </el-card>
      <el-card class="login-card" v-else>
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, getCurrentUser } from '../api/auth'
import store from '../store'
import Layout from '../components/Layout.vue'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const selectedRole = ref('user')

const showRoleSelection = computed(() => {
  const path = route.path
  return path === '/login'
})

const selectRole = (role) => {
  selectedRole.value = role
  if (role === 'merchant') {
    router.replace('/merchant/login')
  } else if (role === 'admin') {
    router.replace('/admin/login')
  } else {
    router.replace('/customer/login')
  }
}

const targetRole = computed(() => {
  const path = route.path
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/merchant')) return 'merchant'
  return 'user'
})
const title = computed(() => {
  if (targetRole.value === 'admin') return '管理员登录'
  if (targetRole.value === 'merchant') return '商家登录'
  return '顾客登录'
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
        
        const { data: user } = await getCurrentUser(tokenData.access_token)
        
        if (targetRole.value === 'admin' && user.role !== 'admin') {
          throw { response: { data: { detail: '此账号没有管理员权限' } } }
        }
        if (targetRole.value === 'merchant' && user.role !== 'merchant' && user.role !== 'admin') {
          throw { response: { data: { detail: '此账号没有商家权限' } } }
        }

        store.setUser(user, tokenData.access_token)
        store.setContextRole(targetRole.value)
        
        ElMessage.success({
          message: '登录成功',
          duration: 500,
          showClose: false
        })
        
        setTimeout(() => {
          if (targetRole.value === 'admin') {
            router.push('/admin/all-users')
          } else if (targetRole.value === 'merchant') {
            router.push('/merchant/my-products')
          } else {
            router.push('/customer')
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

.role-selection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-card {
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  padding: 20px;
}

.role-card:hover {
  transform: translateY(-4px);
}

.role-card h3 {
  margin: 12px 0 8px;
  color: #303133;
}

.role-card p {
  color: #909399;
  font-size: 14px;
}
</style>
