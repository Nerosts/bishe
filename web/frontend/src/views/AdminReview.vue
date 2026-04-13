<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>报名审核管理</h1>
        <p class="sub-title">管理员可查看待审核记录，并进行通过或拒绝操作</p>
      </div>

      <div class="top-buttons">
        <button class="purple-btn" @click="showPending">待审核</button>
        <button class="teal-btn" @click="showHistory">审核历史</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="filter-box" v-if="currentView === 'history'">
      <div class="filter-item">
        <label>历史筛选</label>
        <select v-model="historyStatus" @change="loadRegistrations">
          <option value="">全部历史</option>
          <option value="已通过">仅看已通过</option>
          <option value="已拒绝">仅看已拒绝</option>
        </select>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="section-title">
      {{ currentView === 'pending' ? '待审核列表' : '审核历史列表' }}
    </div>

    <div class="card-list" v-if="registrationList.length > 0">
      <div class="review-card" v-for="item in registrationList" :key="item.registration_id">
        <div class="card-header">
          <h2>{{ item.event_title }}</h2>
          <span class="status-badge" :class="getStatusBadgeClass(item.status)">
            {{ item.status }}
          </span>
        </div>

        <div class="info-grid">
          <p><span class="label">用户名：</span>{{ item.username }}</p>
          <p><span class="label">用户ID：</span>{{ item.user_id }}</p>
          <p><span class="label">活动ID：</span>{{ item.event_id }}</p>
          <p><span class="label">报名记录ID：</span>{{ item.registration_id }}</p>
          <p><span class="label">报名时间：</span>{{ item.register_time }}</p>
        </div>

        <div class="btn-group" v-if="currentView === 'pending'">
          <button class="approve-btn" @click="approveRegistration(item.registration_id)">
            审核通过
          </button>
          <button class="reject-btn" @click="rejectRegistration(item.registration_id)">
            审核拒绝
          </button>
        </div>
      </div>
    </div>

    <div class="empty-box" v-else>
      {{ currentView === 'pending' ? '当前没有待审核记录' : '当前没有审核历史记录' }}
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
const currentView = ref('pending')
const historyStatus = ref('')

const currentUserId = localStorage.getItem('user_id')

const loadRegistrations = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/admin/review`, {
      params: {
        user_id: currentUserId,
        view: currentView.value,
        status: historyStatus.value
      }
    })
    registrationList.value = res.data || []
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取审核记录失败'
    }
  }
}

const approveRegistration = async (registrationId) => {
  try {
    const res = await axios.post(`${API_BASE_URL}/admin/review/${registrationId}/approve`, {
      user_id: currentUserId
    })
    message.value = res.data.message
    await loadRegistrations()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '审核通过失败'
    }
  }
}

const rejectRegistration = async (registrationId) => {
  try {
    const res = await axios.post(`${API_BASE_URL}/admin/review/${registrationId}/reject`, {
      user_id: currentUserId
    })
    message.value = res.data.message
    await loadRegistrations()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '审核拒绝失败'
    }
  }
}

const showPending = async () => {
  currentView.value = 'pending'
  historyStatus.value = ''
  await loadRegistrations()
}

const showHistory = async () => {
  currentView.value = 'history'
  await loadRegistrations()
}

const getStatusBadgeClass = (status) => {
  if (status === '待审核') return 'waiting-badge'
  if (status === '已通过') return 'approved-badge'
  if (status === '已拒绝') return 'rejected-badge'
  return ''
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
  gap: 20px;
}

h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.sub-title {
  margin-top: 8px;
  color: #666;
  font-size: 15px;
}

.top-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-box {
  background: white;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

.filter-item select {
  width: 220px;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
}

.section-title {
  margin: 18px 0 14px;
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.message-box {
  margin-bottom: 18px;
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 22px;
}

.review-card {
  background: white;
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.review-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.10);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 22px;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  color: white;
  white-space: nowrap;
}

.waiting-badge {
  background: #e6a23c;
}

.approved-badge {
  background: #67c23a;
}

.rejected-badge {
  background: #f56c6c;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-bottom: 18px;
}

.info-grid p {
  margin: 0;
  color: #555;
  line-height: 1.6;
  word-break: break-all;
}

.label {
  color: #333;
  font-weight: 700;
}

.btn-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

button {
  border: none;
  border-radius: 10px;
  padding: 11px 18px;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.approve-btn {
  background: #67c23a;
}

.approve-btn:hover {
  background: #85ce61;
}

.reject-btn {
  background: #f56c6c;
}

.reject-btn:hover {
  background: #f78989;
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

.purple-btn {
  background: #8b5cf6;
}

.purple-btn:hover {
  background: #a78bfa;
}

.teal-btn {
  background: #14b8a6;
}

.teal-btn:hover {
  background: #2dd4bf;
}

.empty-box {
  background: white;
  border-radius: 16px;
  padding: 28px;
  color: #999;
  text-align: center;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}
</style>