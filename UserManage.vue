<template>
  <div class="user-manage">
    <div class="header">
      <h2>用户管理</h2>
      <el-button
        v-if="authStore.user?.role === 'ADMIN'"
        type="primary"
        @click="openAddDialog"
      >+ 新增用户</el-button>
    </div>
    <el-card shadow="hover">
      <el-table :data="userList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'ADMIN' ? 'danger' : 'info'" size="small">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.enabled ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >{{ row.enabled ? '禁用' : '启用' }}</el-button>
            <el-button size="small" type="danger" @click="deleteUser(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增用户弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增用户" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="addForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="addForm.role" placeholder="选择角色">
            <el-option label="普通用户" value="USER" />
            <el-option label="管理员" value="ADMIN" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑用户" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" placeholder="选择角色">
            <el-option label="普通用户" value="USER" />
            <el-option label="管理员" value="ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.enabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request.js'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const loading = ref(false)
const userList = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 新增
const showAddDialog = ref(false)
const addForm = ref({
  username: '',
  password: '',
  email: '',
  role: 'USER'
})

// 编辑
const showEditDialog = ref(false)
const editForm = ref({
  id: null,
  username: '',
  email: '',
  role: 'USER',
  enabled: true
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await request.get('/users', {
      params: {
        page: currentPage.value - 1,
        size: pageSize.value
      }
    })
    userList.value = res.content || []
    total.value = res.totalElements || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchUsers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUsers()
}

const openAddDialog = () => {
  addForm.value = { username: '', password: '', email: '', role: 'USER' }
  showAddDialog.value = true
}

const addUser = async () => {
  try {
    await request.post('/users', addForm.value)
    ElMessage.success('用户创建成功')
    showAddDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '创建失败')
  }
}

const openEditDialog = (user) => {
  editForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    role: user.role,
    enabled: user.enabled
  }
  showEditDialog.value = true
}

const updateUser = async () => {
  try {
    await request.put(`/users/${editForm.value.id}`, {
      email: editForm.value.email,
      role: editForm.value.role,
      enabled: editForm.value.enabled
    })
    ElMessage.success('用户更新成功')
    showEditDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '更新失败')
  }
}

const toggleStatus = async (user) => {
  const action = user.enabled ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${user.username} 吗？`, '提示', { type: 'warning' })
    await request.put(`/users/${user.id}`, {
      email: user.email,
      role: user.role,
      enabled: !user.enabled
    })
    ElMessage.success(`${action}成功`)
    fetchUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.message || `${action}失败`)
    }
  }
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该用户吗？', '提示', { type: 'warning' })
    await request.delete('/users/' + id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.message || '删除失败')
    }
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.user-manage .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.user-manage h2 {
  color: #1e293b;
  margin: 0;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
