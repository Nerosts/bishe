<template>
  <div class="page" v-if="event">
    <div class="top-bar">
      <h1>活动详情</h1>
      <div class="top-buttons">
        <button class="gray-btn" @click="goEvents">返回活动列表</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="message-box" v-if="message">
      {{ message }}
    </div>

    <div class="detail-card">
      <h2>{{ event.title }}</h2>
      <p><strong>活动ID：</strong>{{ event.id }}</p>
      <p><strong>类别：</strong>{{ event.category }}</p>
      <p><strong>地点：</strong>{{ event.location }}</p>
      <p><strong>开始时间：</strong>{{ event.start_time }}</p>
      <p><strong>人数上限：</strong>{{ event.max_participants }}</p>
      <p><strong>已通过人数：</strong>{{ event.approved_count }}</p>
      <p><strong>状态：</strong>{{ event.status }}</p>
      <p><strong>活动描述：</strong>{{ event.description }}</p>

      <button
        v-if="role === 'student'"
        class="blue-btn register-btn"
        @click="handleRegister"
      >
        立即报名
      </button>
    </div>
  </div>

  <div class="page" v-else>
    <div class="detail-card">
      <p>活动详情加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const event = ref(null)
const message = ref('')
const userId = ref('')
const role = ref('')

const loadEventDetail = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:5000/events/${route.params.id}`)
    event.value = res.data
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '活动详情加载失败'
    }
  }
}

const handleRegister = async () => {
  try {
    const res = await axios.post('http://127.0.0.1:5000/registrations', {
      user_id: Number(userId.value),
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

const goEvents = () => {
  router.push('/events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  userId.value = localStorage.getItem('user_id') || ''
  role.value = localStorage.getItem('role') || ''

  if (!userId.value) {
    router.push('/login')
    return
  }

  loadEventDetail()
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

.blue-btn {
  background: #409eff;
}

.blue-btn:hover {
  background: #66b1ff;
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

.detail-card {
  max-width: 700px;
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.detail-card h2 {
  margin-top: 0;
  color: #333;
}

.detail-card p {
  margin: 12px 0;
  color: #555;
  font-size: 15px;
}

.register-btn {
  margin-top: 20px;
}
</style>