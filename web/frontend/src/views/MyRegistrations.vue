<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>我的报名</h1>
        <p class="sub">查看当前账号的活动报名记录</p>
      </div>

      <div class="top-buttons">
        <button class="blue-btn" @click="goEvents">返回活动列表</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="message-box" v-if="message">
      {{ message }}
    </div>

    <div v-if="registrations.length === 0" class="empty-box">
      当前没有报名记录
    </div>

    <div v-else class="registration-grid">
      <div class="registration-card" v-for="item in registrations" :key="item.registration_id">
        <h2>{{ item.event_title }}</h2>
        <p><strong>报名记录ID：</strong>{{ item.registration_id }}</p>
        <p><strong>活动类别：</strong>{{ item.event_category }}</p>
        <p><strong>活动地点：</strong>{{ item.event_location }}</p>
        <p><strong>活动开始时间：</strong>{{ item.event_start_time }}</p>
        <p>
          <strong>报名状态：</strong>
          <span
            :class="{
              pending: item.status === '待审核',
              approved: item.status === '已通过',
              rejected: item.status === '已拒绝'
            }"
          >
            {{ item.status }}
          </span>
        </p>
        <p><strong>报名时间：</strong>{{ item.signup_time }}</p>

        <div class="btn-row">
          <button class="red-btn" @click="cancelRegistration(item.registration_id)">
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

const router = useRouter()
const registrations = ref([])
const message = ref('')

const loadRegistrations = async () => {
  const userId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')

  if (!userId || role !== 'student') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`http://127.0.0.1:5000/users/${userId}/registrations`)
    registrations.value = res.data
  } catch (error) {
    console.error('获取我的报名失败', error)
    message.value = '获取报名记录失败'
  }
}

const cancelRegistration = async (registrationId) => {
  const userId = localStorage.getItem('user_id')

  try {
    const res = await axios.delete(`http://127.0.0.1:5000/registrations/${registrationId}`, {
      data: {
        user_id: userId
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

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 18px;
}

.empty-box {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: #666;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.registration-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.registration-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.registration-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
}

.registration-card p {
  margin: 8px 0;
  color: #555;
}

.btn-row {
  margin-top: 18px;
}

.pending {
  color: #e6a23c;
  font-weight: bold;
}

.approved {
  color: #67c23a;
  font-weight: bold;
}

.rejected {
  color: #f56c6c;
  font-weight: bold;
}
</style>