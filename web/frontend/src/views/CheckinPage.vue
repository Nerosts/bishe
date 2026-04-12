<template>
  <div class="page">
    <div class="card">
      <h1>学生签到</h1>
      <p class="sub">请使用已通过审核的学生账号完成签到</p>

      <div class="message-box success" v-if="successMessage">
        {{ successMessage }}
      </div>

      <div class="message-box error" v-if="errorMessage">
        {{ errorMessage }}
      </div>

      <div v-if="eventInfo" class="event-box">
        <h2>{{ eventInfo.title }}</h2>
        <p><strong>活动ID：</strong>{{ eventInfo.id }}</p>
        <p><strong>类别：</strong>{{ eventInfo.category }}</p>
        <p><strong>地点：</strong>{{ eventInfo.location }}</p>
        <p><strong>开始时间：</strong>{{ eventInfo.start_time }}</p>
        <p><strong>状态：</strong>{{ eventInfo.status }}</p>
        <p><strong>当前登录用户：</strong>{{ username || '未登录' }}</p>
        <p><strong>当前角色：</strong>{{ role || '未登录' }}</p>
      </div>

      <div class="btn-group">
        <button class="blue-btn" @click="doCheckin">立即签到</button>
        <button class="gray-btn" @click="goLogin">去登录</button>
        <button class="red-btn" @click="goHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const route = useRoute()
const router = useRouter()

const eventInfo = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

const username = ref(localStorage.getItem('username') || '')
const role = ref(localStorage.getItem('role') || '')
const userId = ref(localStorage.getItem('user_id') || '')

const loadEvent = async () => {
  const eventId = route.query.event_id

  if (!eventId) {
    errorMessage.value = '缺少活动ID'
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/events/${eventId}`)
    eventInfo.value = res.data
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage.value = error.response.data.message
    } else {
      errorMessage.value = '获取活动信息失败'
    }
  }
}

const doCheckin = async () => {
  const eventId = route.query.event_id
  successMessage.value = ''
  errorMessage.value = ''

  if (!userId.value) {
    errorMessage.value = '请先登录学生账号再签到'
    return
  }

  if (role.value !== 'student') {
    errorMessage.value = '只有学生账号可以签到'
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/checkin`, {
      user_id: userId.value,
      event_id: eventId
    })
    successMessage.value = res.data.message
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage.value = error.response.data.message
    } else {
      errorMessage.value = '签到失败'
    }
  }
}

const goLogin = () => {
  const currentFullPath = route.fullPath
  router.push(`/login?redirect=${encodeURIComponent(currentFullPath)}`)
}

const goHome = () => {
  router.push('/home')
}

onMounted(() => {
  loadEvent()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px;
  box-sizing: border-box;
}

.card {
  width: 100%;
  max-width: 700px;
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

h1 {
  margin: 0;
  color: #333;
  text-align: center;
}

.sub {
  text-align: center;
  color: #666;
  margin-top: 10px;
  margin-bottom: 20px;
}

.message-box {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.success {
  background: #f0f9eb;
  color: #67c23a;
}

.error {
  background: #fef0f0;
  color: #f56c6c;
}

.event-box {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.event-box h2 {
  margin-top: 0;
  color: #333;
}

.event-box p {
  margin: 10px 0;
  color: #555;
}

.btn-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

button {
  border: none;
  border-radius: 8px;
  padding: 12px 22px;
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
</style>