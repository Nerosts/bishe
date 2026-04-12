<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>签到记录查询</h1>
        <p class="sub-title">管理员可查看全部签到记录，并按用户名或活动筛选</p>
      </div>

      <div class="top-buttons">
        <button class="green-btn" @click="exportExcel">导出Excel</button>
        <button class="purple-btn" @click="goStats">返回统计分析</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-item">
        <label>用户名筛选</label>
        <input v-model="username" type="text" placeholder="请输入用户名关键字" />
      </div>

      <div class="filter-item">
        <label>活动筛选</label>
        <select v-model="eventId">
          <option value="">全部活动</option>
          <option v-for="item in eventOptions" :key="item.id" :value="item.id">
            {{ item.id }} - {{ item.title }}
          </option>
        </select>
      </div>

      <div class="filter-buttons">
        <button class="blue-btn" @click="loadCheckins">查询</button>
        <button class="gray-btn" @click="resetFilters">重置</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="table-card">
      <table v-if="checkinList.length > 0">
        <thead>
          <tr>
            <th>签到ID</th>
            <th>用户ID</th>
            <th>用户名</th>
            <th>活动ID</th>
            <th>活动标题</th>
            <th>签到时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in checkinList" :key="item.checkin_id">
            <td>{{ item.checkin_id }}</td>
            <td>{{ item.user_id }}</td>
            <td>{{ item.username }}</td>
            <td>{{ item.event_id }}</td>
            <td>{{ item.event_title }}</td>
            <td>{{ item.checkin_time }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-box">
        暂无符合条件的签到记录
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

const username = ref('')
const eventId = ref('')
const message = ref('')
const checkinList = ref([])
const eventOptions = ref([])

const loadCheckins = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/admin/checkins`, {
      params: {
        username: username.value,
        event_id: eventId.value
      }
    })

    checkinList.value = res.data.checkins || []
    eventOptions.value = res.data.events || []
    message.value = ''
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取签到记录失败'
    }
  }
}

const resetFilters = async () => {
  username.value = ''
  eventId.value = ''
  await loadCheckins()
}

const exportExcel = () => {
  const query = new URLSearchParams({
    username: username.value,
    event_id: eventId.value
  }).toString()

  window.open(`${API_BASE_URL}/admin/checkins/export?${query}`, '_blank')
}

const goStats = () => {
  router.push('/admin/stats')
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

onMounted(async () => {
  const role = localStorage.getItem('role')
  if (role !== 'admin') {
    router.push('/login')
    return
  }

  await loadCheckins()
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

.filter-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  color: #333;
  font-weight: bold;
}

.filter-item input,
.filter-item select {
  width: 240px;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.filter-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f5f7fa;
}

th,
td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
  color: #333;
}

.empty-box {
  color: #999;
  padding: 20px 0;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  color: white;
  cursor: pointer;
}

.blue-btn {
  background: #409eff;
}
.blue-btn:hover {
  background: #66b1ff;
}

.green-btn {
  background: #67c23a;
}
.green-btn:hover {
  background: #85ce61;
}

.purple-btn {
  background: #8b5cf6;
}
.purple-btn:hover {
  background: #a78bfa;
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