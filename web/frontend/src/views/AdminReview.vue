<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>报名审核管理</h1>
        <p class="sub">管理员可对报名记录进行通过或拒绝操作</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="message-box" v-if="message">
      {{ message }}
    </div>

    <div v-if="registrations.length === 0" class="empty-box">
      暂无报名记录
    </div>

    <div class="grid" v-else>
      <div class="card" v-for="item in registrations" :key="item.id">
        <h3>报名记录 {{ item.id }}</h3>
        <p><strong>用户ID：</strong>{{ item.user_id }}</p>
        <p><strong>活动ID：</strong>{{ item.event_id }}</p>
        <p>
          <strong>当前状态：</strong>
          <span :class="statusClass(item.status)">{{ item.status }}</span>
        </p>
        <p><strong>报名时间：</strong>{{ item.signup_time }}</p>

        <div class="btn-row">
          <button class="green-btn" @click="approveRegistration(item.id)">
            审核通过
          </button>
          <button class="red-btn" @click="rejectRegistration(item.id)">
            审核拒绝
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const registrations = ref([])
const message = ref('')
const role = ref('')

const loadRegistrations = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/registrations')
    registrations.value = res.data
  } catch (error) {
    message.value = '报名记录加载失败'
  }
}

const approveRegistration = async (id) => {
  try {
    const res = await axios.put(`http://127.0.0.1:5000/registrations/${id}/approve`)
    message.value = res.data.message
    await loadRegistrations()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '审核通过失败'
    }
  }
}

const rejectRegistration = async (id) => {
  try {
    const res = await axios.put(`http://127.0.0.1:5000/registrations/${id}/reject`)
    message.value = res.data.message
    await loadRegistrations()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '审核拒绝失败'
    }
  }
}

const statusClass = (status) => {
  if (status === '已通过') return 'status-pass'
  if (status === '已拒绝') return 'status-reject'
  return 'status-pending'
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

onMounted(() => {
  role.value = localStorage.getItem('role') || ''

  if (role.value !== 'admin') {
    router.push('/login')
    return
  }

  loadRegistrations()
})
</script>

<style scoped>
.page {
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.top-bar h1 {
  margin: 0;
  color: #333;
}

.sub {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  cursor: pointer;
  color: white;
}

.green-btn {
  background: #67c23a;
}

.green-btn:hover {
  background: #85ce61;
}

.red-btn {
  background: #f56c6c;
}

.red-btn:hover {
  background: #f78989;
}

.gray-btn {
  background: #909399;
}

.gray-btn:hover {
  background: #a6a9ad;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.empty-box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  color: #666;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.card h3 {
  margin-top: 0;
  color: #333;
}

.card p {
  margin: 10px 0;
  color: #555;
  font-size: 14px;
}

.btn-row {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.btn-row button {
  flex: 1;
}

.status-pass {
  color: #67c23a;
  font-weight: bold;
}

.status-reject {
  color: #f56c6c;
  font-weight: bold;
}

.status-pending {
  color: #e6a23c;
  font-weight: bold;
}
</style>