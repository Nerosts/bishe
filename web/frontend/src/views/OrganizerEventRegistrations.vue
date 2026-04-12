<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动报名名单</h1>
        <p class="sub">查看当前活动的报名记录</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goMyEvents">返回我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="event-info-card" v-if="eventInfo">
      <h2>{{ eventInfo.event_title }}</h2>
      <p><strong>活动ID：</strong>{{ eventInfo.event_id }}</p>
      <p><strong>类别：</strong>{{ eventInfo.event_category }}</p>
      <p><strong>地点：</strong>{{ eventInfo.event_location }}</p>
      <p><strong>开始时间：</strong>{{ eventInfo.event_start_time }}</p>
    </div>

    <div v-if="registrations.length === 0" class="empty-box">
      当前活动还没有报名记录
    </div>

    <div v-else class="table-box">
      <table>
        <thead>
          <tr>
            <th>报名记录ID</th>
            <th>用户ID</th>
            <th>用户名</th>
            <th>活动ID</th>
            <th>报名状态</th>
            <th>报名时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in registrations" :key="item.registration_id">
            <td>{{ item.registration_id }}</td>
            <td>{{ item.user_id }}</td>
            <td>{{ item.username }}</td>
            <td>{{ item.event_id }}</td>
            <td>
              <span
                :class="{
                  pending: item.status === '待审核',
                  approved: item.status === '已通过',
                  rejected: item.status === '已拒绝'
                }"
              >
                {{ item.status }}
              </span>
            </td>
            <td>{{ item.signup_time }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const eventInfo = ref(null)
const registrations = ref([])

const loadRegistrations = async () => {
  const organizerId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')
  const eventId = route.params.id

  if (!organizerId || role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`http://127.0.0.1:5000/organizer/${organizerId}/events/${eventId}/registrations`)
    eventInfo.value = {
      event_id: res.data.event_id,
      event_title: res.data.event_title,
      event_category: res.data.event_category,
      event_location: res.data.event_location,
      event_start_time: res.data.event_start_time
    }
    registrations.value = res.data.registrations
  } catch (error) {
    console.error('获取活动报名名单失败', error)
  }
}

const goMyEvents = () => {
  router.push('/organizer/my-events')
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

.event-info-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.event-info-card h2 {
  margin-top: 0;
  color: #333;
}

.event-info-card p {
  margin: 8px 0;
  color: #555;
}

.empty-box {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: #666;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.table-box {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  text-align: left;
}

th {
  background: #f8f9fb;
  color: #333;
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