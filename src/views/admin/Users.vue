<template>
  <Layout>
    <div class="admin-users">
      <h2>用户审核</h2>
      
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'warning'">
              {{ row.is_verified ? '已审核' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" v-if="showPending">
          <template #default="{ row }">
            <el-button 
              v-if="!row.is_verified" 
              type="success" 
              size="small" 
              @click="handleVerify(row)"
            >
              审核通过
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && users.length === 0" description="暂无用户" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingUsers, getUsers, verifyUser } from '../../api/users'
import Layout from '../../components/Layout.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(false)
const users = ref([])
const showPending = ref(true)

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await getPendingUsers()
    users.value = data
    if (data.length === 0) {
      const { data: allUsers } = await getUsers()
      users.value = allUsers
      showPending.value = false
    }
  } catch (error) {
    ElMessage.error('加载用户失败')
  } finally {
    loading.value = false
  }
}

const handleVerify = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要审核通过用户「${user.username}」吗？`,
      '确认审核',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await verifyUser(user.id)
    ElMessage.success('审核成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败')
    }
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
