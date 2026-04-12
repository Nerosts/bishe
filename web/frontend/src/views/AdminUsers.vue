<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>用户管理</h1>
        <p class="sub-title">管理员可查看系统用户，并按用户名或角色筛选</p>
      </div>

      <div class="top-buttons">
        <button class="purple-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-item">
        <label>用户名筛选</label>
        <input v-model="username" type="text" placeholder="请输入用户名关键字" />
      </div>

      <div class="filter-item">
        <label>角色筛选</label>
        <select v-model="role">
          <option value="">全部角色</option>
          <option value="student">student</option>
          <option value="organizer">organizer</option>
          <option value="admin">admin</option>
        </select>
      </div>

      <div class="filter-buttons">
        <button class="blue-btn" @click="loadUsers">查询</button>
        <button class="gray-btn" @click="resetFilters">重置</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="table-card">
      <table v-if="userList.length > 0">
        <thead>
          <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>角色</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in userList" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.username }}</td>
            <td>{{ item.role }}</td>
            <td>{{ item.created_at }}</td>
            <td>
              <button
                class="delete-btn"
                :disabled="item.role === 'admin'"
                @click="deleteUser(item.id, item.username)"
              >
                {{ item.role === 'admin' ? '不可删除' : '删除用户' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-box">
        暂无符合条件的用户
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()

const username = ref('')
const role = ref('')
const message = ref('')
const userList = ref([])

const loadUsers = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/admin/users`, {
      params: {
        username: username.value,
        role: role.value
      }
    })
    userList.value = res.data || []
    message.value = ''
  } catch (error) {
    message.value = '获取用户列表失败'
  }
}

const resetFilters = async () => {
  username.value = ''
  role.value = ''
  await loadUsers()
}

const deleteUser = async (userId, usernameText) => {
  const currentAdminId = localStorage.getItem('user_id')
  const ok = window.confirm(`确定要删除用户 ${usernameText} 吗？`)
  if (!ok) return

  try {
    const res = await axios.delete(`${API_BASE_URL}/admin/users/${userId}`, {
      params: {
        current_admin_id: currentAdminId
      }
    })
    message.value = res.data.message
    await loadUsers()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '删除用户失败'
    }
  }
}

const goHome = () => {
  router.push('/home')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(async () => {
  const currentRole = localStorage.getItem('role')
  if (currentRole !== 'admin') {
    router.push('/login')
    return
  }

  await loadUsers()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30px;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  color: #333;
}

.sub-title {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
}

.filter-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  color: #333;
  font-weight: bold;
}

.filter-item input,
.filter-item select {
  width: 240px;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.filter-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f5f7fa;
}

th,
td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
  color: #333;
}

.empty-box {
  color: #999;
  padding: 20px 0;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  color: white;
  cursor: pointer;
}

.blue-btn {
  background: #409eff;
}
.blue-btn:hover {
  background: #66b1ff;
}

.gray-btn {
  background: #909399;
}
.gray-btn:hover {
  background: #a6a9ad;
}

.purple-btn {
  background: #8b5cf6;
}
.purple-btn:hover {
  background: #a78bfa;
}

.red-btn {
  background: #f56c6c;
}
.red-btn:hover {
  background: #f78989;
}

.delete-btn {
  background: #f56c6c;
  padding: 8px 14px;
}

.delete-btn:hover {
  background: #f78989;
}

.delete-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}
</style>