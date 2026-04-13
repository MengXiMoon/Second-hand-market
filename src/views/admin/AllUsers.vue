<template>
  <Layout>
    <div class="admin-users">
      <h2>全部用户</h2>
      
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="150" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'warning'">
              {{ row.is_verified ? '已审核' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && users.length === 0" description="暂无用户" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers } from '../../api/users'
import Layout from '../../components/Layout.vue'
import { getRoleText, getRoleType } from '../../utils/status'

const loading = ref(false)
const users = ref([])

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await getUsers()
    users.value = data
  } catch (error) {
    ElMessage.error('加载用户失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users h2 {
  margin-bottom: 24px;
}
</style>
