<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动详情</h1>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goBack">返回活动列表</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="detail-card" v-if="eventInfo">
      <h2>{{ eventInfo.title }}</h2>
      <p>活动ID：{{ eventInfo.id }}</p>
      <p>类别：{{ eventInfo.category }}</p>
      <p>地点：{{ eventInfo.location }}</p>
      <p>开始时间：{{ eventInfo.start_time }}</p>
      <p>人数上限：{{ eventInfo.max_participants }}</p>
      <p>已通过人数：{{ eventInfo.approved_count }}</p>
      <p>
        状态：
        <span :class="eventInfo.status === '已结束' ? 'status-ended' : 'status-open'">
          {{ eventInfo.status }}
        </span>
      </p>
      <p>活动描述：{{ eventInfo.description }}</p>

      <button
        v-if="role === 'student'"
        class="signup-btn"
        :disabled="eventInfo.status === '已结束'"
        @click="signup"
      >
        {{ eventInfo.status === '已结束' ? '活动已结束' : '立即报名' }}
      </button>
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
const message = ref('')
const role = localStorage.getItem('role') || ''

const loadEventDetail = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/events/${route.params.id}`)
    eventInfo.value = res.data
  } catch (error) {
    message.value = '获取活动详情失败'
  }
}

const signup = async () => {
  const userId = localStorage.getItem('user_id')

  if (!userId) {
    message.value = '请先登录'
    router.push('/login')
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/registrations`, {
      user_id: Number(userId),
      event_id: Number(route.params.id)
    })
    message.value = res.data.message
    await loadEventDetail()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '报名失败'
    }
  }
}

const goBack = () => {
  router.push('/events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  loadEventDetail()
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

.top-buttons {
  display: flex;
  gap: 12px;
}

.detail-card {
  max-width: 720px;
  background: white;
  border-radius: 16px;
  padding: 26px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.detail-card h2 {
  margin-top: 0;
  color: #333;
}

.detail-card p {
  margin: 10px 0;
  color: #555;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  color: white;
  cursor: pointer;
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

.signup-btn {
  margin-top: 18px;
  background: #409eff;
}
.signup-btn:hover {
  background: #66b1ff;
}

.signup-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.status-open {
  color: #16a34a;
  font-weight: bold;
}

.status-ended {
  color: #ef4444;
  font-weight: bold;
}
</style>