<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动签到情况</h1>
        <p class="sub-title">组织者可查看本活动的签到统计与未签到名单</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goBack">返回我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div v-if="stats" class="summary-card">
      <h2>{{ stats.event_title }}</h2>
      <p>活动ID：{{ stats.event_id }}</p>
      <p>类别：{{ stats.event_category }}</p>
      <p>地点：{{ stats.event_location }}</p>
      <p>开始时间：{{ stats.event_start_time }}</p>
      <p>已通过人数：{{ stats.approved_count }}</p>
      <p class="checked">已签到人数：{{ stats.checked_count }}</p>
      <p class="unchecked">未签到人数：{{ stats.unchecked_count }}</p>
    </div>

    <div class="two-column" v-if="stats">
      <div class="list-card">
        <h3>已签到名单</h3>
        <div v-if="stats.checked_list.length === 0" class="empty-text">
          暂无已签到学生
        </div>

        <table v-else>
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>报名时间</th>
              <th>签到时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in stats.checked_list" :key="`checked-${item.user_id}`">
              <td>{{ item.user_id }}</td>
              <td>{{ item.username }}</td>
              <td>{{ item.signup_time }}</td>
              <td>{{ item.checkin_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="list-card">
        <h3>未签到名单</h3>
        <div v-if="stats.unchecked_list.length === 0" class="empty-text">
          暂无未签到学生
        </div>

        <table v-else>
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>报名时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in stats.unchecked_list" :key="`unchecked-${item.user_id}`">
              <td>{{ item.user_id }}</td>
              <td>{{ item.username }}</td>
              <td>{{ item.signup_time }}</td>
            </tr>
          </tbody>
        </table>
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
const stats = ref(null)
const message = ref('')

const loadStats = async () => {
  const organizerId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')
  const eventId = route.params.id

  if (!organizerId || role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(
      `${API_BASE_URL}/organizer/${organizerId}/events/${eventId}/checkin-stats`
    )
    stats.value = res.data
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取签到情况失败'
    }
  }
}

const goBack = () => {
  router.push('/organizer/my-events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  loadStats()
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

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-card {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.summary-card h2 {
  margin-top: 0;
  color: #333;
}

.summary-card p {
  margin: 10px 0;
  color: #555;
}

.checked {
  color: #16a34a !important;
  font-weight: bold;
}

.unchecked {
  color: #f59e0b !important;
  font-weight: bold;
}

.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.list-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  overflow-x: auto;
}

.list-card h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
}

.empty-text {
  color: #909399;
  padding: 16px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 420px;
}

th, td {
  border-bottom: 1px solid #ebeef5;
  padding: 10px 8px;
  text-align: left;
  color: #555;
  font-size: 14px;
}

th {
  color: #333;
  background: #f8fafc;
}
</style>