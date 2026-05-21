<template>
  <div class="login-log">
    <h2>登录记录</h2>
    <el-card shadow="hover">
      <el-table :data="logList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="ipAddress" label="IP地址" />
        <el-table-column prop="loginTime" label="登录时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.loginTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="success" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request.js'

const loading = ref(false)
const logList = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await request.get('/users/logs', {
      params: {
        page: currentPage.value - 1,
        size: pageSize.value
      }
    })
    logList.value = res.content || []
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
  fetchLogs()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchLogs()
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

onMounted(fetchLogs)
</script>

<style scoped>
.login-log h2 {
  color: #1e293b;
  margin: 0 0 20px 0;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
