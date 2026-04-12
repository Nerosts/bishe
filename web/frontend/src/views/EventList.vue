<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动列表</h1>
        <p class="welcome">欢迎你，{{ username }}（{{ roleText }}）</p>
      </div>

      <div class="top-buttons">
        <button class="green-btn" v-if="role === 'student'" @click="goMyRegistrations">
          我的报名
        </button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="message-box" v-if="message">
      {{ message }}
    </div>

    <div class="grid">
      <div class="card" v-for="event in events" :key="event.id">
        <h3>{{ event.title }}</h3>
        <p><strong>类别：</strong>{{ event.category }}</p>
        <p><strong>地点：</strong>{{ event.location }}</p>
        <p><strong>开始时间：</strong>{{ event.start_time }}</p>
        <p><strong>人数上限：</strong>{{ event.max_participants }}</p>
        <p><strong>已通过人数：</strong>{{ event.approved_count }}</p>
        <p><strong>状态：</strong>{{ event.status }}</p>
        <p class="desc">{{ event.description }}</p>

        <div class="btn-row">
          <button class="detail-btn" @click="goDetail(event.id)">查看详情</button>
          <button
            class="blue-btn"
            v-if="role === 'student'"
            @click="handleRegister(event.id)"
          >
            立即报名
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const events = ref([])
const message = ref('')
const username = ref('')
const role = ref('')
const userId = ref('')

const roleText = computed(() => {
  if (role.value === 'student') return '学生'
  if (role.value === 'admin') return '管理员'
  if (role.value === 'organizer') return '组织者'
  return '用户'
})

const loadEvents = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/events')
    events.value = res.data
  } catch (error) {
    message.value = '活动数据加载失败，请检查后端是否启动'
  }
}

const handleRegister = async (eventId) => {
  try {
    const res = await axios.post('http://127.0.0.1:5000/registrations', {
      user_id: Number(userId.value),
      event_id: eventId
    })

    message.value = res.data.message
    await loadEvents()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '报名失败'
    }
  }
}

const goDetail = (id) => {
  router.push(`/events/${id}`)
}

const goHome = () => {
  router.push('/home')
}

const goMyRegistrations = () => {
  router.push('/my-registrations')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  userId.value = localStorage.getItem('user_id') || ''
  username.value = localStorage.getItem('username') || ''
  role.value = localStorage.getItem('role') || ''

  if (!userId.value) {
    router.push('/login')
    return
  }

  loadEvents()
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

.welcome {
  color: #666;
  margin-top: 8px;
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

.detail-btn {
  background: #5b8ff9;
}

.detail-btn:hover {
  background: #7aa7ff;
}

.green-btn {
  background: #67c23a;
}

.green-btn:hover {
  background: #85ce61;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
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
  margin: 8px 0;
  color: #555;
  font-size: 14px;
}

.desc {
  min-height: 40px;
}

.btn-row {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn-row button {
  flex: 1;
}
</style>