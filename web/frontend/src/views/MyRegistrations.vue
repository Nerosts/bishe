<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>我的报名</h1>
        <p class="sub-title">这里显示当前学生的活动报名记录</p>
      </div>

      <div class="top-buttons">
        <button class="blue-btn" @click="goEvents">活动列表</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="card-list">
      <div class="registration-card" v-for="item in registrationList" :key="item.registration_id">
        <h2>{{ item.event_title }}</h2>
        <p>报名记录ID：{{ item.registration_id }}</p>
        <p>活动ID：{{ item.event_id }}</p>
        <p>类别：{{ item.event_category }}</p>
        <p>地点：{{ item.event_location }}</p>
        <p>开始时间：{{ item.event_start_time }}</p>
        <p>审核状态：{{ item.status }}</p>
        <p>报名时间：{{ item.signup_time }}</p>

        <div class="btn-group">
          <button class="detail-btn" @click="goDetail(item.event_id)">查看活动</button>

          <button
            v-if="item.status !== '已拒绝'"
            class="cancel-btn"
            @click="cancelRegistration(item.registration_id)"
          >
            取消报名
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
import { API_BASE_URL } from '../config'

const router = useRouter()
const registrationList = ref([])
const message = ref('')

const currentUserId = localStorage.getItem('user_id')
const currentRole = localStorage.getItem('role')

const loadRegistrations = async () => {
  if (!currentUserId || currentRole !== 'student') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/users/${currentUserId}/registrations`, {
      params: {
        user_id: currentUserId
      }
    })
    registrationList.value = res.data
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取报名记录失败'
    }
  }
}

const cancelRegistration = async (registrationId) => {
  const ok = window.confirm('确定要取消这条报名吗？')
  if (!ok) return

  try {
    const res = await axios.delete(`${API_BASE_URL}/registrations/${registrationId}`, {
      data: {
        user_id: currentUserId
      }
    })
    message.value = res.data.message
    await loadRegistrations()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '取消报名失败'
    }
  }
}

const goDetail = (eventId) => {
  router.push(`/events/${eventId}`)
}

const goEvents = () => {
  router.push('/events')
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
  loadRegistrations()
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
  font-size: 24px;
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

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.registration-card {
  width: 420px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.registration-card h2 {
  margin-top: 0;
  color: #333;
}

.registration-card p {
  margin: 8px 0;
  color: #555;
}

.btn-group {
  margin-top: 18px;
  display: flex;
  gap: 10px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
  font-size: 14px;
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

.red-btn {
  background: #f56c6c;
}
.red-btn:hover {
  background: #f78989;
}

.detail-btn {
  background: #5b8def;
}
.detail-btn:hover {
  background: #7aa5f3;
}

.cancel-btn {
  background: #f59e0b;
}
.cancel-btn:hover {
  background: #fbbf24;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>