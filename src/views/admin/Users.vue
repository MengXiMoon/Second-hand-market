<template>
  <Layout>
    <div class="admin-users">
      <h2>用户审核</h2>
      
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
            <el-tag type="warning">待审核</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="240" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="success" 
              size="small" 
              @click="handleVerify(row)"
            >
              审核通过
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleReject(row)"
              style="margin-left: 8px"
            >
              审核不通过
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && users.length === 0" description="暂无待审核用户" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingUsers, verifyUser, deleteUser } from '../../api/users'
import Layout from '../../components/Layout.vue'
import { getRoleText, getRoleType } from '../../utils/status'

const loading = ref(false)
const users = ref([])

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await getPendingUsers()
    users.value = data
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

const handleReject = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要审核不通过用户「${user.username}」吗？此操作将删除该用户的所有数据，且无法恢复！`,
      '确认审核不通过',
      { 
        confirmButtonText: '确定删除', 
        cancelButtonText: '取消', 
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await deleteUser(user.id)
    ElMessage.success('用户已删除')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
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
