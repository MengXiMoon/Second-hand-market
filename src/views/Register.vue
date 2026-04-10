<template>
  <Layout>
    <div class="register">
      <el-card class="register-card">
        <template #header>
          <h2>注册</h2>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" type="email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请确认密码" show-password />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
              <el-option label="普通用户" value="user" />
              <el-option label="商家" value="merchant" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
              注册
            </el-button>
          </el-form-item>
          <el-form-item>
            <span>已有账号？</span>
            <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../api/auth'
import Layout from '../components/Layout.vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'user'
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await register({
          username: form.username,
          email: form.email,
          password: form.password,
          role: form.role
        })
        ElMessage.success('注册成功，请等待管理员审核')
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  padding-top: 40px;
}

.register-card {
  width: 400px;
}

.register-card h2 {
  margin: 0;
  text-align: center;
}
</style>
