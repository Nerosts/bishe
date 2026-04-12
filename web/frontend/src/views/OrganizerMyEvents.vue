<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>我的活动</h1>
        <p class="sub-title">这里显示当前组织者发布的活动</p>
      </div>

      <div class="top-buttons">
        <button class="orange-btn" @click="goPublish">继续发布</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="card-list">
      <div class="event-card" v-for="item in eventList" :key="item.id">
        <h2>{{ item.title }}</h2>
        <p>活动ID：{{ item.id }}</p>
        <p>类别：{{ item.category }}</p>
        <p>地点：{{ item.location }}</p>
        <p>开始时间：{{ item.start_time }}</p>
        <p>人数上限：{{ item.max_participants }}</p>
        <p>已通过人数：{{ item.approved_count }}</p>
        <p>状态：{{ item.status }}</p>
        <p>描述：{{ item.description }}</p>
        <p>发布时间：{{ item.created_at }}</p>

        <div class="btn-group">
          <button class="green-btn" @click="goRegistrations(item.id)">查看报名名单</button>
          <button class="blue-btn" @click="goEdit(item.id)">编辑活动</button>
          <button class="purple-btn" @click="goQrcode(item.id)">查看签到码</button>
          <button class="cyan-btn" @click="goCheckinStats(item.id)">查看签到情况</button>
          <button class="red-btn" @click="deleteEvent(item.id)">删除活动</button>
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
const eventList = ref([])
const message = ref('')

const loadMyEvents = async () => {
  const organizerId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')

  if (!organizerId || role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/organizer/${organizerId}/events`)
    eventList.value = res.data
  } catch (error) {
    message.value = '获取我的活动失败'
  }
}

const goPublish = () => {
  router.push('/organizer/publish')
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

const goRegistrations = (eventId) => {
  router.push(`/organizer/events/${eventId}/registrations`)
}

const goEdit = (eventId) => {
  router.push(`/organizer/events/${eventId}/edit`)
}

const goQrcode = (eventId) => {
  router.push(`/organizer/events/${eventId}/qrcode`)
}

const goCheckinStats = (eventId) => {
  router.push(`/organizer/events/${eventId}/checkin-stats`)
}

const deleteEvent = async (eventId) => {
  const organizerId = localStorage.getItem('user_id')
  const ok = window.confirm('确定要删除这个活动吗？')
  if (!ok) return

  try {
    const res = await axios.delete(`${API_BASE_URL}/organizer/${organizerId}/events/${eventId}`)
    message.value = res.data.message
    await loadMyEvents()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '删除活动失败'
    }
  }
}

onMounted(() => {
  loadMyEvents()
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

.event-card {
  width: 370px;
  background: white;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.event-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
}

.event-card p {
  margin: 8px 0;
  color: #555;
}

.btn-group {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
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

.orange-btn {
  background: #e6a23c;
}
.orange-btn:hover {
  background: #ebb563;
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

.green-btn {
  background: #14b8a6;
}
.green-btn:hover {
  background: #2dd4bf;
}

.blue-btn {
  background: #409eff;
}
.blue-btn:hover {
  background: #66b1ff;
}

.purple-btn {
  background: #8b5cf6;
}
.purple-btn:hover {
  background: #a78bfa;
}

.cyan-btn {
  background: #06b6d4;
}
.cyan-btn:hover {
  background: #22d3ee;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>